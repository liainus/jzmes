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
                if not AUFNR:
                    total = db_session.query(SapBatchInfo).filter().count()
                    oclass = db_session.query(SapBatchInfo).filter().order_by(desc("GSTRP")).all()[inipage:endpage]
                else:
                    total = db_session.query(SapBatchInfo).filter(
                        SapBatchInfo.AUFNR == AUFNR).count()
                    oclass = db_session.query(SapBatchInfo).filter(
                        SapBatchInfo.AUFNR == AUFNR).order_by(desc("GSTRP")).all()[inipage:endpage]
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
                    oclass = db_session.query(SapBrandUnitInfo).filter().order_by(desc("ID")).all()[inipage:endpage]
                else:
                    total = db_session.query(SapBrandUnitInfo).filter(
                        SapBrandUnitInfo.AUFNR == AUFNR).count()
                    oclass = db_session.query(SapBrandUnitInfo).filter(
                        SapBrandUnitInfo.AUFNR == AUFNR).order_by(desc("ID")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "工艺质量确认流程表查询报错Error：" + str(e), current_user.Name)
            return json.dumps("工艺质量确认流程表查询报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

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
                    oclass = db_session.query(SapMatailInfo).filter().order_by(desc("ID")).all()[inipage:endpage]
                else:
                    total = db_session.query(SapMatailInfo).filter(
                        SapMatailInfo.AUFNR == AUFNR).count()
                    oclass = db_session.query(SapMatailInfo).filter(
                        SapMatailInfo.AUFNR == AUFNR).order_by(desc("ID")).all()[inipage:endpage]
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
                       "SDATE": data.get("StartTime"),"EDATE": data.get("EndTime"), "CHARG": "","SYSID": "WX_MES",
                       "OPDAT": datetime.datetime.now().strftime('%Y%m%d'),"OPTME": datetime.datetime.now().strftime('%H%M%S')}
            dic["CATEGORY"] = ""
            dic["TYPE"] = ""
            dic["OPERATION"] = ""
            dic["DESCRIPTION"] = ""
            dic["DATA"] = data_ma
            data_json = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            # headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
            t = HttpAuthenticated(username='INTF', password='Hrjz1234')
            client = Client(Model.Global.SAPcsurl, transport=t)
            result = client.service.Z_PP_MES_INTF(data_json, 'PP1001', 'MES')
            if result:
                hes = json.loads(result).get("HEADER")
                for i in hes:
                    ABatchID = i.get("CHARG")
                    APlanWeight = i.get("GAMNG")
                    AUnit = i.get("UNIT")
                    ABrandID = i.get("MATNR")
                    ABrandName = i.get("MAKTX")
                    APlanDate = i.get("GSTRP")
                    PlanCreate = ctrlPlan('PlanCreate')
                    re = PlanCreate.createLinePlanManager("", APlanWeight, APlanDate, ABatchID, ABrandID,
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
                    s.UNIT  = i.get("UNIT ")
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
                    db_session.add(s)
                    db_session.commit()
                phs = json.loads(result).get("PHASE")
                for ph in phs:
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
                cms = json.loads(result).get("COMPT")
                for cm in cms:
                    sm = SapMatailInfo()
                    sm.RID =   cm.get("RID")
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
                    db_session.add(sm)
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
    if request.method == 'GET':
        data = request.values
        try:
            dic = {}
            a = ""
            data_ma = {"RID": str(uuid.uuid4()), "WERKS": "1100", "MTART": "Z001",
                       "CDATE": "20201110",
                       "EDATE": "20201110", "SYSID": "MES",
                       "OPDAT": "20201110",
                       "OPTME": "083030"}
            dic["CATEGORY"] = ""
            dic["TYPE"] = ""
            dic["OPERATION"] = ""
            dic["DESCRIPTION"] = ""
            dic["DATA"] = data_ma
            data_json = json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            # headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
            t = HttpAuthenticated(username='INTF', password='Hrjz1234')
            client = Client(Model.Global.SAPcsurl, transport=t)
            result = client.service.Z_PP_MES_INTF(data_json, 'PP1003', 'MES')
            if result:
                re = json.loads(result).get("RETURN").get("MSG_LIST")
                for i in re:
                    product = i.get("HEADER")
                    if product:
                        e = product_plan()
                        e.plan_period = product.get("RID")
                        e.product_code = product.get("")
                        e.product_name = product.get("")
                        e.plan_quantity = product.get("")
                        e.product_unit = product.get("")
                        e.meter_type = product.get("")
                        e.bill_code = product.get("AUFNR")
                        e.plan_type = product.get("DAUAT")
                        e.create_time = product.get("")
                        e.transform_time = product.get("")
                        e.transform_flag = product.get("")
                        db_session.add(e)
                        db_session.commit()
            return json.dumps(result)
        except Exception as e:
            print("调用SAP报工信息接口报错！")
            return json.dumps("调用SAP报工信息接口报错！")