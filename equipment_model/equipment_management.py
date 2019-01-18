import xlwt
from flask import Blueprint, render_template
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
    EquipmentWork, EletronicBatchDataStore, SpareStock, EquipmentMaintenanceKnowledge, EquipmentFailureReporting, \
    EquipmentMaintain, \
    SchedulePlan, SparePartInStockManagement, SparePartStock, Area, Instruments, MaintenanceStatus, MaintenanceCycle, \
    EquipmentRunRecord, \
    EquipmentRunPUID, EquipmentMaintenanceStore, SpareTypeStore
from sqlalchemy import create_engine, Column, ForeignKey, Table, Integer, String, and_, or_, desc,extract
from io import StringIO
import calendar
from Model.system import CenterCost
from tools.common import logger,insertSyslog,insert,delete,update,select

engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

equip = Blueprint('equip', __name__)



# 设备建模
@equip.route('/Pequipment')
def pequipment():
    ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
    data = []
    for tu in ID:
        li = list(tu)
        id = li[0]
        name = li[1]
        processUnit_id = {'ID': id, 'text': name}
        data.append(processUnit_id)
    return render_template('equipmentModel.html', ProcessUnit_id=data)

# 设备详细信息
@equip.route('/Equipment')
def equipment():
    ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
    data = []
    for tu in ID:
        li = list(tu)
        id = li[0]
        name = li[1]
        processUnit_id = {'ID': id, 'text':name}
        data.append(processUnit_id)
    oclasss = db_session.query(CenterCost.ID, CenterCost.CenterCostNum).all()
    data1 = []
    for tu in oclasss:
        li = list(tu)
        id = li[0]
        name = li[1]
        pro_unit_id = {'ID': id, 'text': name}
        data1.append(pro_unit_id)
    return render_template('sysEquipment.html', ProcessUnit_id=data, dic=data1)

# 设备建模查询
@equip.route('/equipmentModel/pequipmentFind', methods=['POST', 'GET'])
def pequipmentFind():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                EQPName = data['EQPName']  # 设备名称
                if(EQPName == "" or EQPName == None):
                    total = db_session.query(Equipment).count()
                    pequipments = db_session.query(Equipment).all()[inipage:endpage]
                else:
                    total = db_session.query(Equipment).filter(Equipment.EQPName.like("%" + EQPName + "%")).count()
                    pequipments = db_session.query(Equipment).filter(Equipment.EQPName.like("%" + EQPName + "%")).all()[inipage:endpage]
                jsonpequipments = json.dumps(pequipments, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonpequipments + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备建模查询报错Error：" + str(e), current_user.Name)

# 设备建模增加
@equip.route('/equipmentModel/pequipmentCreate', methods=['POST', 'GET'])
def pequipmentCreate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(
                    Model.core.Equipment(
                        EQPCode=data['EQPCode'],
                        EQPName=data['EQPName'],
                        PUID=data['PUID'],
                        Desc=data['Desc']))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
            insertSyslog("error", "设备建模增加报错Error：" + str(e), current_user.Name)

# 设备建模修改
@equip.route('/equipmentModel/pequipmentUpdate', methods=['POST', 'GET'])
def pequipmentUpdate():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                id = int(data['ID'])
                oclass = db_session.query(Equipment).filter_by(ID=id).first()
                oclass.EQPCode=data['EQPCode']
                oclass.EQPName=data['EQPName']
                oclass.PUID=data['PUID']
                oclass.Desc=data['Desc']
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)
            insertSyslog("error", "设备建模修改报错Error：" + str(e), current_user.Name)

# 设备建模删除
@equip.route('/equipmentModel/pequipmentDelete', methods=['POST', 'GET'])
def pequipmentDelete():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    # for subkey in list(key):
                    id = int(key)
                    try:
                        oclass = db_session.query(Equipment).filter_by(ID=id).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
            insertSyslog("error", "设备建模删除报错Error：" + str(e), current_user.Name)



