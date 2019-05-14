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
from Model.core import ProcessUnit, Equipment, SysLog, MaterialBOM, ProductRule, Material
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
    EquipmentTimeStatisticTree, SystemEQPCode, EquipmentManagementManua, EquipmentMaintenanceStandard, product_info, product_plan, product_infoERP
from sqlalchemy import create_engine, Column, ForeignKey, Table, Integer, String, and_, or_, desc,extract
from io import StringIO
import calendar
from Model.system import CenterCost, ERPproductcode_prname, SchedulingStock, ProcessQualityPDF, ProcessQuality
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
    dir["a"] = str(i)
    dir["b"] = str(i)
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
        :param name:
        :param times:
        :return:
        '''
        dic = []
        for i in range(0, 3):
            dic.append(appendStr(i))
        return json.dumps(dic)
    @rpc(Unicode, Unicode, _returns=Iterable(Unicode))
    def WMS_Order_Do_Action(self, name, times):
        for i in range(times):
            yield u'Hello, %s' % name

    @rpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(self, name, times):
        for i in range(times):
            yield u'Hello, %s' % name

class SAP_Interface(ServiceBase):
    logging.basicConfig(level=logging.DEBUG)
    @rpc(Unicode, Unicode, _returns=Unicode())
    def SAP_Order_Download(self, name, json_data):
        '''
        SAP同步采购订单
        :param data:
        :return:
        '''
        dic = []
        dict_data = json.loads(json_data)
        for oc in dict_data:
            print(oc['a'])
        for i in range(0, 3):
            dic.append(appendStr(i))
        return json.dumps(dic)

class NH_Interface(ServiceBase):
    logging.basicConfig(level=logging.DEBUG)
    @rpc(Unicode, Unicode, _returns=Unicode())
    def NH_GetTime(self, name, json_data):
        '''
        SAP同步采购订单
        :param data:
        :return:
        '''
        dic = []
        dict_data = json.loads(json_data)
        for oc in dict_data:
            print(oc['a'])
        for i in range(0, 3):
            dic.append(appendStr(i))
        return json.dumps(dic)

wsdl_url = "http://127.0.0.1:5001/?wsdl"
def say_hello_test(url,name):
    client = Client(url)  # 创建一个webservice接口对象
    re = client.service.WMS_Order_Download(name, 1) # 调用这个接口下的getMobileCodeInfo方法，并传入参数
    print(re)
    return re

@Process.route('/aaaa', methods=['POST', 'GET'])
def aaaa():
    if request.method == 'GET':
        re = say_hello_test(wsdl_url,"aa")
        return re
