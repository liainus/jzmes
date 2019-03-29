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
from Model.system import CenterCost, ERPproductcode_prname, SchedulingStock
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
            plan_id = data['plan_id']
            plan = ERP_session.query(product_plan).filter(product_plan.plan_id == plan_id).first()
            if plan.transform_flag == "1":
                return "此数据已经同步过，请选择没有同步过的数据！"
            e = product_plan()
            e.plan_period = plan.plan_period
            e.product_code = plan.product_code
            e.product_name = plan.product_name
            e.plan_quantity = plan.plan_quantity
            e.product_unit = plan.product_unit
            e.meter_type = plan.meter_type
            e.plan_type = plan.plan_type
            e.create_time = plan.create_time
            e.transform_time = plan.transform_time
            e.transform_flag = plan.transform_flag
            db_session.add(e)
            db_session.commit()
            plan.transform_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            plan.transform_flag = 1
            ERP_session.commit()
            PRName = db_session.query(ERPproductcode_prname.PRName).filter(ERPproductcode_prname.product_code == plan.product_code).first()[0]
            ProductRuleID = db_session.query(ProductRule.ID).filter(ProductRule.PRName == PRName).first()[0]
            ss = db_session.query(SchedulingStock).filter(SchedulingStock.product_code == plan.product_code).all()
            if ss != None:
                for s in ss:
                    db_session.delete(s)
                db_session.commit()
            MATIDs = db_session.query(MaterialBOM.MATID).filter(MaterialBOM.ProductRuleID == ProductRuleID).all()
            for MATID in MATIDs:
                MATName = db_session.query(Material.MATName).filter(Material.ID == MATID).first()[0]
                sc = SchedulingStock()
                sc.product_code = plan.product_code
                sc.MATName = MATName
                db_session.add(sc)
            db_session.commit()
            return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "同步ERP计划表报错Error：" + str(e), current_user.Name)

@ERP.route('/erp_model/product_planUpdate', methods=['POST', 'GET'])
def product_planUpdate():
    if request.method == 'POST':
        data = request.values
        return update(product_plan, data)


@ERP.route('/erp_model/product_planDelete', methods=['POST', 'GET'])
def product_planDelete():
    '''
    删除ERP计划信息
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(product_plan).filter_by(plan_id=id).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        insertSyslog("error", "删除户ID为" + str(id) + "报错Error：" + str(ee), current_user.Name)
                        return json.dumps("删除ERP计划信息报错", cls=AlchemyEncoder, ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "删除ERP计划信息报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@ERP.route('/erp_model/product_planCreate', methods=['POST', 'GET'])
def product_planCreate():
    if request.method == 'POST':
        data = request.values
        return insert(product_plan, data)


