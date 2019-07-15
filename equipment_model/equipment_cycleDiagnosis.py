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
from Model.core import ProcessUnit, Equipment, SysLog, PlanManager
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
    EquipmentTimeStatisticTree, SystemEQPCode, EquipmentManagementManua, EquipmentMaintenanceStandard, Instrumentation, \
    InstrumentationHandle
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

diagnosis = Blueprint('diagnosis', __name__)

@diagnosis.route('/cyclediagnosis')
def cyclediagnosis():
    '''仪器仪表周期诊定页面跳转'''
    return render_template('cyclediagnosis.html')

@diagnosis.route('/a', methods=['POST', 'GET'])
def a():
    if request.method == 'GET':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                return select("Equipment","0","5",data)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "/BatchInfoSearch查询报错Error：" + str(e), current_user.Name)

@diagnosis.route('/equipment_model/InstrumentationCreate', methods=['GET', 'POST'])
def InstrumentationCreate():
    if request.method == 'POST':
        data = request.values
        return insert(Instrumentation, data)

@diagnosis.route('/equipment_model/InstrumentationUpdate', methods=['GET', 'POST'])
def InstrumentationUpdate():
    if request.method == 'POST':
        data = request.values
        return update(Instrumentation, data)

@diagnosis.route('/equipment_model/InstrumentationDelete', methods=['GET', 'POST'])
def InstrumentationDelete():
    if request.method == 'POST':
        data = request.values
        return delete(Instrumentation, data)

@diagnosis.route('/equipment_model/InstrumentationHandleCreate', methods=['GET', 'POST'])
def InstrumentationHandleCreate():
    if request.method == 'POST':
        data = request.values
        return insert(InstrumentationHandle, data)

@diagnosis.route('/equipment_model/InstrumentationHandleUpdate', methods=['GET', 'POST'])
def InstrumentationHandleUpdate():
    if request.method == 'POST':
        data = request.values
        return update(InstrumentationHandle, data)

@diagnosis.route('/equipment_model/InstrumentationHandleDelete', methods=['GET', 'POST'])
def InstrumentationHandleDelete():
    if request.method == 'POST':
        data = request.values
        return delete(InstrumentationHandle, data)

#成本中心查询
@diagnosis.route('/equipment_model/InstrumentationSelect', methods=['GET', 'POST'])
def CenterCostSelect():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                CharityPerson = data["CharityPerson"]
                if CharityPerson == "":
                    count = db_session.query(Instrumentation).filter_by().count()
                    oclass = db_session.query(Instrumentation).filter_by().all()[inipage:endpage]
                else:
                    count = db_session.query(Instrumentation).filter(
                        CenterCost.CharityPerson.like("%"+CharityPerson+"%")).count()
                    oclass = db_session.query(Instrumentation).filter(
                        CenterCost.CharityPerson.like("%"+CharityPerson+"%")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(count) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "成本中心查询报错Error：" + str(e), current_user.Name)
            return json.dumps("成本中心查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#成本中心查询
@diagnosis.route('/equipment_model/InstrumentationHandleSelect', methods=['GET', 'POST'])
def CenterCostSelect():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                CharityPerson = data["CharityPerson"]
                if CharityPerson == "":
                    count = db_session.query(InstrumentationHandle).filter_by().count()
                    oclass = db_session.query(InstrumentationHandle).filter_by().all()[inipage:endpage]
                else:
                    count = db_session.query(InstrumentationHandle).filter(
                        CenterCost.CharityPerson.like("%"+CharityPerson+"%")).count()
                    oclass = db_session.query(InstrumentationHandle).filter(
                        CenterCost.CharityPerson.like("%"+CharityPerson+"%")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(count) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "成本中心查询报错Error：" + str(e), current_user.Name)
            return json.dumps("成本中心查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

