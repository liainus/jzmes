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
    EquipmentTimeStatisticTree, SystemEQPCode, EquipmentManagementManua, EquipmentMaintenanceStandard
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

@diagnosis.route('/equipment_model/CenterCostCreate', methods=['GET', 'POST'])
def CenterCostCreate():
    if request.method == 'POST':
        data = request.values
        return insert(CenterCost, data)

@diagnosis.route('/equipment_model/CenterCostUpdate', methods=['GET', 'POST'])
def CenterCostUpdate():
    if request.method == 'POST':
        data = request.values
        return update(CenterCost, data)

#成本中心删除
@diagnosis.route('/equipment_model/CenterCostDelete', methods=['GET', 'POST'])
def CenterCostDelete():
    if request.method == 'POST':
        data = request.values
        return delete(CenterCost, data)

