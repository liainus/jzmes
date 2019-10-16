import re
from typing import Optional, Any
from collections import Counter
import time
import xlrd
import xlwt
from flask import Blueprint, render_template, send_from_directory
from openpyxl.compat import file
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy import create_engine
import Model.Global
from Model.core import ProcessUnit, Equipment, SysLog, MaterialBOM, ProductRule, Material, ZYPlan, PlanManager
from flask import render_template, request, make_response
from tools.MESLogger import MESLogger
from Model.BSFramwork import AlchemyEncoder
import json
import socket
import datetime
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
import re
from Model.system import Role, Organization, User, Menu, Role_Menu, BatchMaterielBalance, OperationManual, NewReadyWork, \
    EquipmentWork, EletronicBatchDataStore, SpareStock, EquipmentMaintenanceKnowledge, EquipmentReportingRecord, \
    EquipmentMaintain, \
    SchedulePlan, SparePartInStockManagement, SparePartStock, Area, Instruments, MaintenanceStatus, MaintenanceCycle, \
    EquipmentRunRecord, \
    EquipmentRunPUID, EquipmentMaintenanceStore, SpareTypeStore, ElectronicBatch, EquipmentStatusCount, Shifts, \
    EquipmentTimeStatisticTree, SystemEQPCode, EquipmentManagementManua, EquipmentMaintenanceStandard, product_info, \
    product_plan, product_infoERP, WMSDetail, PurchasingOrder
from sqlalchemy import create_engine, Column, ForeignKey, Table, Integer, String, and_, or_, desc,extract
from io import StringIO
import calendar
from Model.system import CenterCost, ERPproductcode_prname, SchedulingStock, ProcessQualityPDF, ProcessQuality, ImpowerInterface, EmpowerPeakItem,\
    EmpowerContent, EmpowerContentJournal, ZYPlanWMS, WMStatusLoad, PartiallyProducts, StapleProducts
from tools.common import logger,insertSyslog,insert,delete,update,select
import os
import openpyxl
from spyne import Application
from spyne import rpc
from spyne import ServiceBase
from spyne import Iterable, Integer, Unicode, Array, util, AnyDict, ModelBase
from spyne.protocol.soap import Soap11
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import logging
import suds
from suds.client import Client
from spyne import Application
from suds.xsd.doctor import ImportDoctor, Import
from operator import itemgetter, attrgetter
import random


engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

engine_ERP = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING_ERP, deprecate_large_types=True)
Session_ERP = sessionmaker(bind=engine_ERP)
ERP_session = Session_ERP()

Process = Blueprint('Process', __name__)

@Process.route('/ProcessqualityRawmaterial')
def ProcessqualityRawmaterial():
    '''
    原料确认流程
    :return:
    '''
    return render_template('ProcessqualityRawmaterial.html')

@Process.route('/ProcessqualityInprocess')
def ProcessqualityInprocess():
    '''
    过程中确认流程
    :return:
    '''
    return render_template('ProcessqualityInprocess.html')

@Process.route('/ProcessqualityFinishedProduct')
def ProcessqualityFinishedProduct():
    '''
    成品确认流程
    :return:
    '''
    return render_template('ProcessqualityFinishedProduct.html')

@Process.route('/process_quality/ProcessqualityConfirm', methods=['GET', 'POST'])
def ProcessqualityConfirm():
    '''
    工艺质量操作人确认流程
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        try:
            data_dict = {
                         "ID":data['ID'],
                         "content": data['content'],
                         "OperationPeople": current_user.Name,
                         "OperationDate":datetime.datetime.now()}
            return update(ProcessQuality, data_dict)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由：/process_quality/ProcessqualityConfirm，工艺质量操作人确认流程Error：" + str(e), current_user.Name)


@Process.route('/process_quality/ProcessqualityCheck', methods=['GET', 'POST'])
def ProcessqualityCheck():
    '''
    工艺质量复核人确认流程
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
            data_dict = {
                         "ID": jsonnumber[0],
                         "CheckedPeople": current_user.Name,
                         "OperationDate":datetime.datetime.now()}
            return update(ProcessQuality, data_dict)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由：/process_quality/ProcessqualityCheck，工艺质量复核人确认流程Error：" + str(e), current_user.Name)

