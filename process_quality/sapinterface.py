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

from Model.sap_model import SapBatchInfo, SapBrandUnitInfo, SapMatailInfo
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
    product_plan, product_infoERP, WMSDetail, PurchasingOrder, WMSTrayNumber
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
import uuid



engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()


from suds.sax.text import Raw
from suds.client import Client
from suds.transport.https import HttpAuthenticated

imp = Import('http://www.w3.org/2001/XMLSchema',
             location='http://www.w3.org/2001/XMLSchema.xsd')
imp.filter.add('http://WebXml.com.cn/')

sapinter = Blueprint('sapinter', __name__)
@sapinter.route('/SapBatchInfo')
def sapBatchInfo():
    '''
    SAP物料主数据同步页面
    return:
    '''
    return render_template('SapBatchInfo.html')

@sapinter.route('/tosapBrandUnitInfo')
def tosapBrandUnitInfo():
    '''
    SAP物料主数据同步页面
    return:
    '''
    return render_template('SapBrandUnitInfo.html')
@sapinter.route('/SapBatchInfoSearch', methods=['POST', 'GET'])
def SapBatchInfoSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                AUFNR = data.get('AUFNR')
                CHARG = data.get('CHARG')
                MAKTX = data.get('MAKTX')
                if AUFNR != "" and CHARG != "" and MAKTX != "":
                    total = db_session.query(SapBatchInfo).filter(
                        SapBatchInfo.AUFNR == AUFNR, SapBatchInfo.CHARG == CHARG, SapBatchInfo.MAKTX == MAKTX).count()
                    oclass = db_session.query(SapBatchInfo).filter(
                        SapBatchInfo.AUFNR == AUFNR, SapBatchInfo.CHARG == CHARG, SapBatchInfo.MAKTX == MAKTX
                    ).order_by(desc("GSTRP")).all()[inipage:endpage]
                elif AUFNR != "" and CHARG != "" and MAKTX == "":
                    total = db_session.query(SapBatchInfo).filter(
                        SapBatchInfo.AUFNR == AUFNR, SapBatchInfo.CHARG == CHARG).count()
                    oclass = db_session.query(SapBatchInfo).filter(
                        SapBatchInfo.AUFNR == AUFNR, SapBatchInfo.CHARG == CHARG
                    ).order_by(desc("GSTRP")).all()[inipage:endpage]
                elif  AUFNR == "" and CHARG != "" and MAKTX != "":
                    total = db_session.query(SapBatchInfo).filter(SapBatchInfo.CHARG == CHARG, SapBatchInfo.MAKTX == MAKTX).count()
                    oclass = db_session.query(SapBatchInfo).filter(SapBatchInfo.CHARG == CHARG, SapBatchInfo.MAKTX == MAKTX
                    ).order_by(desc("GSTRP")).all()[inipage:endpage]
                elif  AUFNR != "" and CHARG == "" and MAKTX != "":
                    total = db_session.query(SapBatchInfo).filter(SapBatchInfo.AUFNR == AUFNR, SapBatchInfo.MAKTX == MAKTX).count()
                    oclass = db_session.query(SapBatchInfo).filter(SapBatchInfo.AUFNR == AUFNR, SapBatchInfo.MAKTX == MAKTX
                    ).order_by(desc("GSTRP")).all()[inipage:endpage]
                else:
                    total = db_session.query(SapBatchInfo).filter().count()
                    oclass = db_session.query(SapBatchInfo).filter().order_by(desc("GSTRP")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "工艺质量确认流程表查询报错Error：" + str(e), current_user.Name)
            return json.dumps("工艺质量确认流程表查询报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)
@sapinter.route('/SapBrandUnitInfoSearch', methods=['POST', 'GET'])
def SapBrandUnitInfoSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                AUFNR = data.get('AUFNR')
                if not AUFNR:
                    total = db_session.query(SapBrandUnitInfo).filter().count()
                    oclass = db_session.query(SapBrandUnitInfo).filter().all()[inipage:endpage]
                else:
                    total = db_session.query(SapBrandUnitInfo).filter(
                        SapBrandUnitInfo.AUFNR == AUFNR).count()
                    oclass = db_session.query(SapBrandUnitInfo).filter(
                        SapBrandUnitInfo.AUFNR == AUFNR).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "工艺质量确认流程表查询报错Error：" + str(e), current_user.Name)
            return json.dumps("工艺质量确认流程表查询报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)
@sapinter.route('/SapBrandUnitInfoUpdate', methods=['POST', 'GET'])
def SapBrandUnitInfoUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data.get('ID')
                if ID:
                    oclass = db_session.query(SapBrandUnitInfo).filter(SapBrandUnitInfo.ID == ID).first()
                    oclass.BUDAT = data.get("BUDAT")
                    oclass.ActStartTime = data.get("ActStartTime")
                    oclass.ActFinishTime = data.get("ActFinishTime")
                    oclass.NUM1  = data.get("NUM1")
                    oclass.QTY   = data.get("QTY")
                    oclass.QDATE = data.get("QDATE")
                    oclass.HSDAT = data.get("HSDAT")
                    oclass.AGRND = data.get("AGRND")
                    oclass.SCRAP = data.get("SCRAP")
                    oclass.PRQTY = data.get("PRQTY")
                    oclass.FCONF = data.get("FCONF")
                    db_session.commit()
                return json.dumps('OK')
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SAP流程订单工序信息更新报错Error：" + str(e), current_user.Name)
            return json.dumps("SAP流程订单工序信息更新报错Error", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

@sapinter.route('/SapMatailInfoUpdate', methods=['POST', 'GET'])
def SapMatailInfoUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data.get('ID')
                if ID:
                    oclass = db_session.query(SapMatailInfo).filter(SapMatailInfo.ID == ID).first()
                    oclass.BUDAT = data.get("BUDAT")
                    oclass.Opertation = data.get("Opertation")
                    oclass.BDMNG = data.get("BDMNG")
                    oclass.CHARG = data.get("CHARG")
                    db_session.commit()
                return json.dumps('OK')
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SAP流程订单物料信息更新报错Error：" + str(e), current_user.Name)
            return json.dumps("SAP流程订单物料信息更新报错Error", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

@sapinter.route('/SapMatailInfoAdd', methods=['POST', 'GET'])
def SapMatailInfoAdd():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                smi = SapMatailInfo()
                sm = db_session.query(SapMatailInfo).filter(SapMatailInfo.ID == data.get("ID")).first()
                smi.AUFNR = sm.AUFNR
                smi.RSNUM = sm.RSNUM
                smi.RSPOS = sm.RSPOS
                smi.VORNR = sm.VORNR
                smi.SEQNO = sm.SEQNO
                smi.MATNR = sm.MATNR
                smi.MAKTX = sm.MAKTX
                smi.BDMNG = data.get("BDMNG")
                smi.MEINS = sm.MEINS
                smi.BWART = sm.BWART
                smi.CHARG = data.get("CHARG")
                smi.WERKS = sm.WERKS
                smi.LGORT = sm.LGORT
                smi.WEIGH = sm.WEIGH
                smi.Opertation = data.get("Opertation")
                smi.BUDAT = data.get("BUDAT")
                smi.Status = "未发送"
                db_session.add(smi)
                db_session.commit()
                return json.dumps('OK')
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SAP流程订单物料信息更新报错Error：" + str(e), current_user.Name)
            return json.dumps("SAP流程订单物料信息更新报错Error", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

@sapinter.route('/SapMatailInfoSearch', methods=['POST', 'GET'])
def SapMatailInfoSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                AUFNR = data.get('AUFNR')
                if not AUFNR:
                    total = db_session.query(SapMatailInfo).filter().count()
                    oclass = db_session.query(SapMatailInfo).filter().all()[inipage:endpage]
                else:
                    total = db_session.query(SapMatailInfo).filter(
                        SapMatailInfo.AUFNR == AUFNR).count()
                    oclass = db_session.query(SapMatailInfo).filter(
                        SapMatailInfo.AUFNR == AUFNR).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "工艺质量确认流程表查询报错Error：" + str(e), current_user.Name)
            return json.dumps("工艺质量确认流程表查询报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

@sapinter.route('/SAP_MailInfos', methods=['GET', 'POST'])
def SAP_MailInfos():
    '''SAP物料主数据同步接口'''
    if request.method == 'GET':
        data = request.values
        try:
            dic = {}
            data_ma = {"RID": str(uuid.uuid4()), "WERKS": "1100", "MTART": data.get("Mtart"),
                       "SDATE": data.get("StartTime"),
                       "EDATE": data.get("EndTime"), "SYSID": "WX_MES",
                       "OPDAT": datetime.datetime.now().strftime('%Y%m%d'),
                       "OPTME": datetime.datetime.now().strftime('%H%M%S')}
            dic["CATEGORY"] = ""
            dic["TYPE"] = ""
            dic["OPERATION"] = ""
            dic["DESCRIPTION"] = ""
            dic["DATA"] = data_ma
            data_json = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            # headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
            t = HttpAuthenticated(username='INTF', password='Hrjz1234')
            client = Client(Model.Global.SAPcsurl, transport=t)
            result = client.service.Z_PP_MES_INTF(data_json, 'PP1005', 'MES')
            if result:
                re = json.loads(result).get("RETURN").get("MSG_LIST")
                for i in re:
                    mat = i.get("DATA")
                    if mat:
                        e = product_infoERP()
                        e.product_code = mat.get("ITEM_CODE")
                        e.product_name = mat.get("ITEM_NAME")
                        e.product_type = mat.get("ITEM_TYPE")
                        e.product_unit = mat.get("ITEM_UNIT")
                        db_session.commit()
            return json.dumps('OK')
        except Exception as e:
            print(e)
            insertSyslog()
            return json.dumps("调用SAP物料主数据同步接口接口报错！")


from Model.control import ctrlPlan
@sapinter.route('/SAP_OrderSynchonizes', methods=['GET', 'POST'])
def SAP_OrderSynchonizes():
    '''SAP订单信息同步接口'''
    if request.method == 'GET':
        data = request.values
        try:
            dic = {}
            data_ma = {"RID": str(uuid.uuid4()), "DWERK": "1100", "DAUAT": data.get("DAUAT"),"MATNR": "","VERID": "", "AUFNR": "",
                       "SDATE": data.get("StartTime").replace("-",""),"EDATE": data.get("EndTime").replace("-",""), "CHARG": "","SYSID": "WX_MES",
                       "OPDAT": datetime.datetime.now().strftime('%Y%m%d'),"OPTME": datetime.datetime.now().strftime('%H%M%S')}
            dic["CATEGORY"] = ""
            dic["TYPE"] = ""
            dic["OPERATION"] = ""
            dic["DESCRIPTION"] = ""
            dic["DATA"] = data_ma
            data_json = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            # headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
            t = HttpAuthenticated(username='INTF', password='Intf600')
            client = Client(Model.Global.SAPurl, transport=t)
            result = client.service.Z_PP_MES_INTF(data_json, 'PP1001', 'MES')
            if result:
                hes = json.loads(result).get("HEADER")
                for i in hes:
                    PRNameoclass = db_session.query(ERPproductcode_prname).filter(
                        ERPproductcode_prname.product_code.like("%" + i.get("MATNR") + "%")).first()
                    PRName = PRNameoclass.PRName
                    batchoclass = None #db_session.query(SapBatchInfo).filter(SapBatchInfo.AUFNR == i.get("AUFNR")).first()
                    if batchoclass:
                        pm = db_session.query(PlanManager).filter(PlanManager.BatchID == i.get("CHARG"),
                                                                  PlanManager.BrandName == PRName).first()
                        if pm:
                            if pm.PlanStatus == Model.Global.PlanStatus.Checked.value:
                                batchoclass.RID = i.get("RID")
                                batchoclass.AUFNR = i.get("AUFNR")
                                batchoclass.DAUAT = i.get("DAUAT")
                                batchoclass.DWERK = i.get("DWERK")
                                batchoclass.CHARG = i.get("CHARG")
                                batchoclass.MATNR = i.get("MATNR")
                                batchoclass.MAKTX = i.get("MAKTX")
                                batchoclass.GAMNG = i.get("GAMNG")
                                batchoclass.UNIT = i.get("UNIT")
                                batchoclass.VERID = i.get("VERID")
                                batchoclass.RSNUM = i.get("RSNUM")
                                batchoclass.ROUTN = i.get("ROUTN")
                                batchoclass.GSTRP = i.get("GSTRP")
                                batchoclass.GLTRP = i.get("GLTRP")
                                batchoclass.STATE = i.get("STATE")
                                batchoclass.PLNNR = i.get("PLNNR")
                                batchoclass.PLNAL = i.get("PLNAL")
                                batchoclass.KTEXT = i.get("KTEXT")
                                batchoclass.GESSTICHPR = i.get("GESSTICHPR")
                                batchoclass.QBASE = i.get("QBASE")
                                if batchoclass.Status == "已报工":
                                    batchoclass.Status = "修改报工"
                                if batchoclass.MatilStatus == "已发送SAP":
                                    batchoclass.MatilStatus = "修改发送"
                                db_session.commit()
                        else:
                            continue
                    else:
                        pr = db_session.query(ProductRule).filter(ProductRule.PRName == PRName).first()
                        ABatchID = i.get("CHARG")
                        APlanWeight = i.get("GAMNG")
                        AUnit = i.get("UNIT")
                        if "肿节风浸膏" in i.get("MAKTX"):
                            ABrandName = "肿节风浸膏"
                        if "健胃消食片浸膏粉" in i.get("MAKTX"):
                            ABrandName = "健胃消食片浸膏粉"
                        APlanDate = datetime.datetime.strptime(i.get("GSTRP"), '%Y%m%d')
                        APlanDate = APlanDate.strftime('%Y-%m-%d')
                        PlanCreate = ctrlPlan('PlanCreate')
                        re = PlanCreate.createLinePlanManager("", float(APlanWeight), APlanDate, ABatchID, str(pr.ID),
                                                              ABrandName, ABrandName, AUnit, current_user.Name)
                        s = SapBatchInfo()
                        s.RID   = i.get("RID")
                        s.AUFNR = i.get("AUFNR")
                        s.DAUAT = i.get("DAUAT")
                        s.DWERK = i.get("DWERK")
                        s.CHARG = i.get("CHARG")
                        s.MATNR = i.get("MATNR")
                        s.MAKTX = i.get("MAKTX")
                        s.GAMNG = i.get("GAMNG")
                        s.UNIT  = i.get("UNIT")
                        s.VERID = i.get("VERID")
                        s.RSNUM = i.get("RSNUM")
                        s.ROUTN = i.get("ROUTN")
                        s.GSTRP = i.get("GSTRP")
                        s.GLTRP = i.get("GLTRP")
                        s.STATE = i.get("STATE")
                        s.PLNNR = i.get("PLNNR")
                        s.PLNAL = i.get("PLNAL")
                        s.KTEXT = i.get("KTEXT")
                        s.GESSTICHPR = i.get("GESSTICHPR")
                        s.QBASE = i.get("QBASE")
                        s.Status = "未报工"
                        s.MatilStatus = "未发送SAP"
                        db_session.add(s)
                        db_session.commit()
                phs = json.loads(result).get("PHASE")
                for ph in phs:
                    brandunitoclass = db_session.query(SapBrandUnitInfo).filter(
                        SapBrandUnitInfo.AUFNR == ph.get("AUFNR"), SapBrandUnitInfo.VORNR == ph.get("VORNR")).first()
                    if brandunitoclass == None:
                        sbu = SapBrandUnitInfo()
                        sbu.RID   = ph.get("RID")
                        sbu.AUFNR = ph.get("AUFNR")
                        sbu.ROUTN = ph.get("ROUTN")
                        sbu.VORNR = ph.get("VORNR")
                        sbu.LTXA1 = ph.get("LTXA1")
                        sbu.MGVRG = ph.get("MGVRG")
                        sbu.UNIT  = ph.get("UNIT")
                        sbu.STEUS = ph.get("STEUS")
                        sbu.VORGSCHL = ph.get("VORGSCHL")
                        sbu.VGW01 = ph.get("VGW01")
                        sbu.VGW02 = ph.get("VGW02")
                        sbu.VGW03 = ph.get("VGW03")
                        sbu.VGW04 = ph.get("VGW04")
                        sbu.VGW05 = ph.get("VGW05")
                        sbu.VGW06 = ph.get("VGW06")
                        db_session.add(sbu)
                        db_session.commit()
                    else:
                        brandunitoclass.RID = ph.get("RID")
                        brandunitoclass.AUFNR = ph.get("AUFNR")
                        brandunitoclass.ROUTN = ph.get("ROUTN")
                        brandunitoclass.VORNR = ph.get("VORNR")
                        brandunitoclass.LTXA1 = ph.get("LTXA1")
                        brandunitoclass.MGVRG = ph.get("MGVRG")
                        brandunitoclass.UNIT = ph.get("UNIT")
                        brandunitoclass.STEUS = ph.get("STEUS")
                        brandunitoclass.VORGSCHL = ph.get("VORGSCHL")
                        brandunitoclass.VGW01 = ph.get("VGW01")
                        brandunitoclass.VGW02 = ph.get("VGW02")
                        brandunitoclass.VGW03 = ph.get("VGW03")
                        brandunitoclass.VGW04 = ph.get("VGW04")
                        brandunitoclass.VGW05 = ph.get("VGW05")
                        brandunitoclass.VGW06 = ph.get("VGW06")
                        db_session.commit
                # sbui = db_session.query(SapBrandUnitInfo).filter(SapBrandUnitInfo.AUFNR == AUFNR).order_by(
                #     desc("VORNR")).first()
                # if sbui:
                #     sbui.FCONF = "X"
                #     db_session.commit()
                cms = json.loads(result).get("COMPT")
                for cm in cms:
                    matiloclass = db_session.query(SapMatailInfo).filter(
                        SapMatailInfo.AUFNR == cm.get("AUFNR"), SapMatailInfo.RSPOS == cm.get("RSPOS")).first()
                    if matiloclass == None:
                        sm = SapMatailInfo()
                        sm.RID = cm.get("RID")
                        sm.AUFNR = cm.get("AUFNR")
                        sm.RSNUM = cm.get("RSNUM")
                        sm.RSPOS = cm.get("RSPOS")
                        sm.VORNR = cm.get("VORNR")
                        sm.SEQNO = cm.get("SEQNO")
                        sm.MATNR = cm.get("MATNR")
                        sm.MAKTX = cm.get("MAKTX")
                        sm.BDMNG = cm.get("BDMNG")
                        sm.MEINS = cm.get("MEINS")
                        sm.BWART = cm.get("BWART")
                        sm.CHARG = cm.get("CHARG")
                        sm.WERKS = cm.get("WERKS")
                        sm.LGORT = cm.get("LGORT")
                        sm.WEIGH = cm.get("WEIGH")
                        sm.Status = "未发送"
                        db_session.add(sm)
                        db_session.commit()
                    else:
                        matiloclass.RID = cm.get("RID")
                        matiloclass.AUFNR = cm.get("AUFNR")
                        matiloclass.RSNUM = cm.get("RSNUM")
                        matiloclass.RSPOS = cm.get("RSPOS")
                        matiloclass.VORNR = cm.get("VORNR")
                        matiloclass.SEQNO = cm.get("SEQNO")
                        matiloclass.MATNR = cm.get("MATNR")
                        matiloclass.MAKTX = cm.get("MAKTX")
                        matiloclass.BDMNG = cm.get("BDMNG")
                        matiloclass.MEINS = cm.get("MEINS")
                        matiloclass.BWART = cm.get("BWART")
                        matiloclass.CHARG = cm.get("CHARG")
                        matiloclass.WERKS = cm.get("WERKS")
                        matiloclass.LGORT = cm.get("LGORT")
                        matiloclass.WEIGH = cm.get("WEIGH")
                        db_session.commit()
            return json.dumps('OK')
        except Exception as e:
            db_session.rollback()
            print("调用SAP订单信息同步接口口报错！")
            insertSyslog("接口error", "SAP_OrderSynchonizes报错Error：" + str(e), current_user.Name)
            return json.dumps("调用SAP订单信息同步接口报错！")

@sapinter.route('/Sap_WorkReport', methods=['GET', 'POST'])
def Sap_WorkReport():
    '''SAP报工信息接口'''
    if request.method == 'POST':
        data = request.values
        try:
            dic = {}
            data_list = []
            sbui = db_session.query(SapBrandUnitInfo).filter(SapBrandUnitInfo.ID == data.get("ID")).first()
            AUFNR = sbui.AUFNR
            sbuis = db_session.query(SapBrandUnitInfo).filter(SapBrandUnitInfo.AUFNR == AUFNR, SapBrandUnitInfo.VORNR<sbui.VORNR).order_by(desc("VORNR")).all()
            for s in sbuis:
                if s.Status != "工序报工完成"  and s.Status != "工序修改报工完成":
                    return json.dumps('请按工序顺序进行报工！')
            data_dir = {"RID": str(uuid.uuid4()), "RIDITEM": str(uuid.uuid4()), "AUFNR": sbui.AUFNR, "VORNR": sbui.VORNR,
                        "FCONF": sbui.FCONF, "WERKS": "1100",
                        "PRQTY": sbui.PRQTY, "SCRAP": "", "AGRND": "", "MEINS": sbui.UNIT,
                        "STEUS": sbui.STEUS, "HSDAT": sbui.HSDAT[0:10].replace("-", ""), "QDATE": sbui.QDATE[0:10].replace("-", ""), "QTY": sbui.QTY,
                        "NUM1": sbui.NUM1, "APP_PER": current_user.Name,
                        "ESDAT": sbui.ActStartTime[0:10].replace("-", ""),
                        "ESTME": sbui.ActStartTime[11:19].replace(":", ""),
                        "EFDAT": sbui.ActFinishTime[0:10].replace("-", ""),
                        "EFTME": sbui.ActFinishTime[11:19].replace(":", ""), "BUDAT": sbui.BUDAT[0:10].replace("-", ""),
                        "VGWTS": sbui.VORGSCHL,
                        "CONFACT1": sbui.VGW01, "CONFACT2": sbui.VGW02, "CONFACT3": sbui.VGW02,
                        "CONFACT4": sbui.VGW04,
                        "CONFACT5": sbui.VGW05, "CONFACT6": sbui.VGW06,
                        "OPDAT": datetime.datetime.now().strftime('%Y%m%d'),
                        "OPTME": datetime.datetime.now().strftime('%H%M%S')}
            data_list.append(data_dir)
            dic["CATEGORY"] = ""
            dic["TYPE"] = ""
            dic["OPERATION"] = ""
            dic["DESCRIPTION"] = ""
            dic["DATA"] = data_list
            data_json = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            # headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
            t = HttpAuthenticated(username='INTF', password='Intf600')
            client = Client(Model.Global.SAPurl, transport=t)
            result = client.service.Z_PP_MES_INTF(data_json, 'PP1003', 'MES')
            if result:
                re = json.loads(result).get("RETURN").get("MSGTY")
                if re == "S":
                    baog = db_session.query(SapBrandUnitInfo).filter(SapBrandUnitInfo.ID == data.get("ID")).first()
                    if baog.Status == "修改报工":
                        baog.Status = "工序修改报工完成"
                    else:
                        baog.Status = "工序报工完成"
                    db_session.commit()
                    sbuis = db_session.query(SapBrandUnitInfo).filter(SapBrandUnitInfo.ID == AUFNR).all()
                    flag = "True"
                    for s in sbuis:
                        if s.Status != "工序报工完成" or s.Status != "工序修改报工完成":
                            flag = "Flase"
                    if flag == "True":
                        sbi = db_session.query(SapBatchInfo).filter(SapBatchInfo.AUFNR == AUFNR).first()
                        sbi.Status = "已报工"
                    return json.dumps('OK')
                else:
                    return json.dumps(json.loads(result).get("RETURN").get("MESSAGE"))

        except Exception as e:
            db_session.rollback()
            print("调用SAP报工信息接口报错！")
            insertSyslog("调用SAP报工信息接口报错", "Sap_WorkReport报错Error：" + str(e), current_user.Name)
            return json.dumps("调用SAP报工信息接口报错！")

@sapinter.route('/Sap_Matailre', methods=['GET', 'POST'])
def Sap_Matailre():
    '''SAP物料信息返回接口'''
    if request.method == 'POST':
        data = request.values
        try:
            dic = {}
            data_list = []
            IDS = json.loads(data.get("IDS"))
            AUFNR = ""
            for ID in IDS:
                smi = db_session.query(SapMatailInfo).filter(SapMatailInfo.ID == ID).first()
                AUFNR = smi.AUFNR
                data_dir = {"RID": str(uuid.uuid4()), "RIDITEM": str(uuid.uuid4()), "AUFNR": smi.AUFNR, "RSNUM": smi.RSNUM,
                            "RSPOS": smi.RSPOS, "MATNR": smi.MATNR,
                            "MAKTX": smi.MAKTX, "BDMNG": smi.BDMNG, "MEINS": smi.MEINS,
                            "CHARG": smi.CHARG, "LGORT": smi.LGORT, "WERKS": smi.WERKS, "BWART": "261",
                            "BUDAT": smi.BUDAT[0:10].replace("-", ""), "OPDAT": smi.Opertation[0:10].replace("-", ""),
                            "OPTME": smi.Opertation[11:19].replace(":", "")}
                data_list.append(data_dir)
            dic["CATEGORY"] = ""
            dic["TYPE"] = ""
            dic["OPERATION"] = ""
            dic["DESCRIPTION"] = ""
            dic["DATA"] = data_list
            data_json = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            # headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
            t = HttpAuthenticated(username='INTF', password='Intf600')
            client = Client(Model.Global.SAPurl, transport=t)
            result = client.service.Z_PP_MES_INTF(data_json, 'PP1002', 'MES')
            if result:
                re = json.loads(result).get("RETURN").get("MSGTY")
                if re == "S":
                    for ID in IDS:
                        smire = db_session.query(SapMatailInfo).filter(SapMatailInfo.ID == ID).first()
                        smire.Status = "已发送"
                        db_session.commit()
                    sms = db_session.query(SapMatailInfo).filter(SapMatailInfo.AUFNR == AUFNR).all()
                    flag = "True"
                    for s in sms:
                        if s.Status != "已发送":
                            flag = "Flase"
                    if flag == "True":
                        sbi = db_session.query(SapBatchInfo).filter(SapBatchInfo.AUFNR == AUFNR).first()
                        sbi.MatilStatus = "已发送SAP"
                    return json.dumps('OK')
                else:
                    return json.dumps(json.loads(result).get("RETURN").get("MESSAGE"))

        except Exception as e:
            db_session.rollback()
            print("SAP物料信息返回接口报错！")
            insertSyslog("SAP物料信息返回接口报错", "Sap_Matailre报错Error：" + str(e), current_user.Name)
            return json.dumps("调用SAP物料信息返回接口！")