@equip.route('/allEquipments/Find')
def EquipmentsFind():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                EQPName = data['EQPName']  # 设备名称
                if (EQPName == "" or EQPName == None):
                    total = db_session.query(Equipment).count()
                    pequipments = db_session.query(Equipment).all()[inipage:endpage]
                else:
                    total = db_session.query(Equipment).filter(Equipment.EQPName.like("%" + EQPName + "%")).count()
                    pequipments = db_session.query(Equipment).filter(
                        Equipment.EQPName.like("%" + EQPName + "%")).all()[inipage:endpage]
                jsonpequipments = json.dumps(pequipments, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonpequipments + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备建模查询报错Error：" + str(e), current_user.Name)


# role更新数据，通过传入的json数据，解析之后进行相应更新
@equip.route('/allEquipments/Update', methods=['POST', 'GET'])
def allEquipmentsUpdate():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentUpdate")
        re = EquipmentIFS.allEquipmentsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@equip.route('/allEquipments/Delete', methods=['POST', 'GET'])
def allEquipmentsDelete():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentDelete")
        re = EquipmentIFS.allEquipmentsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@equip.route('/allEquipments/Create', methods=['POST', 'GET'])
def allEquipmentsCreate():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentCreate")
        re = EquipmentIFS.allEquipmentsCreate(data)
        return re


@equip.route('/allEquipments/Search', methods=['POST', 'GET'])
def allEquipmentsSearch():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentSearch")
        re = EquipmentIFS.allEquipmentsSearch(data)
        return re
# 备件出入库管理
@equip.route('/sparePartInStockManagement', methods=['POST', 'GET'])
def sparePartInStockManagement():
    oclass = db_session.query(SpareTypeStore.ID,SpareTypeStore.SpareTypeName).all()
    dic = []
    for i in oclass:
        lis = list(i)
        dic.append({"ID":lis[0],"SpareTypeName":lis[1]})
    return render_template('sparePartInStockManagement.html',dic=dic)

# 备件库查询
@equip.route('/spareStockSearch', methods=['POST', 'GET'])
def spareStockSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                SpareName = "%" + data["SpareName"] + "%"
                if data["SpareName"] == "":
                    RoleNames = db_session.query(User.RoleName).filter(User.Name == current_user.Name).all()
                    rolename = ""
                    for name in RoleNames:
                        if name[0] == "备件审核人":
                            rolename = "备件审核人"
                        if name[0] == "系统管理员":
                            rolename = "系统管理员"
                    if rolename == "备件审核人":
                        spareCount = db_session.query(SpareStock).filter(
                            SpareStock.SpareStatus.in_((Model.Global.SpareStatus.OutStock.value,Model.Global.SpareStatus.InStock.value))).count()
                        spareClass = db_session.query(SpareStock).filter(
                            SpareStock.SpareStatus.in_((Model.Global.SpareStatus.OutStock.value,Model.Global.SpareStatus.InStock.value))).order_by(
                            desc("InStockDate"))[inipage:endpage]
                    else:
                        spareCount = db_session.query(SpareStock).filter().count()
                        spareClass = db_session.query(SpareStock).filter().order_by(desc("InStockDate"))[inipage:endpage]
                else:
                    spareCount = db_session.query(SpareStock).filter(SpareStock.SpareName.like(SpareName)).count()
                    spareClass = db_session.query(SpareStock).filter(SpareStock.SpareName.like(SpareName)).order_by(desc("InStockDate"))[inipage:endpage]
                jsonoclass = json.dumps(spareClass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(spareCount) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件库查询报错Error：" + str(e), current_user.Name)
            return json.dumps("备件库查询报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

# 备件库存查询
@equip.route('/spareStockSearchEchis', methods=['POST', 'GET'])
def spareStockSearchEchis():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                SpareName = data["SpareName"]
                if data["SpareName"] == "":
                    return "请输入要查询的备件名！"
                spareCount = db_session.query(SpareStock).filter(SpareStock.SpareName == SpareName).count()
                return json.dumps(spareCount, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件库存查询报错Error：" + str(e), current_user.Name)
            return json.dumps("备件库存查询报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

# 备件新增
@equip.route('/spareStockCreate', methods=['POST', 'GET'])
def spareStockCreate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                RoleName = db_session.query(User.RoleName).filter(User.WorkNumber == current_user.WorkNumber).first()[0]
                if RoleName != "备件录入人" and RoleName != "系统管理员":
                    return "此用户没有新增备件权限！"
                SpareCode = data["SpareCode"]
                SpareStockclass = db_session.query(SpareStock).filter(SpareStock.SpareCode == SpareCode).first()
                if SpareStockclass != None:
                    return "备件编码重复！"
                spareStock = SpareStock()
                spareStock.SpareCode = SpareCode
                spareStock.SpareName = data["SpareName"]
                spareStock.SpareStatus = Model.Global.SpareStatus.InStock.value
                spareStock.SpareModel = data["SpareModel"]
                spareStock.SpareFactory = data["SpareFactory"]
                spareStock.SpareType = data["SpareType"]
                spareStock.SparePower = data["SparePower"]
                spareStock.Description = data["Description"]
                spareStock.ProductionDate = data["ProductionDate"]
                spareStock.StockUseStatus = data["StockUseStatus"]
                spareStock.ProductionDate = data["ProductionDate"]
                spareStock.CreateDate = datetime.datetime.now()
                spareStock.InStockPeople = current_user.Name
                db_session.add(spareStock)
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件新增报错Error：" + str(e), current_user.Name)
            return json.dumps("备件新增报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#备件编辑
@equip.route('/spareStockUpdate', methods=['POST', 'GET'])
def spareStockUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                RoleName = db_session.query(User.RoleName).filter(User.WorkNumber == current_user.WorkNumber).first()[0]
                if RoleName != "备件录入人" and RoleName != "系统管理员":
                    return "此用户没有修改备件权限！"
                ID = int(data['ID'])
                oclass = db_session.query(SpareStock).filter_by(ID=ID).first()
                oclass.SpareCode = data["SpareCode"]
                SpareStockclass = db_session.query(SpareStock).filter(SpareStock.SpareCode == oclass.SpareCode).first()
                if SpareStockclass != None:
                    if SpareStockclass.ID != ID:
                        return "备件编码重复！"
                oclass.SpareName = data["SpareName"]
                oclass.SpareModel = data["SpareModel"]
                oclass.SpareFactory = data["SpareFactory"]
                oclass.SpareType = data["SpareType"]
                oclass.SparePower = data["SparePower"]
                oclass.Description = data["Description"]
                oclass.ProductionDate = data["ProductionDate"]
                oclass.StockUseStatus = data["StockUseStatus"]
                oclass.ProductionDate = data["ProductionDate"]
                db_session.add(oclass)
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件编辑报错Error：" + str(e), current_user.Name)
            return json.dumps("备件编辑报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

#备件删除
@equip.route('/spareStockDelete', methods=['POST', 'GET'])
def spareStockDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                RoleName = db_session.query(User.RoleName).filter(User.WorkNumber == current_user.WorkNumber).first()[0]
                if RoleName != "备件录入人" and RoleName != "系统管理员":
                    return "此用户没有删除备件权限！"
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(SpareStock).filter_by(ID=ID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("备件删除报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件删除报错Error：" + str(e), current_user.Name)
            return json.dumps("备件删除报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

# 备件入库出库
@equip.route('/spareStockInOut', methods=['POST', 'GET'])
def spareStockInOut():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                RoleName = db_session.query(User.RoleName).filter(User.WorkNumber == current_user.WorkNumber).first()[0]
                if RoleName != "备件录入人" and RoleName != "系统管理员":
                    return "此用户没有备件入库出库权限！"
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(SpareStock).filter_by(ID=ID).first()
                        if oclass.SpareStatus == Model.Global.SpareStatus.New.value:
                            oclass.SpareStatus = Model.Global.SpareStatus.InStock.value
                        elif oclass.SpareStatus == Model.Global.SpareStatus.InStockChecked.value:
                            oclass.SpareStatus = Model.Global.SpareStatus.OutStock.value
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("备件入库出库报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件入库出库报错Error：" + str(e), current_user.Name)
            return json.dumps("备件入库出库报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 备件入库出库审核
@equip.route('/spareStockChecked', methods=['POST', 'GET'])
def spareStockChecked():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                RoleName = db_session.query(User.RoleName).filter(User.WorkNumber == current_user.WorkNumber).first()[0]
                if RoleName != "备件审核人" and RoleName != "系统管理员":
                    return "此用户没有备件入库出库审核权限！"
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(SpareStock).filter_by(ID=ID).first()
                        if oclass.SpareStatus == Model.Global.SpareStatus.InStock.value:
                            oclass.SpareStatus = Model.Global.SpareStatus.InStockChecked.value
                        elif oclass.SpareStatus == Model.Global.SpareStatus.OutStock.value:
                            oclass.SpareStatus = Model.Global.SpareStatus.OutStockChecked.value
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("备件入库出库审核报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件入库出库审核报错Error：" + str(e), current_user.Name)
            return json.dumps("备件入库出库审核报错", cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

# 备件入库出库审核撤回
@equip.route('/spareStockCheckRecall', methods=['POST', 'GET'])
def spareStockCheckRecall():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                RoleName = db_session.query(User.RoleName).filter(User.WorkNumber == current_user.WorkNumber).first()[0]
                if RoleName != "备件审核人" and RoleName != "系统管理员":
                    return "此用户没有备件入库出库审核撤回权限！"
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(SpareStock).filter_by(ID=ID).first()
                        if oclass.SpareStatus == Model.Global.SpareStatus.InStock.value:
                            oclass.SpareStatus = Model.Global.SpareStatus.New.value
                        elif oclass.SpareStatus == Model.Global.SpareStatus.OutStock.value:
                            oclass.SpareStatus = Model.Global.SpareStatus.InStockChecked.value
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("备件入库出库审核撤回报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件入库出库审核撤回报错Error：" + str(e), current_user.Name)
            return json.dumps("备件入库出库审核撤回报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 制定检修计划
@equip.route('/EqpMaintainCreate', methods=['POST', 'GET'])
def EqpMaintainCreate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                SpareCode = data["SpareCode"]
                SpareStockclass = db_session.query(SpareStock).filter(SpareStock.SpareCode == SpareCode).first()
                if SpareStockclass != None:
                    return "备件编码重复！"
                spareStock = SpareStock()
                spareStock.SpareCode = SpareCode
                spareStock.SpareName = data["SpareName"]
                spareStock.SpareStatus = Model.Global.SpareStatus.InStock.value
                spareStock.SpareModel = data["SpareModel"]
                spareStock.SpareFactory = data["SpareFactory"]
                spareStock.SpareType = data["SpareType"]
                spareStock.SparePower = data["SparePower"]
                spareStock.Description = data["Description"]
                spareStock.ProductionDate = data["ProductionDate"]
                spareStock.StockUseStatus = data["StockUseStatus"]
                spareStock.ProductionDate = data["ProductionDate"]
                spareStock.CreateDate = datetime.datetime.now()
                spareStock.InStockPeople = current_user.Name
                db_session.add(spareStock)
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "制定检修计划报错Error：" + str(e), current_user.Name)
            return json.dumps("制定检修计划报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 操作手册
@equip.route('/CreateOperationManual', methods=['POST', 'GET'])
def CreateOperationManual():
    if request.method == "GET":
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                ManualName = data['ManualName']
                ManualFile = data['ManualFile']
                book = xlwt.Workbook(encoding='utf-8')
                print(ManualFile)
                bb = re.findall(r'.{7}', ManualFile)
                print(bb)
                aa = ""
                [chr(i) for i in [int(b, 2) for b in ManualFile.split(' ')]]
                for b in bb:
                    aa += chr(int(b, 2))
                print(aa)
                output = StringIO.StringIO(aa)
                book.save(output)
                response = make_response(output.getvalue())
                response.headers['Content-Type'] = 'application/vnd.ms-excel'
                response.headers['Content-Disposition'] = 'attachment; filename=' + ManualName + '.doc'
                output.closed
                return response
                ManualName = data['ManualName']
                ManualFile = data['ManualFile']
                print(ManualFile)
                bb = re.findall(r'.{7}', ManualFile)
                print(bb)
                String = []
                # String = ManualFile.split(" ")
                aa = ""
                for b in bb:
                    aa += chr(int(b, 2))
                print(aa)
                # print(A.encode(encoding="utf-8").decode(encoding="utf-8"))
                file = open('D:/Temp/' + ManualName + '.doc', 'wr')
                file.write(aa.encode(encoding="utf-8").decode(encoding="utf-8"))
                file.closed
                # response = make_response(aa.getvalue())
                # response.headers['Content-Type'] = 'application/vnd.ms-excel'
                # response.headers['Content-Disposition'] = 'attachment; filename=' + ManualName + '.xls'
                # Description = data['Description']
                # Type = data['Type']
                # UploadDate = datetime.datetime.now()
                # db_session.add(OperationManual(ManualName = ManualName,ManualFile = ManualFile,Description = Description,Type = Type,UploadDate = UploadDate))
                # db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "创建操作手册报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

def getMonthFirstDayAndLastDay(year, month):
    """
    :param year: 年份，默认是本年，可传int或str类型
    :param month: 月份，默认是本月，可传int或str类型
    :return: firstDay: 当月的第一天，datetime.date类型
              lastDay: 当月的最后一天，datetime.date类型
    """
    if year:
        year = int(year)
    else:
        year = datetime.date.today().year

    if month:
        month = int(month)
    else:
        month = datetime.date.today().month

    # 获取当月第一天的星期和当月的总天数
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)

    # 获取当月的第一天
    firstDay = datetime.date(year=year, month=month, day=1)
    lastDay = datetime.date(year=year, month=month, day=monthRange)
    return firstDay, lastDay

# 设备运行记录查询
@equip.route('/equipmentRunSearch', methods=['POST', 'GET'])
def equipmentRunCountSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                # pages = int(data['page'])
                # rowsnumber = int(data['rows'])
                # inipage = (pages - 1) * rowsnumber + 0
                # endpage = (pages - 1) * rowsnumber + rowsnumber
                EQPName = data["EQPName"]
                data = request.values
                InputDate = data["InputDate"]
                InputDate = InputDate.split("-")
                re = getMonthFirstDayAndLastDay(InputDate[0],InputDate[1])
                if EQPName == "":
                    equipmentRunCount = db_session.query(EquipmentRunRecord).filter(EquipmentRunRecord.CreateDate.between(re[0],re[1])).count()
                    equipmentRunClass = db_session.query(EquipmentRunRecord).filter(EquipmentRunRecord.CreateDate.between(re[0],re[1])).order_by(desc("InputDate")).all()
                else:
                    equipmentRunCount = db_session.query(EquipmentRunRecord).filter(EquipmentRunRecord.EQPName == EQPName,EquipmentRunRecord.CreateDate.between(re[0],re[1])).count()
                    equipmentRunClass = db_session.query(EquipmentRunRecord).filter(
                        EquipmentRunRecord.EQPName == EQPName,
                        EquipmentRunRecord.CreateDate.between(re[0], re[1])).order_by(desc("InputDate")).all()
                RunDates = 0
                ClearDates = 0
                FailureDates = 0
                for ee in equipmentRunClass:
                    RunDates += ee.RunDate
                    ClearDates += ee.ClearDate
                    FailureDates += ee.FailureDate
                sz = []
                dir = {}
                dir["Classes"] = "合计："
                dir["RunDate"] = RunDates
                dir["ClearDate"] = ClearDates
                dir["FailureDate"] = FailureDates
                sz.append(dir)
                sz = json.dumps(sz, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = json.dumps(equipmentRunClass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(equipmentRunCount) + ',"rows"' + ":\n" + jsonoclass + ',"footer"' + ":\n" + sz +"}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备运行记录查询报错Error：" + str(e), current_user.Name)
            return json.dumps("设备运行记录查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
# 设备运行记录添加
@equip.route('/equipmentRunRecordCreate', methods=['POST', 'GET'])
def equipmentRunRecordCreate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                EQPName = data["EQPName"]
                ocal = db_session.query(EquipmentRunPUID).filter(EquipmentRunPUID.EQPName == EQPName).first()
                equipmentRunRecord = EquipmentRunRecord()
                equipmentRunRecord.Workshop = "江中罗亭生产车间"
                equipmentRunRecord.PUIDName = ocal.PUIDName
                equipmentRunRecord.EQPName = EQPName
                equipmentRunRecord.EQPCode = ocal.EQPCode
                equipmentRunRecord.InputDate = data["InputDate"]
                equipmentRunRecord.Classes = data["Classes"]
                equipmentRunRecord.RunDate = intkong(data["RunDate"])
                equipmentRunRecord.ClearDate = intkong(data["ClearDate"])
                equipmentRunRecord.FailureDate = intkong(data["FailureDate"])
                equipmentRunRecord.OperatePeople = data["OperatePeople"]
                equipmentRunRecord.BrandName1 = data["BrandName1"]
                equipmentRunRecord.BatchID1 = data["BatchID1"]
                equipmentRunRecord.BrandName2 = data["BrandName2"]
                equipmentRunRecord.BatchID2 = data["BatchID2"]
                equipmentRunRecord.CreateDate = datetime.datetime.now()
                db_session.add(equipmentRunRecord)
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备运行记录添加报错Error：" + str(e), current_user.Name)
            return json.dumps("设备运行记录添加报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
def intkong(args):
    isFloat = ""
    try:
        float(args)
    except:
        isFloat = False
    else:
        isFloat = True
    if isFloat == True:
        return float(args)
    else:
        return 0

# 设备运行记录修改
@equip.route('/equipmentRunRecordUpdate', methods=['POST', 'GET'])
def equipmentRunRecordUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data["ID"]
                oclass = db_session.query(EquipmentRunRecord).filter(EquipmentRunRecord.ID == ID).first()
                oclass.InputDate = data["InputDate"]
                oclass.Classes = data["Classes"]
                oclass.RunDate = intkong(data["RunDate"])
                oclass.ClearDate = intkong(data["ClearDate"])
                oclass.FailureDate = intkong(data["FailureDate"])
                oclass.OperatePeople = data["OperatePeople"]
                oclass.BrandName1 = data["BrandName1"]
                oclass.BatchID1 = data["BatchID1"]
                oclass.BrandName2 = data["BrandName2"]
                oclass.BatchID2 = data["BatchID2"]
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备运行总记录修改报错Error：" + str(e), current_user.Name)
            return json.dumps("设备运行总记录修改报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备运行记录删除
@equip.route('/equipmentRunRecordDelete', methods=['POST', 'GET'])
def equipmentRunRecordDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(EquipmentRunRecord).filter_by(ID=ID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("设备运行记录删除报错", cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备运行记录删除报错Error：" + str(e), current_user.Name)
            return json.dumps("设备运行记录删除报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备故障报修查询
@equip.route('/EquipmentFailureReportingSearch', methods=['POST', 'GET'])
def EquipmentFailureReportingSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                FailureReportingNum = data["FailureReportingNum"]
                if FailureReportingNum == "":
                    EquipmentFailureReportingCount = db_session.query(EquipmentFailureReporting).filter_by().count()
                    EquipmentFailureReportingClass = db_session.query(EquipmentFailureReporting).filter_by().all()[inipage:endpage]
                else:
                    EquipmentFailureReportingCount = db_session.query(EquipmentFailureReporting).filter(EquipmentFailureReporting.FailureReportingNum == FailureReportingNum).count()
                    EquipmentFailureReportingClass = db_session.query(EquipmentFailureReporting).filter(
                        EquipmentFailureReporting.FailureReportingNum == FailureReportingNum).all()[inipage:endpage]
                jsonoclass = json.dumps(EquipmentFailureReportingClass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(EquipmentFailureReportingCount) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备故障报修查询报错Error：" + str(e), current_user.Name)
            return json.dumps("设备故障报修查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备故障报修添加
@equip.route('/EquipmentFailureReportingCreate', methods=['POST', 'GET'])
def EquipmentFailureReportingCreate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                failureReporting = EquipmentFailureReporting()
                failureReporting.FailureReportingNum = data["FailureReportingNum"]
                failureReporting.FailureReportingType = data["FailureReportingType"]
                failureReporting.EQPName = data["EQPName"]
                failureReporting.ReportingBeginDate = datetime.datetime.now()
                failureReporting.FailureBeginDate = datetime.datetime.strptime(data["FailureBeginDate"],'%Y-%m-%d %H:%M:%S')
                failureReporting.ReportingStatus = Model.Global.ReportingStatus.New.value
                failureReporting.FailureReportingDesc = data["FailureReportingDesc"]
                failureReporting.NewPeople = current_user.Name
                db_session.add(failureReporting)
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备故障报修添加报错Error：" + str(e), current_user.Name)
            return json.dumps("设备故障报修添加加报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备故障报修修改
@equip.route('/EquipmentFailureReportingUpdate', methods=['POST', 'GET'])
def EquipmentFailureReportingUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data["ID"]
                oclass = db_session.query(EquipmentFailureReporting).filter(
                    EquipmentFailureReporting.ID == ID).first()
                oclass.FailureReportingNum = data["FailureReportingNum"]
                oclass.FailureReportingType = data["FailureReportingType"]
                oclass.EQPName = data["EQPName"]
                oclass.FailureBeginDate = datetime.datetime.strptime(data["FailureBeginDate"],'%Y-%m-%d %H:%M:%S')
                oclass.FailureReportingDesc = data["FailureReportingDesc"]
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备故障报修修报错Error：" + str(e), current_user.Name)
            return json.dumps("设备故障报修修改报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备故障报修处理
@equip.route('/EquipmentFailureReportingHandle', methods=['POST', 'GET'])
def EquipmentFailureReportingHandle():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(EquipmentFailureReporting).filter(
                            EquipmentFailureReporting.ID == ID).first()
                        if oclass.ReportingStatus == Model.Global.ReportingStatus.Confirm.value or oclass.ReportingStatus == Model.Global.ReportingStatus.Handle.value:
                            return "此报修单号已被处理，请选择未处理的维修单！"
                        oclass.ReportingStatus = Model.Global.ReportingStatus.Handle.value
                        oclass.HandlePeople = current_user.Name
                        db_session.commit()
                        return 'OK'
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("设备故障报修处理报错", cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备故障报修处理报错Error：" + str(e), current_user.Name)
            return json.dumps("设备故障报修处理报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备故障报修确认
@equip.route('/EquipmentFailureReportingConfirm', methods=['POST', 'GET'])
def EquipmentFailureReportingConfirm():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data["ID"]
                oclass = db_session.query(EquipmentFailureReporting).filter(
                    EquipmentFailureReporting.ID == ID).first()
                oclass.ActualBeginDate = datetime.datetime.strptime(data["ActualBeginDate"],'%Y-%m-%d %H:%M:%S')
                oclass.ActualEndDate = datetime.datetime.strptime(data["ActualEndDate"],'%Y-%m-%d %H:%M:%S')
                oclass.Description = data["Description"]
                oclass.ReportingStatus = Model.Global.ReportingStatus.Confirm.value
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备故障报修确认报错Error：" + str(e), current_user.Name)
            return json.dumps("设备故障报修确认报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备故障报修删除
@equip.route('/EquipmentFailureReportingDelete', methods=['POST', 'GET'])
def EquipmentFailureReportingDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(EquipmentFailureReporting).filter_by(ID=ID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("设备故障报修删除报错", cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备故障报修删除报错Error：" + str(e), current_user.Name)
            return json.dumps("设备故障报修删除报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备检修计划查询
@equip.route('/EquipmentMaintainSearch', methods=['POST', 'GET'])
def EquipmentMaintainSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                MaintainPlanNum = data["MaintainPlanNum"]
                if MaintainPlanNum == "":
                    EquipmentFailureReportingCount = db_session.query(
                        EquipmentMaintain).filter_by().count()
                    EquipmentFailureReportingClass = db_session.query(
                        EquipmentMaintain).filter_by().all()[inipage:endpage]
                else:
                    EquipmentFailureReportingCount = db_session.query(EquipmentMaintain).filter(
                        EquipmentMaintain.MaintainPlanNum == MaintainPlanNum).count()
                    EquipmentFailureReportingClass = db_session.query(EquipmentMaintain).filter(
                        EquipmentMaintain.MaintainPlanNum == MaintainPlanNum).all()[
                                                     inipage:endpage]
                jsonoclass = json.dumps(EquipmentFailureReportingClass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(
                    EquipmentFailureReportingCount) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备故障报修查询报错Error：" + str(e), current_user.Name)
            return json.dumps("设备故障报修查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 制定检修计划
@equip.route('/EquipmentMaintainCreate', methods=['POST', 'GET'])
def EquipmentMaintainCreate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                maintain = EquipmentMaintain()
                maintain.MaintainPlanNum = data["MaintainPlanNum"]
                maintain.MaintainType = data["MaintainType"]
                maintain.EquipmentName = data["EquipmentName"]
                maintain.PlanBeginDate = datetime.datetime.now()
                maintain.MaintainDemand = data["MaintainDemand"]
                maintain.MaintainStatus = Model.Global.MaintainStatus.New.value
                maintain.Description = data["Description"]
                maintain.MakePlanPeople = current_user.Name
                db_session.add(maintain)
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "制定检修计划报错Error：" + str(e), current_user.Name)
            return json.dumps("制定检修计划报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 制定检修计划修改
@equip.route('/EquipmentMaintainUpdate', methods=['POST', 'GET'])
def EquipmentMaintainUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data["ID"]
                oclass = db_session.query(EquipmentMaintain).filter(
                    EquipmentMaintain.ID == ID).first()
                oclass.MaintainPlanNum = data["MaintainPlanNum"]
                oclass.MaintainType = data["MaintainType"]
                oclass.EquipmentName = data["EquipmentName"]
                oclass.MaintainDemand = data["MaintainDemand"]
                oclass.Description = data["Description"]
                db_session.commit()
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "制定检修计划修改报错Error：" + str(e), current_user.Name)
            return json.dumps("制定检修计划修改报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 制定检修计划删除
@equip.route('/EquipmentMaintainDelete', methods=['POST', 'GET'])
def EquipmentMaintainDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(EquipmentMaintain).filter_by(ID=ID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("制定检修计划删除报错", cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "制定检修计划删除报错Error：" + str(e), current_user.Name)
            return json.dumps("制定检修计划删除报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 检修计划审核
@equip.route('/EquipmentMaintainCheck', methods=['POST', 'GET'])
def EquipmentMaintainCheck():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(EquipmentMaintain).filter(
                            EquipmentMaintain.ID == ID).first()
                        if oclass.MaintainStatus != Model.Global.MaintainStatus.New.value:
                            return "此计划单号已审核，请选择未审核的检修单！"
                        oclass.MaintainStatus = Model.Global.MaintainStatus.Checked.value
                        oclass.CheckPeople = current_user.Name
                        db_session.commit()
                        return 'OK'
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("制定检修计划审核报错", cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "制定检修计划审核报错Error：" + str(e), current_user.Name)
            return json.dumps("制定检修计划审核报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 检修计划确认
@equip.route('/EquipmentMaintainFinished', methods=['POST', 'GET'])
def EquipmentMaintainFinished():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(EquipmentMaintain).filter(
                            EquipmentMaintain.ID == ID).first()
                        oclass.MaintainStatus = Model.Global.MaintainStatus.Finished.value
                        oclass.FinishedPeople = current_user.Name
                        oclass.PlanEndDate = datetime.datetime.now()
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps("检修计划确认报错", cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "检修计划确认报错Error：" + str(e), current_user.Name)
            return json.dumps("检修计划确认报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


# 设备维护
@equip.route('/equipmentMaintain')
def equipmentMaintain():
    RoleNames = db_session.query(User.RoleName).filter(User.Name == current_user.Name).all()
    rolename = ""
    for name in RoleNames:
        if name[0] == "设备管理部审核人":
            rolename = "设备管理部审核人"
        if name[0] == "设备部技术人员":
            rolename = "设备部技术人员"
        if name[0] == "系统管理员":
            rolename = "系统管理员"
    return render_template('equipmentMaintain.html', rolename=rolename)

# 设备运行数据
@equip.route('/EquipmentManage/runData')
def EquipmentManageRunData():
    return render_template('EquipmentManageRunData.html')
# 设备运行记录
@equip.route('/equipmentOperateRecord')
def equipmentOperateRecord():
    return render_template('equipmentOperateRecord.html')
# 设备运行记录获取树形列表
@equip.route('/quipmentRunPUIDParent', methods=['POST', 'GET'])
def quipmentRunPUIDParent():
    if request.method == 'GET':
        data = request.values
        try:
            data = getMyEquipmentRunPUIDChildren(id=0)
            return json.dumps(data)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备运行记录获取树形列表报错Error：" + str(e), current_user.Name)
            return json.dumps("设备运行记录获取树形列表报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
def getMyEquipmentRunPUIDChildren(id):
    sz = []
    try:
        orgs = db_session.query(EquipmentRunPUID).filter(EquipmentRunPUID.ParentNode == id).all()
        for obj in orgs:
            if obj.ParentNode != 0 and obj.ParentNode != 1:
                sz.append({"id": obj.ID, "text": obj.EQPName, "state": "open","children": []})
            else:
                sz.append({"id": obj.ID, "text": obj.EQPName, "state": "closed","children": getMyEquipmentRunPUIDChildren(obj.ID)})
        return sz
    except Exception as e:
        print(e)
        return json.dumps("设备运行记录获取树形列表", cls=AlchemyEncoder, ensure_ascii=False)

# 备件管理
@equip.route('/equipmentspare')
def equipmentbeij():
    return render_template('equipmentspare.html')

# 故障管理
@equip.route('/equipmenttrouble')
def equipmenttrouble():
    RoleNames = db_session.query(User.RoleName).filter(User.Name == current_user.Name).all()
    rolename = ""
    for name in RoleNames:
        if name[0] == "操作人":
            rolename = "操作人"
        if name[0] == "设备部技术人员":
            rolename = "设备部技术人员"
        if name[0] == "系统管理员":
            rolename = "系统管理员"
    return render_template('equipmenttrouble.html',rolename=rolename)

# 设备保养记录存储
@equip.route('/EquipmentMaintenance/DataStore')
def MaintenanceDataStore():
    if request.method == 'GET':
        try:
            data = request.values.to_dict()
            if data is not None:
                clear_value = data['clear']
                clear_value = eval(clear_value)
                wipe_value = data['wipe']
                wipe_value = eval(wipe_value)
                confirm_value = data['confirm']
                confirm_value = eval(confirm_value)
                date = datetime.datetime.now()
                name = eval(data['name'])[0]
                type = eval(data['type'])[0]
                number = eval(data['number'])[0]
                PersonLiable = eval(data['PersonLiable'])[0]
                SuperVisor = eval(data['SuperVisor'])[0]
                lubrication = 1 if eval(data['lubrication'])[0] == "true" else 0

                if 'lubrication' in data.keys():
                    lub = db_session.query(EquipmentMaintenanceStore).filter(and_(
                        EquipmentMaintenanceStore.EquipentName == name,
                        EquipmentMaintenanceStore.EquipmentNumber == number,
                        EquipmentMaintenanceStore.Content == "电机加油",
                        extract("year", EquipmentMaintenanceStore.OperationDate) == int(date.year),
                        extract("month", EquipmentMaintenanceStore.OperationDate) == int(date.month))).first()
                    if lub:
                        lub.OperationValue = lubrication
                        db_session.commit()
                    else:
                        oclass = EquipmentMaintenanceStore()
                        oclass.EquipmentType = type
                        oclass.EquipentName = name
                        oclass.EquipmentNumber = number
                        oclass.Content = "电机加油"
                        oclass.OperationValue = data['lubrication']
                        oclass.Date = datetime.datetime.now()
                        oclass.PersonLiable = PersonLiable
                        oclass.SuperVisor = SuperVisor
                        oclass.OperationDate = datetime.datetime.now()
                        db_session.add(oclass)
                        db_session.commit()
                date_1 = 1
                for clear in clear_value:
                    if clear_value == 'null':
                        continue
                    clear_obj = db_session.query(EquipmentMaintenanceStore).filter(and_(
                        EquipmentMaintenanceStore.EquipentName == name,
                        EquipmentMaintenanceStore.EquipmentNumber == number,
                        EquipmentMaintenanceStore.Date == date_1,
                        EquipmentMaintenanceStore.Content == "周围环境",
                        extract("year", EquipmentMaintenanceStore.OperationDate) == int(date.year),
                        extract("month", EquipmentMaintenanceStore.OperationDate) == int(date.month))).first()
                    if clear_obj:
                        clear_obj.OperationValue = int(clear)
                        db_session.commit()
                    else:
                        oclass = EquipmentMaintenanceStore()
                        oclass.EquipmentType = type
                        oclass.EquipentName = name
                        oclass.EquipmentNumber = number
                        oclass.Content = "周围环境"
                        oclass.OperationValue = eval(clear)
                        oclass.Date = date_1
                        oclass.PersonLiable = PersonLiable
                        oclass.SuperVisor = SuperVisor
                        oclass.OperationDate = datetime.datetime.now()
                        db_session.add(oclass)
                        db_session.commit()
                    date_1 += 1
                date_2 = 1
                for wipe in wipe_value:
                    wipe_obj = db_session.query(EquipmentMaintenanceStore).filter(and_(
                        EquipmentMaintenanceStore.EquipentName == name,
                        EquipmentMaintenanceStore.EquipmentNumber == number,
                        EquipmentMaintenanceStore.Date == date_2,
                        EquipmentMaintenanceStore.Content == "机外表面擦油",
                        extract("year", EquipmentMaintenanceStore.OperationDate) == int(date.year),
                        extract("month", EquipmentMaintenanceStore.OperationDate) == int(date.month))).first()
                    if wipe_obj:
                        wipe_obj.OperationValue = int(wipe)
                        db_session.commit()
                    else:
                        oclass = EquipmentMaintenanceStore()
                        oclass.EquipmentType = type
                        oclass.EquipentName = name
                        oclass.EquipmentNumber = number
                        oclass.Content = "机外表面擦油"
                        oclass.OperationValue = eval(wipe)
                        oclass.Date = date_2
                        oclass.PersonLiable = PersonLiable
                        oclass.SuperVisor = SuperVisor
                        oclass.OperationDate = datetime.datetime.now()
                        db_session.add(oclass)
                        db_session.commit()
                    date_2 += 1
                date_3 = 1
                for confirm in confirm_value:
                    confirm_obj = db_session.query(EquipmentMaintenanceStore).filter(and_(
                        EquipmentMaintenanceStore.EquipentName == name,
                        EquipmentMaintenanceStore.EquipmentNumber == number,
                        EquipmentMaintenanceStore.Date == date_3,
                        EquipmentMaintenanceStore.Content == "保养签章",
                        extract("year", EquipmentMaintenanceStore.OperationDate) == int(date.year),
                        extract("month", EquipmentMaintenanceStore.OperationDate) == int(date.month))).first()
                    if confirm_obj:
                        confirm_obj.OperationValue = int(confirm)
                        db_session.commit()
                    else:
                        oclass = EquipmentMaintenanceStore()
                        oclass.EquipmentType = type
                        oclass.EquipentName = name
                        oclass.EquipmentNumber = number
                        oclass.Content = "保养签章"
                        oclass.OperationValue = eval(confirm)
                        oclass.Date = date_3
                        oclass.PersonLiable = PersonLiable
                        oclass.SuperVisor = SuperVisor
                        oclass.OperationDate = datetime.datetime.now()
                        db_session.add(oclass)
                        db_session.commit()
                    date_3 += 1
                return "OK"
            return "NO"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备保养记录数据存储报错Error：" + str(e), current_user.Name)
            return json.dumps("设备保养记录数据存储报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


# 设备保养记录查询
@equip.route('/EquipmentMaintenance/Search')
def MaintenanceDataSearch():
    if request.method == 'GET':
        try:
            data = request.values
            name = data['name']
            type = data['type']
            time = data['date'].split('-')
            if name is None or type is None or time is None:
                return "NO"
            oclass = db_session.query(EquipmentMaintenanceStore).filter(and_(
                EquipmentMaintenanceStore.EquipentName == name,
                EquipmentMaintenanceStore.EquipmentType == type,
                extract("year",EquipmentMaintenanceStore.OperationDate)== time[0],
                extract("month", EquipmentMaintenanceStore.OperationDate)== time[1])).first()
            number = oclass.EquipmentNumber
            PersonLiable = oclass.PersonLiable
            SuperVisor = oclass.SuperVisor
            clear = db_session.query(EquipmentMaintenanceStore.OperationValue).filter(and_(
                EquipmentMaintenanceStore.EquipentName == name,
                EquipmentMaintenanceStore.EquipmentType == type,
                EquipmentMaintenanceStore.Content == "周围环境",
                extract("year", EquipmentMaintenanceStore.OperationDate) == time[0],
                extract("month", EquipmentMaintenanceStore.OperationDate) == time[1])).all()
            clear = [cl[0] for cl in clear]

            wipe = db_session.query(EquipmentMaintenanceStore.OperationValue).filter(and_(
                EquipmentMaintenanceStore.EquipentName == name,
                EquipmentMaintenanceStore.EquipmentType == type,
                EquipmentMaintenanceStore.Content == "机外表面擦油",
                extract("year", EquipmentMaintenanceStore.OperationDate) == time[0],
                extract("month", EquipmentMaintenanceStore.OperationDate) == time[1])).all()
            wipe = [wi[0] for wi in wipe]

            confirm = db_session.query(EquipmentMaintenanceStore.OperationValue).filter(and_(
                EquipmentMaintenanceStore.EquipentName == name,
                EquipmentMaintenanceStore.EquipmentType == type,
                EquipmentMaintenanceStore.Content == "保养签章",
                extract("year", EquipmentMaintenanceStore.OperationDate) == time[0],
                extract("month", EquipmentMaintenanceStore.OperationDate) == time[1])).all()
            confirm = [con[0] for con in confirm]

            lubrication = db_session.query(EquipmentMaintenanceStore.OperationValue).filter(and_(
                extract("year", EquipmentMaintenanceStore.OperationDate) == time[0],
                extract("month", EquipmentMaintenanceStore.OperationDate) == time[1],
                EquipmentMaintenanceStore.EquipentName == name,
                EquipmentMaintenanceStore.EquipmentType == type,
                EquipmentMaintenanceStore.Content == "电机加油")).order_by(desc("Date")).first()[0]

            equip_data = {"EQPNumber":number, "personLiable":PersonLiable,
                          "supervisor":SuperVisor, "clear":clear,
                          "wipe":wipe, "confirm":confirm, "lubrication":lubrication}
            return json.dumps(equip_data,cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备保养记录数据查询报错Error：" + str(e), current_user.Name)
            return json.dumps("设备保养记录数据查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 设备日常保养记录
@equip.route('/EMaintainEveryDay')
def EMaintainEveryDay():
    return render_template('EMaintainEveryDay.html')

@equip.route('/EquipmentManage/runDataChart')
def runDataChart():
    if request.method == 'GET':
        try:
            data = request.values
            equip = data['equip']
            date = data['date']
            if equip != None and date != None:
                year_month = date.split('-')
                firstDay,lastDay = getMonthFirstDayAndLastDay(year_month[0], year_month[1])
                objects = db_session.query(EquipmentRunRecord).filter(
                    EquipmentRunRecord.EQPName == equip,
                    EquipmentRunRecord.CreateDate.between(firstDay,lastDay)).all()
                if objects:
                    objects = sorted(objects, key=lambda obj: obj.InputDate)
                    time_list = list()
                    run_time = list()
                    error_time = list()
                    clear_time = list()
                    for obj in objects:
                        run_time.append(obj.RunDate)
                        clear_time.append(obj.ClearDate)
                        error_time.append(obj.FailureDate)
                        time_list.append(obj.InputDate)
                else:
                    return "NO"
                year_error_time = list()
                year_run_time = list()
                for month in range(1,13):
                    month_data = db_session.query(EquipmentRunRecord).filter(and_(
                        EquipmentRunRecord.EQPName == equip,
                        extract('year', EquipmentRunRecord.CreateDate) == year_month[0],
                        extract('month', EquipmentRunRecord.CreateDate) == month)).all()
                    if len(month_data) > 0:
                        year_run_time.append(sum([i.RunDate for i in month_data]))
                        year_error_time.append(sum([i.FailureDate for i in month_data]))
                    else:
                        year_run_time.append(0)
                        year_error_time.append(0)
                data_list = [{"run_time": run_time, "clear_time": clear_time,
                              "error_time": error_time, 'time': time_list,
                              "year_run_time":year_run_time, "year_error_time":year_error_time}]
                return json.dumps(data_list, cls=AlchemyEncoder, ensure_ascii=False)
            return "NO"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备运行-图表数据获取报错Error：" + str(e), current_user.Name)
            return json.dumps("设备运行-图表数据获取报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#备件类型页面跳转
@equip.route('/equipment_model/SpareTypeStorePage')
def SpareTypeStorePage():
    return render_template("SpareTypeStorePage.html")

#备件类型查询
@equip.route('/equipment_model/SpareTypeStoreSelect', methods=['GET', 'POST'])
def SpareTypeStoreSelect():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                SpareTypeName = data["SpareTypeName"]
                if SpareTypeName == "":
                    SpareTypeStoreCount = db_session.query(SpareTypeStore).filter_by().count()
                    SpareTypeStoreClass = db_session.query(SpareTypeStore).filter_by().all()[inipage:endpage]
                else:
                    SpareTypeStoreCount = db_session.query(SpareTypeStore).filter(
                        SpareTypeStore.SpareTypeName.like("%"+SpareTypeName+"%")).count()
                    SpareTypeStoreClass = db_session.query(SpareTypeStore).filter(
                        SpareTypeStore.SpareTypeName.like("%"+SpareTypeName+"%")).all()[inipage:endpage]
                jsonoclass = json.dumps(SpareTypeStoreClass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(SpareTypeStoreCount) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "备件类型查询报错Error：" + str(e), current_user.Name)
            return json.dumps("备件类型查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#备件类型增加
@equip.route('/equipment_model/SpareTypeStoreCreate', methods=['GET', 'POST'])
def SpareTypeStoreCreate():
    if request.method == 'POST':
        data = request.values
        return insert(SpareTypeStore, data)

#备件类型修改
@equip.route('/equipment_model/SpareTypeStoreUpdate', methods=['GET', 'POST'])
def SpareTypeStoreUpdate():
    if request.method == 'POST':
        data = request.values
        return update(SpareTypeStore, data)

#备件类型删除
@equip.route('/equipment_model/SpareTypeStoreDetele', methods=['GET', 'POST'])
def SpareTypeStoreDetele():
    if request.method == 'POST':
        data = request.values
        return delete(SpareTypeStore, data)


#成本中心页面跳转
@equip.route('/equipment_model/CenterCostPage')
def CenterCostPage():
    return render_template('CenterCostPage.html')

#成本中心查询
@equip.route('/equipment_model/CenterCostSelect', methods=['GET', 'POST'])
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
                    CenterCostCount = db_session.query(CenterCost).filter_by().count()
                    CenterCostClass = db_session.query(CenterCost).filter_by().all()[inipage:endpage]
                else:
                    CenterCostCount = db_session.query(CenterCost).filter(
                        CenterCost.CharityPerson.like("%"+CharityPerson+"%")).count()
                    CenterCostClass = db_session.query(CenterCost).filter(
                        CenterCost.CharityPerson.like("%"+CharityPerson+"%")).all()[inipage:endpage]
                jsonoclass = json.dumps(CenterCostClass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(CenterCostCount) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "成本中心查询报错Error：" + str(e), current_user.Name)
            return json.dumps("成本中心查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#成本中心增加
@equip.route('/equipment_model/CenterCostCreate', methods=['GET', 'POST'])
def CenterCostCreate():
    if request.method == 'POST':
        data = request.values
        return insert(CenterCost, data)

#成本中心修改
@equip.route('/equipment_model/CenterCostUpdate', methods=['GET', 'POST'])
def CenterCostUpdate():
    if request.method == 'POST':
        data = request.values
        return update(CenterCost, data)

#成本中心删除
@equip.route('/equipment_model/CenterCostDelete', methods=['GET', 'POST'])
def CenterCostDelete():
    if request.method == 'POST':
        data = request.values
        return delete(CenterCost, data)

# 设备类型库存树形列表
@equip.route('/equipment_model/spareStoreTree', methods=['POST', 'GET'])
def spareStoreTree():
    if request.method == 'GET':
        data = request.values
        try:
            data = getSpareStoreTree(id=0)
            return json.dumps(data)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备类型库存树形列表报错Error：" + str(e), current_user.Name)
            return json.dumps("设备类型库存树形列表报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
def getSpareStoreTree(id):
    sz = []
    try:
        orgs = db_session.query(SpareTypeStore).filter(SpareTypeStore.ParentNode == id).all()
        for obj in orgs:
            if obj.ParentNode != 0 and obj.ParentNode != 1:
                sz.append({"id": obj.ID, "text": obj.SpareTypeName, "state": "open","children": []})
            else:
                sz.append({"id": obj.ID, "text": obj.SpareTypeName, "state": "closed","children": getSpareStoreTree(obj.ID)})
        return sz
    except Exception as e:
        print(e)
        return json.dumps("设备类型库存树形列表报错", cls=AlchemyEncoder, ensure_ascii=False)

#设备库存柱状图
@equip.route('/equipment_model/spareStoreEcharts', methods=['GET', 'POST'])
def spareStoreEcharts():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                dir = {}
                dlistn = []
                dlistc = []
                SpareTypeName = data["SpareTypeName"]
                if SpareTypeName == "" or SpareTypeName == None:
                    return "请选择设备类型！"
                else:
                    oclassSpare = db_session.query(SpareStock.SpareName).distinct().filter(SpareStock.SpareType.like("%"+SpareTypeName+"%"), SpareStock.SpareStatus==Model.Global.SpareStatus.InStockChecked.value).all()
                    for name in oclassSpare:
                        dlistn.append(name)
                        count = db_session.query(SpareStock).filter(SpareStock.SpareName.like("%"+name[0]+"%"), SpareStock.SpareStatus==Model.Global.SpareStatus.InStockChecked.value).count()
                        dlistc.append(count)
                dir["name"] = dlistn
                dir["count"] = dlistc
                print(dir)
                return json.dumps(dir, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "设备库存柱状图查询报错Error：" + str(e), current_user.Name)
            return json.dumps("设备库存柱状图查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