@Process.route('/process_quality/ProcessqualityReview', methods=['GET', 'POST'])
def ProcessqualityReview():
    '''
    工艺质量审核人确认流程
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
            data_dict = {
                "ID": jsonnumber[0],
                "Reviewer": current_user.Name,
                "OperationDate": datetime.datetime.now()}
            return update(ProcessQuality, data_dict)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由：/process_quality/ProcessqualityReview，工艺质量审核人确认流程Error：" + str(e), current_user.Name)

# post方法：上传文件的
@Process.route('/process_quality/ProcessQualityPDFUpload', methods=['post'])
def ProcessQualityPDFUpload():
    fname = request.files.get('file')  #获取上传的文件
    print(request.values)
    if fname:
        BatchID = request.values.get('BatchID')
        new_fname = r'static/generic/web/' +BatchID+"-"+ fname.filename
        fname.save(new_fname)  #保存文件到指定路径
        data_dict = {"Name": BatchID+"-"+fname.filename,
                     "Path": new_fname,
                     "Author": current_user.Name,
                     "UploadTime": datetime.datetime.now()}
        message = insert(ProcessQualityPDF, data_dict)
        return 'OK'
    else:
        return '{"msg": "请上传文件！"}'
# get方法：查询当前路径下的所有文件
@Process.route('/process_quality/ProcessQualityPDFSearch', methods=['get'])
def ProcessQualityPDFSearch():
    data = request.values
    try:
        json_str = json.dumps(data.to_dict())
        if len(json_str) > 10:
            pages = int(data['page'])
            rowsnumber = int(data['rows'])
            inipage = (pages - 1) * rowsnumber + 0
            endpage = (pages - 1) * rowsnumber + rowsnumber
            filename = data.get('Name')
            if not filename:
                total = db_session.query(ProcessQualityPDF).count()
                oclass = db_session.query(ProcessQualityPDF).all()[inipage:endpage]
            else:
                total = db_session.query(ProcessQualityPDF).filter(ProcessQualityPDF.Name.like("%" + filename + "%")).count()
                oclass = db_session.query(ProcessQualityPDF).filter(ProcessQualityPDF.Name.like("%" + filename + "%")).all()[
                              inipage:endpage]
            jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
            jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
            return jsonoclass
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "路由：/process_quality/ProcessQualityPDFSearch，PDF获取Error：" + str(e), current_user.Name)
dirpath = os.path.join(str(Process.root_path)[0:-15],'static\generic\web')
#get方法：指定目录下载文件
@Process.route('/process_quality/ProcessQualityPDFDownload', methods=['get'])
def ProcessQualityPDFDownload():
    fname = request.values.get('Name', '')
    if os.path.isfile(os.path.join(dirpath, fname)):
        response = make_response(send_from_directory(dirpath, fname, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(fname.encode().decode('latin-1'))
        return response
    else:
        return '{"msg":"参数不正确"}'
# #文件预览
# basedir = os.path.abspath(os.path.dirname(__file__))
# @Process.route('/process_quality/preview', methods=['get'])
# def preview():
#     print(dirpath)
#     filename = request.values.get('Name', '')
#     file_dir = os.path.join(dirpath, filename)
#     if request.method == 'GET':
#         if filename is None:
#             pass
#         else:
#             # response = make_response(send_from_directory(dirpath, filename, as_attachment=True))
#             # response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
#             image_data = open(file_dir, "rb").read()
#             response = make_response(image_data)
#             response.headers["Content-Disposition"] = "attachment; filename={}".format(
#                 filename.encode().decode('utf-8'))
#             response.headers['Content-Type'] = 'image/png'
#             return response
#         return render_template('viewer.html')
#     else:
#         pass

@Process.route('/process_quality/ProcessQualityPDFDelete', methods=['GET', 'POST'])
def ProcessQualityPDFDelete():
    '''
    PDF删除
    :return:
    '''
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    # for subkey in list(key):
                    id = int(key)
                    try:
                        oclass = db_session.query(ProcessQualityPDF).filter(
                            ProcessQualityPDF.ID == id).first()
                        delete(ProcessQualityPDF, data)
                        os.remove(oclass.Path)
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由：/process_quality/ProcessQualityPDFDelete，PDF删除Error：" + str(e), current_user.Name)

@Process.route('/process_quality/ProcessQualityUpdate', methods=['POST', 'GET'])
def ProcessQualityUpdate():
    if request.method == 'POST':
        data = request.values
        return update(ProcessQuality, data)

@Process.route('/process_quality/ProcessQualityDelete', methods=['POST', 'GET'])
def ProcessQualityDelete():
    if request.method == 'POST':
        data = request.values
        return delete(ProcessQuality, data)

@Process.route('/process_quality/ProcessQualityCreate', methods=['POST', 'GET'])
def ProcessQualityCreate():
    if request.method == 'POST':
        data = request.values
        return insert(ProcessQuality, data)

@Process.route('/process_quality/ProcessQualitySearch', methods=['POST', 'GET'])
def ProcessQualitySearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                BatchID = data.get('BatchID')
                if not BatchID:
                    Description = data.get('Description')
                    total = db_session.query(ProcessQuality).filter(ProcessQuality.Description == Description).count()
                    oclass = db_session.query(ProcessQuality).filter(ProcessQuality.Description == Description).all()[inipage:endpage]
                else:
                    total = db_session.query(ProcessQuality).filter(
                        ProcessQuality.BatchID == BatchID).count()
                    oclass = db_session.query(ProcessQuality).filter(
                        ProcessQuality.BatchID == BatchID).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "工艺质量确认流程表查询报错Error：" + str(e), current_user.Name)
            return json.dumps("工艺质量确认流程表查询报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

@Process.route('/refractometerHistoryData')
def CrefractometerHistoryData():
    '''
    折光仪历史数据
    :return:
    '''
    return render_template('refractometerHistoryData.html')

@Process.route('/refractometerRealTimeData')
def refractometerRealTimeData():
    '''
    折光仪实时数据
    :return:
    '''
    return render_template('refractometerRealTimeData.html')
class ADS_test(ServiceBase):
    logging.basicConfig(level=logging.DEBUG)
    @rpc(Unicode, Integer, _returns=Unicode())
    def ADS_Order_Download(self, name, times):
        dic = []
        for i in range(0, 3):
            dic.append(appendStr(i))
        return json.dumps(dic)
def appendStr(i):
    dir = {}
    dir['btype'] = "aa"
    dir['mid'] = "aa"
    dir['Num'] = "12"
    dir['BatchNo'] = "aa"
    dir['BillNo'] = "aa"
    dir['StoreDef_ID'] = "aa"
    return dir
class WMS_Interface(ServiceBase):
    '''
    接口服务端
    '''
    logging.basicConfig(level=logging.DEBUG)
    @rpc(Unicode, Unicode, _returns=Unicode())
    def WMS_Order_Download(self, name, times):
        '''
        采购订单同步给WMS
        '''
        dic = []
        for i in range(0, 3):
            dic.append(appendStr(i))
        return json.dumps(dic)

    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(self, name, times):
        for i in range(times):
            yield u'Hello, %s' % name

    @rpc(Unicode, Unicode, _returns=Unicode())
    def WMS_OrderStatus(self, name, json_data):
        '''
        单据状态变更
        '''
        try:
            dic = []
            jso = json.loads(json_data)
            for i in jso:
                BillNo = i.get("BillNo")
                status = i.get("status")
                if BillNo != None:
                    BatchID = BillNo[0:-1]
                    BrandID = BillNo[-1:]
                    zy = db_session.query(ZYPlanWMS).filter(ZYPlanWMS.BatchID == BatchID ,ZYPlanWMS.BrandID == BrandID).first()
                    if zy:
                        zy.ExcuteStatus = status
                        db_session.commit()
                    else:
                        return json.dumps("没有此单据号！")
                else:
                    continue
            return json.dumps("SUCCESS")
        except Exception as e:
            print("WMS调用WMS_OrderStatus接口报错！")
            return json.dumps(e)

    @rpc(Unicode, Unicode, _returns=Unicode())
    def Sync_StapleProducts(self, name, json_data):
        '''
        WMS同步原料检验单
        '''
        try:
            dic = []
            jso = json.loads(json_data)
            for i in jso:
                sta = StapleProducts()
                sta.BillNo = i.get("BillNo")
                sta.BatchNo = i.get("BatchNo")
                sta.StoreDef_ID = i.get("StoreDef_ID")
                sta.btype = i.get("btype")
                sta.mid = i.get("mid")
                sta.Num = i.get("Num")
                sta.FinishNum = i.get("FinishNum")
                sta.IsRelevance = "0"
                sta.OperationDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db_session.add(sta)
                db_session.commit()
            return json.dumps("SUCCESS")
        except Exception as e:
            print("WMS调用WMS_OrderStatus接口报错！")
            return json.dumps(e)

    @rpc(Unicode, Unicode, _returns=Unicode())
    def WMS_ZYPlanStatus(self, name, json_data):
        '''
        备料段计划开始结束状态WMS回传
        '''
        try:
            dic = []
            jso = json.loads(json_data)
            for i in jso:
                BatchID = i.get("BatchID")
                BrandName = i.get("BrandName")
                status = i.get("status")
                if BatchID != None:
                    zy = db_session.query(ZYPlan).filter(ZYPlan.BatchID == BatchID,
                                                         ZYPlan.BrandName == BrandName,ZYPlan.PUID == 1).first()
                    if zy != None:
                        if status == "1":
                            zy.ActBeginTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        elif status == "3":
                            zy.ActEndTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    db_session.commit()
                else:
                    continue
            return json.dumps("SUCCESS")
        except Exception as e:
            print("WMS调用WMS_ZYPlanStatus接口报错！")
            return json.dumps(e)
@Process.route('/WMS_SendPlan', methods=['GET', 'POST'])
def WMS_SendPlan():
    '''发送备料计划到WMS'''
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        dic = []
                        oclass = db_session.query(ZYPlanWMS).filter(ZYPlanWMS.ID == id).first()
                        # IsSend = str(int(oclass.IsSend)+1)
                        if oclass.IsSend == "10":
                            return json.dumps("数据已发送过WMS！")
                        oclss = db_session.query(MaterialBOM).filter(MaterialBOM.ProductRuleID == oclass.BrandID).all()
                        for ocl in oclss:
                            StoreDef_ID = "1"
                            if ocl.MATID in ("100005", "100009", "2120"):
                                StoreDef_ID = "2"
                            num = str(float(ocl.BatchTotalWeight)*float(ocl.BatchPercentage))
                            dic.append({"BillNo":str(oclass.BatchID)+str(oclass.BrandID),"BatchNo":str(oclass.BatchID),"btype":"203","StoreDef_ID":StoreDef_ID,"mid":ocl.MATID,"num":num})
                        jsondic = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
                        client = Client(Model.Global.WMSurl)
                        ret = client.service.Mes_Interface("billload", jsondic)
                        if ret[0] != "SUCCESS":
                            return json.dumps("调用WMS_SendPlan接口报错！"+ret[1])
                        oclass.IsSend = "10"
                        db_session.commit()
                        return 'OK'
                    except Exception as ee:
                        return json.dumps("调用WMS_SendPlan接口报错！")
        except Exception as e:
            print("调用WMS_SendPlan接口报错！")
            return json.dumps("调用WMS_SendPlan接口报错！")
@Process.route('/WMS_SendSAPMatil', methods=['GET', 'POST'])
def WMS_SendSAPMatil():
    '''发送SAP物料信息到WMS'''
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
            dic = []
            for key in jsonnumber:
                id = int(key)
                oclass = db_session.query(product_infoERP).filter(product_infoERP.ID == id).first()
                dic.append(oclass)
            jsondic = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            client = Client(Model.Global.WMSurl)
            ret = client.service.Mes_Interface("MatDetLoad", jsondic)
            if ret["Mes_InterfaceResult"] == "SUCCESS":
                return 'OK'
            else:
                return json.dumps(ret["ErrData"])
        except Exception as e:
            print("调用WMS_SendPlan接口报错！")
            return json.dumps("调用WMS_SendPlan接口报错！")
@Process.route('/WMS_ReceiveDetail', methods=['GET', 'POST'])
def WMS_ReceiveDetail():
    '''获取备料计划WMS的流水'''
    if request.method == 'GET':
        data = request.values
        try:
            dic = []
            ID = data.get("ID")
            zyw = db_session.query(ZYPlanWMS).filter(ZYPlanWMS.ID == ID).first()
            dic.append({"BillNo":zyw.BatchID+zyw.BrandID+zyw.IsSend})
            jsondic = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            client = Client(Model.Global.WMSurl)
            re = client.service.Mes_Interface("WorkFlowLoad", jsondic)
            if re[0] == 'SUCCESS':
                jsondata = json.loads(re["json_data"])
                return '{"total"' + ":" + str(len(jsondata)) + ',"rows"' + ":\n" + json.dumps(jsondata,
                                                                                              cls=AlchemyEncoder,
                                                                                              ensure_ascii=False) + "}"
            else:
                return json.dumps(re[1])
        except Exception as e:
            print("调用WMS_SendPlan接口报错！")
            return json.dumps("调用WMS_SendPlan接口报错！")

@Process.route('/WMS_StockInfo', methods=['GET', 'POST'])
def WMS_StockInfo():
    '''获取WMS库存信息'''
    if request.method == 'GET':
        data = request.values
        try:
            ic = []
            pages = int(data.get("offset"))  # 页数
            rowsnumber = int(data.get("limit"))  # 行数
            inipage = pages * rowsnumber + 0  # 起始页
            endpage = pages * rowsnumber + rowsnumber  # 截止页
            client = Client(Model.Global.WMSurl)
            re = client.service.Mes_Interface("StoreLoad")
            if re[0] == "SUCCESS":
                jsondata = json.loads(re[2])
                for i in jsondata:
                    product_code = i.get("MID")
                    num = i.get("num")
                    oclass = db_session.query(SchedulingStock).filter(
                        SchedulingStock.product_code == product_code).first()
                    if oclass != None:
                        oclass.StockHouse = num
                        db_session.commit()
            else:
                return json.dumps(re[1])
            count = db_session.query(SchedulingStock).count()
            oclass = db_session.query(SchedulingStock).all()[inipage:endpage]
            jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
            return '{"total"' + ":" + str(count) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print("调用WMS_StockInfo接口报错！")
            return json.dumps("调用WMS_StockInfo接口报错！")

@Process.route('/MStatusLoad', methods=['GET', 'POST'])
def MStatusLoad():
    '''检验单状态同步给WMS'''
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        dic = []
                        oclass = db_session.query(WMStatusLoad).filter(WMStatusLoad.ID == id).first()
                        client = Client(Model.Global.WMSurl)
                        ret = client.service.Mes_Interface("MStatusLoad",json.dumps(dic))
                        if ret[0] == "SUCCESS":
                            return 'OK'
                        else:
                            return json.dumps(ret[1])
                    except Exception as ee:
                        return json.dumps("调用MStatusLoad接口报错！")
        except Exception as e:
            print("调用MStatusLoad接口报错！")
            return json.dumps("调用MStatusLoad接口报错！")


class SAP_Interface(ServiceBase):
    logging.basicConfig(level=logging.DEBUG)
    @rpc(Unicode, Unicode, _returns=Unicode())
    def SAP_Order_Download(self, name, json_data):
        '''
        SAP同步采购订单
        :param data:
        :return:
        '''
        try:
            dic = []
            dict_data = json.loads(json_data)
            for oc in dict_data:
                wms = db_session.query(PurchasingOrder).filter(PurchasingOrder.BillNo == oc.get("billNo"), PurchasingOrder.mid == oc.get("mid")).first()
                if wms != None:
                    continue
                w = PurchasingOrder()
                w.BillNo = oc.get("billNo")
                w.mid = oc.get("mid")
                w.btype = oc.get("bType")
                w.Num = oc.get("num")
                w.StoreDef_id = oc.get("storeDef_id")
                w.BatchNo = oc.get("batchNo")
                db_session.add(w)
                db_session.commit()
            return json.dumps('SUCCESS')
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SAP_Order_Download报错：" + str(e), current_user.Name)
            return json.dumps(e)

class NH_Interface(ServiceBase):
    logging.basicConfig(level=logging.DEBUG)
    @rpc(Unicode, Unicode, _returns=Unicode())
    def NH_GetOutPut(self, name, json_data):
        '''
        SAP同步采购订单
        :param data:
        :return:
        '''
        dic = []
        dict_data = json.loads(json_data)
        start = dict_data.get("StartTime")
        end = dict_data.get("EndTime")
        ocass = db_session.query(PlanManager).filter(PlanManager.PlanBeginTime.between(start, end), PlanManager.PlanStatus == "70").all()
        for oc in ocass:
            BrandName = oc.BrandName
            if BrandName == "健胃消食片浸膏粉":
                produce = db_session.query(EletronicBatchDataStore.OperationpValue).filter(EletronicBatchDataStore.BatchID == oc.BatchID,
                                                             EletronicBatchDataStore.Content == "count8").first()
            elif BrandName == "肿节风浸膏":
                produce = db_session.query(EletronicBatchDataStore.OperationpValue).filter(
                    EletronicBatchDataStore.BatchID == oc.BatchID,
                    EletronicBatchDataStore.Content == "count2").first()
            if produce != None:
                produce = produce[0]
            else:
                produce = ""
            dic.append({"BatchID":oc.BatchID,"output":produce,"BrandName":BrandName,"PlanBeginTime":ocass.PlanBeginTime})
        return json.dumps(dic)

@Process.route('/impowerSpage')
def impowerSpage():
    return render_template('impowerSpage.html')

@Process.route('/impowerSelect', methods=['POST', 'GET'])
def impowerSelect():
    if request.method == 'GET':
        try:
            imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
            imp.filter.add('http://WebXml.com.cn/')
            doctor = ImportDoctor(imp)
            client = Client(Model.Global.EmpowerURL, doctor=doctor)
            userzj = db_session.query(User).filter(User.Name == "dw5213").first()
            re = client.service.GetAllEmpowerProject(userzj.Name, userzj.Password)
            if re[2] == 'OK':
                ret = re[0]
                # re = r"Training;Training\hsr;Training\wkr;成品组;成品组\2017健胃消食片浸膏粉橙皮苷含量;成品组\2017肿节风浸膏异嗪皮啶含量;成品组\2018-健胃消食片(无糖型)浸膏-橙;成品组\2018-健胃消食片浸膏粉-橙皮苷;成品组\2018-肿节风浸膏-异嗪皮啶;成品组\2019-大黄粉-总蒽醌和游离蒽醌;成品组\2019-健胃消食片(无糖型)浸膏-橙;成品组\2019-健胃消食片浸膏粉-橙皮苷;成品组\2019-痔康片清膏-芦丁;成品组\2019-肿节风浸膏-异嗪皮啶;计算机化系统验证;气相实验;液相实验;原辅组;原辅组\2017陈皮橙皮苷;原辅组\2017陈皮黄曲霉毒素;原辅组\2017回收乙醇异嗪皮啶残留;原辅组\2017乙醇挥发性杂质;原辅组\2017肿节风异嗪皮啶迷迭香酸;原辅组\2018-陈皮-黄曲霉毒素;原辅组\2018-回收乙醇-异嗪皮啶;原辅组\2018-乙醇-挥发性杂质;原辅组\2018-肿节风-异嗪皮啶及迷迭香酸;原辅组\2018陈皮橙皮苷;原辅组\2019-陈皮-橙皮苷;原辅组\2019-陈皮-黄曲霉毒素;原辅组\2019-大黄-总蒽醌和游离蒽醌;原辅组\2019-地榆炭-没食子酸;原辅组\2019-槐花-芦丁;原辅组\2019-黄芩-黄芩苷;原辅组\2019-回收乙醇-异嗪皮啶;原辅组\2019-金银花-绿原酸和木犀草苷;原辅组\2019-乙醇-挥发性杂质;原辅组\2019-肿节风-异嗪皮啶及迷迭香酸;原辅组\2019-豨莶草-奇壬醇;正确4Q验证;智能制造实验;质谱实验;"
                sz = []
                child = []
                i = 0
                orgs = ret.strip().split(";")
                for obj in orgs:
                    if "\\" in obj:
                        ch = obj.split("\\")
                        listi.append({"id": i, "text": ch[1], "children": []})
                    else:
                        listi = []
                        sz.append({"id": i, "text": obj, "children": listi})
                    i = i + 1
                return json.dumps(sz, cls=AlchemyEncoder, ensure_ascii=False)
            else:
                return json.dumps(re[1], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "/impowerSelect报错Error：" + str(e), current_user.Name)
            return json.dumps("impower查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
@Process.route('/impowerSelectData', methods=['POST', 'GET'])
def impowerSelectData():
    if request.method == 'GET':
        data = request.values
        try:
            projectName = data.get("projectName")
            imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
            imp.filter.add('http://WebXml.com.cn/')
            doctor = ImportDoctor(imp)
            client = Client(Model.Global.EmpowerURL, doctor=doctor)  # 创建一个webservice接口对象
            userzj = db_session.query(User).filter(User.Name == "dw5213").first()
            re = client.service.GetEmpowerProjectItem(userzj.Name, userzj.Password, projectName, "*")
            datadir = []
            if re[2] == 'OK':
                orgs = re[0].strip().split("\n")
                a = 0
                for i in orgs:
                    igs = i.split(",")
                    if len(igs) == 9 and a > 0:
                        imp = ImpowerInterface()
                        imp.ID = a
                        imp.SampleName = igs[0]
                        imp.SampleBottle = igs[1]
                        imp.Sampling = igs[2]
                        imp.SampleType = igs[3]
                        imp.ProcessingChannel = igs[4]
                        imp.CollectionDate = igs[5]
                        imp.OperationDate = igs[6]
                        imp.ProcessingMethod = igs[7]
                        imp.ResultID = igs[8]
                        datadir.append(imp)
                        a = a + 1
                    else:
                        a = a + 1
                        continue
                s = sorted(datadir, key=attrgetter('ResultID'))
                newdatadir = sorted(s, key=attrgetter('ResultID'), reverse=True)
                jsonoclass = json.dumps(newdatadir, cls=AlchemyEncoder, ensure_ascii=False)
                return jsonoclass
            else:
                return json.dumps(re[1], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "/impowerSelectData报错Error：" + str(e), current_user.Name)
            return json.dumps("impowerSelectData查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
@Process.route('/impowerPeakItemSelect', methods=['POST', 'GET'])
def impowerPeakItemSelect():
    if request.method == 'GET':
        data = request.values
        try:
            projectName = data.get("projectName")
            ResultID = data.get("ResultID")
            imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
            imp.filter.add('http://WebXml.com.cn/')
            doctor = ImportDoctor(imp)
            client = Client(Model.Global.EmpowerURL, doctor=doctor)  # 创建一个webservice接口对象
            userzj = db_session.query(User).filter(User.Name == "dw5213").first()
            re = client.service.GetEmpowerPeakItem(userzj.Name, userzj.Password, projectName, "结果ID", ResultID)
            datadir = []
            if re[2] == 'OK':
                orgs = re[0].strip().split(";")
                a = 0
                for i in orgs:
                    igs = i.split(",")
                    if len(igs) == 5 and a > 0:
                        imp = EmpowerPeakItem()
                        imp.ID = a
                        imp.Name = igs[0]
                        imp.RetentionTime = igs[1]
                        imp.Area = igs[2]
                        imp.PercentileArea = igs[3]
                        imp.Height = igs[4]
                        datadir.append(imp)
                        a = a + 1
                    else:
                        a = a + 1
                        continue
            else:
                datadir = datadir.append(re[1])
            jsonoclass = json.dumps(datadir, cls=AlchemyEncoder, ensure_ascii=False)
            return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "/impowerPeakItemSelect报错Error：" + str(e), current_user.Name)
            return json.dumps("impowerPeakItemSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
@Process.route('/impowerIniDataSelect', methods=['POST', 'GET'])
def impowerIniDataSelect():
    if request.method == 'GET':
        data = request.values
        try:
            projectName = data.get("projectName")
            SampleName = data.get("SampleName")
            SampleBottle = data.get("SampleBottle")
            Sampling = data.get("Sampling")
            imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
            imp.filter.add('http://WebXml.com.cn/')
            doctor = ImportDoctor(imp)
            client = Client(Model.Global.EmpowerURL, doctor=doctor)  # 创建一个webservice接口对象
            userzj = db_session.query(User).filter(User.Name == "dw5213").first()#userzj.Name, userzj.Password, "成品组\\2017健胃消食片浸膏粉橙皮苷含量", "样品名称", "17116003-2", "样品瓶", "	67", "进样", "2"
            re = client.service.GetEmpowerIniData(userzj.Name, userzj.Password, projectName, "样品名称", SampleName, "样品瓶", SampleBottle, "进样", Sampling)
            dir = {}
            list1 = []
            list2 = []
            if re[2] == 'OK':
                ch = re[0].split("\n")
                for i in range(0,len(ch)):
                    print(ch[i])
                    if i > 2:
                        if ch[i] == "":
                            continue
                        else:
                            chs = ch[i].split("\t")
                            list1.append(chs[0])
                            list2.append(chs[1])
                    else:
                        continue
            dir["X"] = list1
            dir["Y"] = list2
            jsonobject = json.dumps(dir, cls=AlchemyEncoder, ensure_ascii=False)
            return jsonobject
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "/impowerIniDataSelect报错Error：" + str(e), current_user.Name)
            return json.dumps("impowerIniDataSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
#含量查询
@Process.route('/EmpowerContentSelect', methods=['GET', 'POST'])
def EmpowerContentSelect():
    if request.method == 'GET':
        data = request.values
        try:
            ResultID = data.get("ResultID")
            if not ResultID:
                return ""
            Content = db_session.query(EmpowerContent).filter(EmpowerContent.ResultID == ResultID).first()
            if not Content:
                Content.ID = ""
                Content.ResultID = ""
                Content.Content = ""
            return json.dumps(Content, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "EmpowerContentSelect查询报错Error：" + str(e), current_user.Name)
            return json.dumps("EmpowerContentSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


#含量修改
@Process.route('/EmpowerContentUpdate', methods=['GET', 'POST'])
def EmpowerContentCostUpdate():
    if request.method == 'POST':
        data = request.values
        ID = data.get("ID")
        Content = data.get("Content")
        ResultID = data.get("ResultID")
        jour = EmpowerContentJournal()
        jour.OperationDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        jour.Other = ResultID
        if not ID:
            jour.DetailedInformation = "用户"+current_user.Name+"增加含量"
            jour.Operation = "增加含量"
            db_session.add(jour)
            db_session.commit()
            return insert(EmpowerContent, data)
        jour.DetailedInformation = "用户" + current_user.Name + "修改含量"
        jour.Operation = "修改含量"
        db_session.add(jour)
        db_session.commit()
        return update(EmpowerContent, data)

@Process.route('/EmpowerContentJournalSelect', methods=['GET', 'POST'])
def EmpowerContentJournalSelect():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ResultID = data.get("ResultID")
                if not ResultID:
                    return ""
                total = db_session.query(EquipmentManagementManua).count()
                oclass = db_session.query(EmpowerContentJournal).filter(EmpowerContentJournal.Other == ResultID).order_by(desc("OperationDate")).all()
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "EmpowerContentJournalSelect查询报错Error：" + str(e), current_user.Name)
            return json.dumps("EmpowerContentJournalSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#备件类型增加
@Process.route('/WMStatusLoadCreate', methods=['GET', 'POST'])
def WMStatusLoadCreate():
    if request.method == 'POST':
        data = request.values
        return insert(WMStatusLoad, data)

#备件类型修改
@Process.route('/WMStatusLoadUpdate', methods=['GET', 'POST'])
def WMStatusLoadUpdate():
    if request.method == 'POST':
        data = request.values
        return update(WMStatusLoad, data)

#备件类型删除
@Process.route('/WMStatusLoadDetele', methods=['GET', 'POST'])
def WMStatusLoadDetele():
    if request.method == 'POST':
        data = request.values
        return delete(WMStatusLoad, data)

@Process.route('/WMStatusLoadSelect', methods=['GET', 'POST'])
def WMStatusLoadSelect():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                BillNo = data["BillNo"]
                if BillNo == "":
                    Count = db_session.query(WMStatusLoad).filter_by().count()
                    Class = db_session.query(WMStatusLoad).filter_by().all()[inipage:endpage]
                else:
                    Count = db_session.query(WMStatusLoad).filter(
                        WMStatusLoad.BillNo == BillNo).count()
                    Class = db_session.query(WMStatusLoad).filter(
                        WMStatusLoad.BillNo == BillNo).all()[inipage:endpage]
                jsonoclass = json.dumps(Class, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(Count) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "WMStatusLoadSelect查询报错Error：" + str(e), current_user.Name)
            return json.dumps("WMStatusLoadSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@Process.route('/WMStatusLoadConfirm', methods=['GET', 'POST'])
def WMStatusLoadConfirm():
    """原料质检确认"""
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                ID = data.get("id")
                oclass = db_session.query(StapleProducts).filter(StapleProducts.ID == ID).first()
                if oclass.ConfirmStatus == None or oclass.ConfirmStatus == "":
                    return "请先做质保状态确认，再发送！"
                dic = []
                StoreDef_ID = "1"
                if oclass.mid in ("100005", "100009","2120"):
                    StoreDef_ID = "2"
                dic.append(
                    {"BillNo": str(oclass.BillNo), "mid": str(oclass.mid), "BatchNo": str(oclass.BatchNo),
                     "StoreDef_ID": StoreDef_ID, "OldStatus": "3","NewStatus":"1" if "合格" in oclass.ConfirmStatus else "2"})
                client = Client(Model.Global.WMSurl)
                ret = client.service.Mes_Interface("MStatusLoad", json.dumps(dic))
                if ret[0] == "SUCCESS":
                    return 'OK'
                else:
                    return json.dumps("调用接口MStatusLoad报错："+ret[1])
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由：/WMStatusLoadConfirm,Error：" + str(e), current_user.Name)

#半成品库增加
@Process.route('/PartiallyProductsCreate', methods=['GET', 'POST'])
def PartiallyProductsCreate():
    if request.method == 'POST':
        data = request.values
        return insert(PartiallyProducts, data)

#半成品库修改
@Process.route('/PartiallyProductsUpdate', methods=['GET', 'POST'])
def PartiallyProductsUpdate():
    if request.method == 'POST':
        data = request.values
        return update(PartiallyProducts, data)

#半成品库删除
@Process.route('/PartiallyProductsDetele', methods=['GET', 'POST'])
def PartiallyProductsDetele():
    if request.method == 'POST':
        data = request.values
        return delete(PartiallyProducts, data)

@Process.route('/PartiallyProductsSelect', methods=['GET', 'POST'])
def PartiallyProductsSelect():
    '''半成品库查询'''
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data.get("offset"))  # 页数
                rowsnumber = int(data.get("limit"))  # 行数
                inipage = pages * rowsnumber + 0  # 起始页
                endpage = pages * rowsnumber + rowsnumber  # 截止页
                BatchID = data.get("BatchID")
                if BatchID == "" or BatchID ==None:
                    Count = db_session.query(PartiallyProducts).count()
                    Class = db_session.query(PartiallyProducts).order_by(desc("BatchID")).all()
                else:
                    Count = db_session.query(PartiallyProducts).filter(
                        PartiallyProducts.BatchID == BatchID).count()
                    Class = db_session.query(PartiallyProducts).filter(
                        PartiallyProducts.BatchID == BatchID).order_by(desc("BatchID")).all()
                jsonoclass = json.dumps(Class, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(Count) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "WMStatusLoadSelect查询报错Error：" + str(e), current_user.Name)
            return json.dumps("WMStatusLoadSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@Process.route('/PartiallyProductsChecked', methods=['GET', 'POST'])
def PartiallyProductsChecked():
    '''半成品复核审核'''
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data.get("ID")
                CheckedStatus = data.get("CheckedStatus")
                ReviewStatus = data.get("ReviewStatus")
                QAConfirmStatus = data.get("QAConfirmStatus")
                ConfirmStatus = data.get("ConfirmStatus")
                if ID is not "" or ID is not None:
                    cla = db_session.query(PartiallyProducts).filter_by(ID = ID).first()
                    if CheckedStatus != None:
                        cla.CheckedStatus = CheckedStatus
                        cla.CheckedPeople = current_user.Name
                    elif ConfirmStatus != None:
                        cla.ConfirmStatus = ConfirmStatus
                        cla.connfirmer = current_user.Name
                    elif ReviewStatus != None:
                        cla.ReviewStatus = ReviewStatus
                        cla.Reviewer = current_user.Name
                    elif QAConfirmStatus != None:
                        cla.QAConfirmStatus = QAConfirmStatus
                        cla.QAConfirmer = current_user.Name
                        dic = []
                        StoreDef_ID = "1"
                        mid = db_session.query(Material.MATCode).filter(Material.MATName == cla.BrandName).first()[0]
                        if cla.BrandName == "肿节风浸膏":
                            StoreDef_ID = "2"
                        dic.append(
                            {"BillNo": str(cla.BatchID + cla.BrandID), "mid": mid, "BatchNo": str(cla.BatchID),
                             "StoreDef_ID": StoreDef_ID, "OldStatus": "3",
                             "NewStatus": "1" if "质保通过" in QAConfirmStatus else "2"})
                        client = Client(Model.Global.WMSurl)
                        ret = client.service.Mes_Interface("MStatusLoad", json.dumps(dic))
                        if ret[0] != "SUCCESS":
                            return json.dumps("调用半成品检验接口MStatusLoad报错：" + ret[1])
                    db_session.commit()
                    return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "/PartiallyProductsChecked半成品复核审核报错Error：" + str(e), current_user.Name)
            return json.dumps("/PartiallyProductsChecked半成品复核审核报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@Process.route('/WMSStoreSelect', methods=['GET', 'POST'])
def WMSStoreSelect():
    '''WMS备料库存信息查询'''
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                client = Client(Model.Global.WMSurl)
                ret = client.service.Mes_Interface_TL("StoreLoad")
                if ret["Mes_Interface_TLResult"] == "SUCCESS":
                    jsondata = json.loads(ret["json_data"])
                    return '{"total"' + ":" + str(len(jsondata)) + ',"rows"' + ":\n" + json.dumps(jsondata, cls=AlchemyEncoder, ensure_ascii=False) + "}"
                else:
                    return json.dumps(ret["ErrData"])
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "WMSStoreSelect查询报错Error：" + str(e), current_user.Name)
            return json.dumps("WMSStoreSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@Process.route('/WMSDetailedSelect', methods=['GET', 'POST'])
def WMSDetailedSelect():
    '''WMS流水信息查询'''
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                dic = []
                BatchID = data.get("BatchID")
                BrandName = data.get("BrandName")
                dic.append({"BatchID":BatchID,"BrandName":BrandName})
                jsondic = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
                client = Client(Model.Global.WMSurl)
                ret = client.service.Mes_Interface_TL("WorkFlowLoad", jsondic)
                if ret["Mes_Interface_TLResult"] == "SUCCESS":
                    jsondata = json.loads(ret["json_data"])
                    return '{"total"' + ":" + str(len(jsondata)) + ',"rows"' + ":\n" + json.dumps(jsondata, cls=AlchemyEncoder, ensure_ascii=False) + "}"
                else:
                    return json.dumps(ret["ErrData"])
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "WMSDetailedSelect查询报错Error：" + str(e), current_user.Name)
            return json.dumps("WMSDetailedSelect查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@Process.route('/SAPtoWMSMailBL', methods=['GET', 'POST'])
def SAPtoWMSMailBL():
    '''
    同步物料信息到备料段
    :return:
    '''
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                dir = []
                for key in jsonnumber:
                    id = int(key)
                    oclass = db_session.query(product_infoERP).filter_by(ID=id).first()
                    dir.append(oclass)
                jsondic = json.dumps(dir, cls=AlchemyEncoder, ensure_ascii=False)
                client = Client(Model.Global.WMSurl)
                ret = client.service.Mes_Interface_TL("MatDetLoad", jsondic)
                if ret[0] != "SUCCESS":
                    return json.dumps("调用SAPtoWMSMailBL接口报错！" + ret[1])
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)
            insertSyslog("接口/SAPtoWMSMailBL", "同步物料信息到备料段报错Error：" + str(e), current_user.Name)

@Process.route('/StapleProductsPage')
def StapleProductsPage():
    '''
    WMS原料检验
    '''
    return render_template('StapleProductsPage.html')

#SAP采购订单增加
@Process.route('/PurchasingOrderCreate', methods=['GET', 'POST'])
def PurchasingOrderCreate():
    if request.method == 'POST':
        data = request.values
        return insert(PurchasingOrder, data)

#SAP采购订单修改
@Process.route('/PurchasingOrderUpdate', methods=['GET', 'POST'])
def PurchasingOrderUpdate():
    if request.method == 'POST':
        data = request.values
        return update(PurchasingOrder, data)

#SAP采购订单删除
@Process.route('/PurchasingOrderDetele', methods=['GET', 'POST'])
def PurchasingOrderDetele():
    if request.method == 'POST':
        data = request.values
        return delete(PurchasingOrder, data)

@Process.route('/PurchasingOrderSelect', methods=['GET', 'POST'])
def PurchasingOrderSelect():
    '''SAP采购订单查询'''
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data.get("offset"))  # 页数
                rowsnumber = int(data.get("limit"))  # 行数
                inipage = pages * rowsnumber + 0  # 起始页
                endpage = pages * rowsnumber + rowsnumber  # 截止页
                BillNo = data["BillNo"]
                if BillNo == "":
                    Count = db_session.query(PurchasingOrder).filter_by().count()
                    Class = db_session.query(PurchasingOrder).filter_by().all()[inipage:endpage]
                else:
                    Count = db_session.query(PurchasingOrder).filter(
                        PurchasingOrder.BillNo == BillNo).count()
                    Class = db_session.query(PurchasingOrder).filter(
                        PurchasingOrder.BillNo == BillNo).all()[inipage:endpage]
                jsonoclass = json.dumps(Class, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(Count) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SAP采购订单查询报错Error：" + str(e), current_user.Name)
            return json.dumps("SAP采购订单查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@Process.route('/WMS_SendPartiallyProducts', methods=['GET', 'POST'])
def WMS_SendPartiallyProducts():
    '''发送半成品到WMS'''
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                dic = []
                for key in jsonnumber:
                    id = int(key)
                    oclass = db_session.query(PartiallyProducts).filter(PartiallyProducts.ID == id).first()
                    StoreDef_ID = "1"
                    if oclass.BrandName == "肿节风浸膏":
                        StoreDef_ID = "2"
                    product_code = db_session.query(ERPproductcode_prname.product_code).filter(ERPproductcode_prname.PRName == oclass.BrandName).first()[0]
                    dic.append(
                        {"BillNo": str(oclass.BatchID) + str(oclass.BrandID), "BatchNo":str(oclass.BatchID), "btype": "102", "StoreDef_ID": StoreDef_ID,
                         "mid": product_code, "num": oclass.Produce})
                jsondic = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
                client = Client(Model.Global.WMSurl)
                ret = client.service.Mes_Interface("billload", jsondic)
                if ret[0] != "SUCCESS":
                    return json.dumps("调用WMS_SendPartiallyProducts接口报错！" + ret[1])
                oclass.IsSend = "10"
                db_session.commit()
                return 'OK'
        except Exception as e:
            print("调用WMS_SendPartiallyProducts接口报错！")
            return json.dumps("调用WMS_SendPartiallyProducts接口报错！")