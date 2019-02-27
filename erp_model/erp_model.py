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
from Model.core import ProcessUnit, Equipment, SysLog
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
from Model.system import CenterCost
from tools.common import logger,insertSyslog,insert,delete,update,select
import os
import openpyxl

engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

engine_ERP = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING_ERP, deprecate_large_types=True)
Session_ERP = sessionmaker(bind=engine_ERP)
ERP_session = Session_ERP()

ERP = Blueprint('ERP', __name__)

@ERP.route('/ERP_productinfo')
def ERP_productinfo():
    return render_template('ERP_productinfo.html')

@ERP.route('/ERP_productplan')
def ERP_productplan():
    return render_template('ERP_productplan.html')

@ERP.route('/erp_model/ERP_productinfoSearch', methods=['POST', 'GET'])
def ERP_productinfoSearch():
    '''
    ERP产品物料表查询
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                total = ERP_session.query(product_info).count()
                oclass = ERP_session.query(product_info).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "ERP产品物料表查询报错Error：" + str(e), current_user.Name)

@ERP.route('/erp_model/productinfoSearch', methods=['POST', 'GET'])
def productinfoSearch():
    '''
    ERP产品物料表查询
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                total = db_session.query(product_infoERP).count()
                oclass = db_session.query(product_infoERP).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "ERP产品物料表查询报错Error：" + str(e), current_user.Name)

@ERP.route('/erp_model/ERP_productplanSearch', methods=['POST', 'GET'])
def ERP_productplanSearch():
    '''
    ERP产品物料表查询
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                total = ERP_session.query(product_plan).count()
                oclass = ERP_session.query(product_plan).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "ERP产品物料表查询报错Error：" + str(e), current_user.Name)

@ERP.route('/erp_model/productplanSearch', methods=['POST', 'GET'])
def productplanSearch():
    '''
    ERP计划表查询
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                total = db_session.query(product_plan).count()
                oclass = db_session.query(product_plan).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "ERP产品物料表查询报错Error：" + str(e), current_user.Name)

@ERP.route('/erp_model/ERP_productinfoSynchro', methods=['POST', 'GET'])
def ERP_productinfoSynchro():
    '''
    同步ERP产品物料表
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            product_infos = ERP_session.query(product_info).all()
            sql = "TRUNCATE TABLE product_infoERP"
            db_session.execute(sql)
            db_session.commit()
            for p in product_infos:
                e = product_infoERP()
                e.product_code = p.product_code
                e.product_name = p.product_name
                e.product_type = p.product_type
                e.product_unit = p.product_unit
                db_session.add(e)
            db_session.commit()
            return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "同步ERP产品物料表报错Error：" + str(e), current_user.Name)

@ERP.route('/erp_model/ERP_productplanSynchro', methods=['POST', 'GET'])
def ERP_productplanSynchro():
    '''
    同步ERP计划表
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            product_plans = ERP_session.query(product_plan).all()
            sql = "TRUNCATE TABLE product_plan"
            db_session.execute(sql)
            db_session.commit()
            for p in product_plans:
                e = product_plan()
                e.product_code = p.product_code
                e.product_name = p.product_name
                e.plan_quantity = p.plan_quantity
                e.plan_type = p.plan_type
                e.create_time = p.create_time
                e.transform_time = p.transform_time
                e.transform_flag = p.transform_flag
                db_session.add(e)
            db_session.commit()
            return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "同步ERP计划表报错Error：" + str(e), current_user.Name)


