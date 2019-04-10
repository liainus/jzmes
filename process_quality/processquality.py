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
        data = request.values  # 返回请求中的参数和form
        try:
            data_dict = {"BatchID": data['BatchID'],
                         "content": data['content'],
                         "OperationPeople": current_user.Name,
                         "Description": data['Description'],
                         "OperationDate":datetime.datetime.now()}
            return insert(ProcessQuality, data_dict)
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

@Process.route('/process_quality/ProcessqualityReview', methods=['GET', 'POST'])
def ProcessqualityReview():
    '''
    工艺质量审核人确认流程
    :return:
    '''

# post方法：上传文件的
@Process.route('/process_quality/ProcessQualityPDFUpload', methods=['post'])
def ProcessQualityPDFUpload():
    fname = request.files.get('file')  #获取上传的文件
    if fname:
        new_fname = r'process_quality/upload/' + fname.filename
        fname.save(new_fname)  #保存文件到指定路径
        data_dict = {"Name": fname.filename,
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
dirpath = os.path.join(Process.root_path,'upload')
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

