import json
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from flask_login import current_user
import Model
from Model.core import SysLog
from tools.MESLogger import MESLogger
import socket
import datetime
from Model.BSFramwork import AlchemyEncoder
import re
from Model.core import Enterprise, Area, Factory, ProductLine, ProcessUnit, Equipment, Material, MaterialType, \
    ProductUnit, ProductRule, ZYTask, ZYPlanMaterial, ZYPlan, Unit, PlanManager, SchedulePlan, ProductControlTask, \
    OpcServer, Pequipment, WorkFlowStatus, WorkFlowEventZYPlan, WorkFlowEventPlan, \
    OpcTag, CollectParamsTemplate, CollectParams, Collectionstrategy, CollectTask, \
    CollectTaskCollection, ReadyWork, NodeIdNote, ProductUnitRoute, ProductionMonitor, NewZYPlanMaterial, \
    QualityControlTree
from Model.system import Role, Organization, User, Menu, Role_Menu, BatchMaterielBalance, OperationManual, NewReadyWork, \
    EquipmentWork, EletronicBatchDataStore, SpareStock, EquipmentMaintenanceKnowledge, EquipmentMaintain, \
    SchedulePlan, SparePartInStockManagement, SparePartStock, Area, Instruments, MaintenanceStatus, MaintenanceCycle, \
    plantCalendarScheduling
from Model.system import User, EquipmentRunPUID, ElectronicBatch, EquipmentRunRecord, QualityControl, PackMaterial, \
    TypeCollection, OperationProcedure, EquipmentMaintenanceStore, Scheduling, SchedulingStock, ERPproductcode_prname, \
    SchedulingStandard, product_plan, SchedulingMaterial, YieldMaintain, ZYPlanWMS, ElectronicBatchTwo, PartiallyProducts
from Model.system import Role, Organization, User, Menu, Role_Menu, BatchMaterielBalance, OperationManual, NewReadyWork, \
    EquipmentWork, EletronicBatchDataStore, SpareStock, EquipmentMaintenanceKnowledge, EquipmentReportingRecord, \
    EquipmentMaintain, \
    SchedulePlan, SparePartInStockManagement, SparePartStock, Area, Instruments, MaintenanceStatus, MaintenanceCycle, \
    EquipmentRunRecord, \
    EquipmentRunPUID, EquipmentMaintenanceStore, SpareTypeStore, ElectronicBatch, EquipmentStatusCount, Shifts, \
    EquipmentTimeStatisticTree, SystemEQPCode, EquipmentManagementManua, EquipmentMaintenanceStandard


engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

logger = MESLogger('../logs', 'log')
#插入日志OperationType OperationContent OperationDate UserName ComputerName IP
def insertSyslog(operationType, operationContent, userName):
        try:
            if operationType == None: operationType = ""
            if operationContent == None:
                operationContent = ""
            else:
                operationContent = str(operationContent)
            if userName == None: userName = ""
            ComputerName = socket.gethostname()
            db_session.add(
                SysLog(OperationType=operationType, OperationContent=operationContent,OperationDate=datetime.datetime.now(), UserName=userName,
                       ComputerName=ComputerName, IP=socket.gethostbyname(ComputerName)))
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)

def insert(tablename, data):
    '''
    :param tablename: 要进行插入数据的model
    :param insert_dict: 要进行插入的数据，数据类型为dict，key为model的字段属性，value为要插入的值
    :return: 返回json信息，包含status，message
    '''
    if hasattr(tablename, '__tablename__'):
        oclass = tablename()
        if isinstance(data, dict) and len(data) > 0:
            try:
                # if "ID" in data.keys():
                #     popdata = data.pop("ID")
                for key in data:
                    if key != "ID":
                        setattr(oclass, key, data[key])
                db_session.add(oclass)
                db_session.commit()
                return 'OK'
            except Exception as e:
                print(e)
                db_session.rollback()
                logger.error(e)
                insertSyslog("error", "%s数据添加报错："%tablename + str(e), current_user.Name)
                return json.dumps('数据添加失败！')

def delete(tablename, delete_data):
    '''
    :param tablename: 要进行删除信息的model
    :param recv_data: 要进行更新的数据，数据类型为list，list中的每个元素为需要删除的每条记录的ID
    :return: 返回json信息，包含status，message
    '''
    if hasattr(tablename, '__tablename__'):
        try:
            jsonstr = json.dumps(delete_data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(tablename).filter_by(ID=id).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        insertSyslog("error", "删除户ID为"+str(id)+"报错Error：" + str(ee), current_user.Name)
                        return json.dumps("删除用户报错", cls=AlchemyEncoder,ensure_ascii=False)
                return 'OK'
        except Exception as e:
            db_session.rollback()
            logger.error(e)
            insertSyslog("error", "%s数据删除报错："%tablename + str(e), current_user.Name)
            return json.dumps('数据删除失败！')

def update(tablename, new_data):
    '''
    :param tablename:要进行更新的model
    :param new_data: 要进行更新的数据，数据类型为dict，key为model的字段属性，value为要更新的值
    :return: 返回json信息，包含status，message
    '''
    if hasattr(tablename, '__tablename__'):
        if isinstance(new_data, dict) and len(new_data) > 0:
            try:
                oclass = db_session.query(tablename).filter(tablename.ID==new_data['ID']).first()
                if oclass:
                    for key in new_data:
                        if hasattr(oclass, key) and key != 'ID':
                            setattr(oclass, key, new_data[key])
                    db_session.add(oclass)
                    db_session.commit()
                    return 'OK'
                else:
                    return json.dumps('当前记录不存在！', cls=AlchemyEncoder, ensure_ascii=False)
            except Exception as e:
                db_session.rollback()
                logger.error(e)
                insertSyslog("error", "%s数据更新报错："%tablename + str(e), current_user.Name)
                return json.dumps('数据更新失败！', cls=AlchemyEncoder, ensure_ascii=False)

def select(table, offset, limit, param):
    '''
    :param tablename: 查询表
    :param pages: 页数
    :param rowsnumber: 一页多少行
    :param fieid: 查询字段
    :param param: 查询条件
    :return: 
    '''
    from sqlalchemy import MetaData, create_engine
    metadata = MetaData()
    from sqlalchemy import Table
    try:
        pages = int(offset)
        rowsnumber = int(limit)
        inipage = pages * rowsnumber + 0
        endpage = pages * rowsnumber + rowsnumber
        if (param == "" or param == None):
            total = db_session.query(table).count()
            oclass = db_session.query(table).all()[inipage:endpage]
        else:
            newTable = Table(table, metadata, autoload=True, autoload_with=engine)
            total = db_session.query(table).filter(newTable.columns._data[param] == param.value()).count()
            oclass = db_session.query(table).filter(newTable.columns._data[param] == param.get(param)).all()[inipage:endpage]
        jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
        jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        return jsonoclass
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "查询报错Error：" + str(e), current_user.Name)
