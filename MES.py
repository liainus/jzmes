# coding:utf8
import datetime
import decimal
import json
import os
import re
import string
from io import StringIO
import time
from collections import Counter

import redis
import xlwt
from flask import Flask, jsonify, redirect, url_for, flash
import xlrd
from flask import Flask, jsonify, redirect, url_for
from flask import render_template, request, make_response
from flask import session
from sqlalchemy import create_engine, Column, ForeignKey, Table, Integer, String, and_, or_, desc
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
import Model.Global
from Model.BSFramwork import AlchemyEncoder
from Model.core import Enterprise, Area, Factory, ProductLine, ProcessUnit, Equipment, Material, MaterialType, \
    ProductUnit, ProductRule, ZYTask, ZYPlanMaterial, ZYPlan, Unit, PlanManager, SchedulePlan, ProductControlTask, \
    OpcServer, Pequipment, WorkFlowStatus, WorkFlowEventZYPlan, WorkFlowEventPlan, \
    OpcTag, CollectParamsTemplate, CollectParams, Collectionstrategy, CollectTask, \
    CollectTaskCollection, ReadyWork, NodeIdNote, ProductUnitRoute, ProductionMonitor, NewZYPlanMaterial
from Model.system import Role, Organization, User, Menu, Role_Menu, BatchMaterielBalance, OperationManual, NewReadyWork, EquipmentWork
from tools.MESLogger import MESLogger
from Model.core import SysLog
from sqlalchemy import func
import string
import re
from collections import Counter
from Model.system import User, OperationProcedure, ElectronicBatch, QualityControl, PackMaterial, TypeCollection
from Model.Global import WeightUnit
from Model.control import ctrlPlan
from flask_login import LoginManager, current_user
from flask.ext.login import login_required, logout_user, login_user
import socket
from opcua import Client
from Model.dynamic_model import make_dynamic_classes
import Model.node
from threading import Timer
from constant import constant
#flask_login的初始化
login_manager = LoginManager()
login_manager.db_session_protection = 'strong'
login_manager.login_view ='login'

# 获取本文件名实例化一个flask对象
app = Flask(__name__)
app.config['SECRET_KEY'] = 'qeqhqiqd131'
login_manager.init_app(app)


engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()
logger = MESLogger('../logs', 'log')

# 存储
def store(data):
    # 调用__enter__函数，该函数把返回值传给变量json_file
    with open('data.json', encoding='gbk') as json_file:
        # 将python数据进行json编码并写入json文件对象中
        json_file.write(json.dumps(data))  # 该语句结束后执行__exit__，它将对异常进行监控和处理


# 重写load
def load():
    with open('D:\Python\JZMES\MicroMES\static\data\datagrid_organization.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data


'''登录'''
@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter_by(id=int(user_id)).first()

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('login.html')
        if request.method == 'POST':
            data = request.values
            work_number = data['WorkNumber']
            password = data['password']
                # 验证账户与密码
            user = db_session.query(User).filter_by(WorkNumber=work_number).first()
            if user and user.confirm_password(password):
                login_user(user)  # login_user(user)调用user_loader()把用户设置到db_session中
                # 查询用户当前菜单权限
                roles = db_session.query(User.RoleName).filter_by(WorkNumber=work_number).all()
                menus = []
                for role in roles:
                    for index in role:
                        role_id = db_session.query(Role.ID).filter_by(RoleName=index).first()
                        menu = db_session.query(Menu.ModuleCode).join(Role_Menu, isouter=True).filter_by(Role_ID=role_id).all()
                        for li in menu:
                            menus.append(li[0])
                session['menus'] = menus
                return redirect('/')
            # 认证失败返回登录页面
            error = '用户名或密码错误'
            return render_template('login.html', error=error)
    except Exception as e:
        db_session.rollback()
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 退出登录
# 使用login_required装饰路由函数,未登录的请求将会跳转到上面login_manger.login_view设置的登录页面路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



# 系统日志
@app.route('/syslogs')
def syslogs():
    return render_template('syslogs.html')

# 日志查询
@app.route('/syslogs/findByDate')
def syslogsFindByDate():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                startTime = data['startTime']  # 开始时间
                endTime = data['endTime']  # 结束时间
                if startTime == "" and endTime == "":
                    total = db_session.query(SysLog).count()
                    syslogs = db_session.query(SysLog).order_by(desc("OperationDate")).all()[inipage:endpage]
                elif startTime != "" and endTime == "":
                    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    total = db_session.query(SysLog).filter(SysLog.OperationDate.between(startTime, nowTime)).count()
                    syslogs = db_session.query(SysLog).filter(SysLog.OperationDate.between(startTime, nowTime)).order_by(desc("OperationDate"))[
                              inipage:endpage]
                else:
                    total = db_session.query(SysLog).filter(SysLog.OperationDate.between(startTime, endTime)).count()
                    syslogs = db_session.query(SysLog).filter(SysLog.OperationDate.between(startTime, endTime)).order_by(desc("OperationDate"))[
                              inipage:endpage]
                jsonsyslogs = json.dumps(syslogs, cls=AlchemyEncoder, ensure_ascii=False)
                jsonsyslogs = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonsyslogs + "}"
                return jsonsyslogs
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

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

# 用户管理
@app.route('/userManager')
def userManager():
    departments = db_session.query(Organization.ID, Organization.OrganizationName).all()
    # print(departments)
    # departments = json.dumps(departments, cls=AlchemyEncoder, ensure_ascii=False)
    data = []
    for tu in departments:
        li = list(tu)
        id = li[0]
        name = li[1]
        department = {'OrganizationID':id,'OrganizationName':name}
        data.append(department)

    dataRoleName = []
    roleNames = db_session.query(Role.ID, Role.RoleName).all()
    for role in roleNames:
        li = list(role)
        id = li[0]
        name = li[1]
        roleName = {'RoleID': id, 'RoleName': name}
        dataRoleName.append(roleName)
    return render_template('userManager.html',departments=data,roleNames=dataRoleName)


@app.route('/MyUser/Select')
def MyUserSelect():
    if request.method == 'GET':
        odata = request.values
        try:
            json_str = json.dumps(odata.to_dict())
            if len(json_str) > 10:
                pages = int(odata['page'])  # 页数
                rowsnumber = int(odata['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                id = odata['id']
                Name = odata['Name']
                if id != '':
                    OrganizationCodeData = db_session.query(Organization).filter_by(id=id).first()
                    if OrganizationCodeData != None:
                        OrganizationName = str(OrganizationCodeData.OrganizationName)
                        total = db_session.query(User).filter(and_(User.OrganizationName.like("%" + OrganizationName + "%") if OrganizationName is not None else "",
                                                           User.Name.like("%" + Name + "%") if Name is not None else "")).count()
                        oclass = db_session.query(User).filter(and_(User.OrganizationName.like("%" + OrganizationName + "%") if OrganizationName is not None else "",
                                                           User.Name.like("%" + Name + "%") if Name is not None else ""))[inipage:endpage]
                    else:
                        total = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").count()
                        oclass = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "")[inipage:endpage]
                else:
                    total = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").count()
                    oclass = db_session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "")[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
            return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询用户列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)



@app.route('/user/addUser', methods=['POST', 'GET'])
def addUser():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                user = User()
                user.Name=data['Name']
                user.Password=user.password(data['Password'])
                # print(user.Password)
                user.WorkNumber=data['WorkNumber']
                user.Status="1" # 登录状态先设置一个默认值1：已登录，0：未登录
                user.Creater=data['Creater']
                user.CreateTime=datetime.datetime.now()
                user.LastLoginTime=datetime.datetime.now()
                user.IsLock='false' # data['IsLock'],
                user.OrganizationName=data['OrganizationName']
                user.RoleName=data['RoleName']
                db_session.add(user)
                db_session.commit()
                insertSyslog("添加用户", "添加用户"+data['Name']+"添加成功", current_user.Name)
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "添加用户报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/user/updateUser', methods=['POST', 'GET'])
def UpdateUser():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                id = int(data['id'])
                user = db_session.query(User).filter_by(id=id).first()
                user.Name = data['Name']
                user.Password = data['Password']
                user.Password = user.password(data['Password'])
                # user.Status = data['Status']
                user.Creater = data['Creater']
                # user.CreateTime = data['CreateTime']
                # user.LastLoginTime = data['LastLoginTime']
                # user.IsLock = data['IsLock']
                user.OrganizationName = data['OrganizationName']
                db_session.commit()
                insertSyslog("success", "更新用户" + data['Name'] + "成功", current_user.Name)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "更新用户报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/user/deleteUser', methods=['POST', 'GET'])
def deleteUser():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(User).filter_by(id=id).first()
                        db_session.delete(oclass)
                        db_session.commit()
                        insertSyslog("success", "删除ID是" + string(id) + "的用户删除成功", current_user.Name)
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        insertSyslog("error", "删除户ID为"+string(id)+"报错Error：" + string(ee), current_user.Name)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "删除用户报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 权限分配
@app.route('/roleright')
def roleright():
    return render_template('roleRight.html')

# 角色列表树形图
def getRoleList(id=0):
    sz = []
    try:
        roles = db_session.query(Role).filter().all()
        for obj in roles:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID,
                           "text": obj.RoleName,
                           "children": getRoleList(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'

        return sz
    except Exception as e:
        print(e)
        insertSyslog("error", "查询角色报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 权限分配下的角色列表
@app.route('/Permission/SelectRoles')
def SelectRoles():
    if request.method == 'GET':
        try:
            data = getRoleList(id=0)
            # organizations = db_session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询权限分配下的角色列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 权限分配下的用户列表
@app.route('/permission/userlist')
def userList():
    # 获取用户列表
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        # 默认返回所有用户
        ID = data['ID']
        if ID == '':
            try:
                json_str = json.dumps(data.to_dict())
                if len(json_str) > 10:
                    pages = int(data['page'])  # 页数
                    rowsnumber = int(data['rows'])  # 行数
                    inipage = (pages - 1) * rowsnumber + 0  # 起始页
                    endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                    total = db_session.query(User).count()
                    users_data = db_session.query(User)[inipage:endpage]
                    # ORM模型转换json格式
                    jsonusers = json.dumps(users_data, cls=AlchemyEncoder, ensure_ascii=False)
                    jsonusers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonusers + "}"
                    return jsonusers.encode("utf8")
            except Exception as e:
                print(e)
                logger.error(e)
                insertSyslog("error", "查询权限分配下的用户列表报错Error：" + str(e), current_user.Name)
                return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
        if ID != '':
            data = request.values  # 返回请求中的参数和form
            try:
                json_str = json.dumps(data.to_dict())
                if len(json_str) > 10:
                    pages = int(data['page'])  # 页数
                    rowsnumber = int(data['rows'])  # 行数
                    inipage = (pages - 1) * rowsnumber + 0  # 起始页
                    endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                    # 通过角色ID获取当前角色对应的用户
                    role_id = data['ID']
                    role_name= db_session.query(Role.RoleName).filter_by(ID=role_id).first()
                    if role_name is None:  # 判断当前角色是否存在
                        return
                    total = db_session.query(User).filter_by(RoleName=role_name).count()
                    users_data = db_session.query(User).filter_by(RoleName=role_name).all()[
                                 inipage:endpage]
                    # ORM模型转换json格式
                    jsonusers = json.dumps(users_data, cls=AlchemyEncoder, ensure_ascii=False)
                    jsonusers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonusers + "}"
                    return jsonusers
            except Exception as e:
                print(e)
                logger.error(e)
                insertSyslog("error", "通过点击角色查询用户报错Error：" + str(e), current_user.Name)
                return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

def trueOrFalse(obj,role_menus):
    if str(obj.ModuleName) in role_menus:
        return True
    return False

# 权限分配下的功能模块列表
def getMenuList(role_menus, id=0):
    sz = []
    try:
        menus = db_session.query(Menu).filter_by(ParentNode=id).all()
        for obj in menus:
            if obj.ParentNode == id:
                    sz.append({"id": obj.ID,
                               "text": obj.ModuleName,
                               "checked": trueOrFalse(obj, role_menus),
                               "children": getMenuList(role_menus, obj.ID)})
        return sz
    except Exception as e:
        print(e)
        insertSyslog("error", "查询权限分配下的功能模块列表Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载菜单列表
@app.route('/permission/menulist')
def menulist():
    if request.method == 'GET':
        role_data = request.values
        if 'id' not in role_data.keys():
            try:
                data = getMenuList(role_menus=[],id=0)
                jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
                return jsondata.encode("utf8")
            except Exception as e:
                print(e)
                logger.error(e)
                insertSyslog("error", "加载菜单列表Error：" + str(e), current_user.Name)
                return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
        id = role_data['id']
        try:
            role_menus = db_session.query(Menu.ModuleName).join(Role_Menu, isouter=True).filter_by(Role_ID=id).all()
            r_menus = []
            for menu in role_menus:
                r_menus.append(menu[0])
            menus_data = getMenuList(r_menus, id=0)
            jsondata = json.dumps(menus_data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "加载菜单列表Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 权限分配下为角色添加权限
@app.route('/permission/MenuToRole')
def menuToUser():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            # 获取菜单和用户并存入数据库
            role_id = data['role_id']  # 获取角色ID
            if role_id is None:
                return
            menus = db_session.query(Menu).join(Role_Menu, isouter=True).filter_by(Role_ID=id).all()
            if menus:
                db_session.delete(menus)
                db_session.commit()
            menu_id = data['menu_id'] # 获取菜单ID
            if menu_id is None:
                return
            menu_id = re.findall(r'\d+\.?\d*', menu_id)
            for r in menu_id:
                role = db_session.query(Role).filter_by(ID=role_id).first()
                menu = db_session.query(Menu).filter_by(ID=r).first()
                # 将菜单ID和角色ID存入User_Role
                menu.roles.append(role)
                db_session.add(menu)
                db_session.commit()
            # 存入数据库后跳转到权限分配页面
            return redirect(url_for("roleright"))
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "权限分配下为角色添加权限Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 批次管理
@app.route('/batchmanager')
def batchmanager():
    # productUnit_ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
    # data = []
    # for tu in productUnit_ID:
    #     li = list(tu)
    #     id = li[0]
    #     name = li[1]
    #     pro_unit_id = {'ID': id, 'text': name}
    #     data.append(pro_unit_id)
    return render_template('batch_manager.html')

#批次管理查询计划
@app.route('/batchManager/SearchBatchManager')
def SearchBatchManager():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                currentWorkdate = data["currentWorkdate"]
                PUID = data["PUID"]
                if(PUID == ""):
                    total = db_session.query(PlanManager).count()
                    zYPlans = db_session.query(PlanManager).order_by(desc("PlanBeginTime")).all()[inipage:endpage]
                else:
                    total = db_session.query(PlanManager).filter(PlanManager.PlanBeginTime == currentWorkdate, PlanManager.PUID == PUID).count()
                    zYPlans = db_session.query(PlanManager).filter(PlanManager.PlanBeginTime == currentWorkdate, PlanManager.PUID == PUID).order_by(desc("PlanBeginTime")).all()[inipage:endpage]
                jsonzyplans = json.dumps(zYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzyplans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonzyplans + "}"
                return jsonzyplans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "批次管理查询计划报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 批次管理查询计划明细
@app.route('/batchManager/SearchBatchZYPlan')
def SearchBatchZYPlan():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ID = data["ID"]
                PName = data["PName"]
                planMa = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                PUID = db_session.query(ProductUnitRoute.PUID).filter(ProductUnitRoute.PDUnitRouteName == PName, ProductUnitRoute.ProductRuleID == planMa.BrandID).first()
                total = db_session.query(ZYPlan.ID).filter(ZYPlan.BatchID == planMa.BatchID, ZYPlan.PUID == PUID[0]).count()
                zYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == planMa.BatchID, ZYPlan.PUID == PUID[0]).order_by(desc("EnterTime")).all()[
                          inipage:endpage]
                jsonzyplans = json.dumps(zYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzyplans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonzyplans + "}"
                return jsonzyplans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "批次管理查询计划明细报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 批次管理查询任务明细
@app.route('/batchManager/SearchBatchZYTask')
def SearchBatchZYTask():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ID = data["ID"]
                plan = db_session.query(ZYPlan).filter(ZYPlan.ID == ID).first()
                total = db_session.query(ZYTask.ID).filter(ZYTask.BatchID == plan.BatchID,
                                                           ZYTask.PUID == plan.PUID).count()
                zYPlans = db_session.query(ZYTask).filter(ZYTask.BatchID == plan.BatchID,
                                                          ZYTask.PUID == plan.PUID).order_by(
                    desc("EnterTime")).all()[
                          inipage:endpage]
                jsonzyplans = json.dumps(zYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzyplans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonzyplans + "}"
                return jsonzyplans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "批次管理查询任务明细报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 计划向导获取批次任务明细
@app.route('/ZYPlanGuid/CriticalTasks', methods=['POST', 'GET'])
def criticalTasks():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            print(json_str)
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ABatchID = data['ABatchID']
                total = db_session.query(ZYTask).filter(ZYTask.BatchID == ABatchID).count()
                zyTasks = db_session.query(ZYTask).filter(ZYTask.BatchID == ABatchID).all()[inipage:endpage]
                jsonzyTasks = json.dumps(zyTasks, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzyTasks = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonzyTasks + "}"
                return jsonzyTasks
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划向导获取批次任务明细报错Error：" + str(e), "AAAAAAadmin")
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载工作台
@app.route('/organizationMap')
def organizationMap():
    return render_template('index_organization.html')

@app.route('/organizationMap/selectAll')#组织结构
def selectAll():
    if request.method == 'GET':
        try:
            data = getMyOrganizationChildrenMap(id=0)
            jsondata = [{"name":"江中集团","value":"0","children":data}]
            jsondatas = json.dumps(jsondata, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondatas
        except Exception as e:
            print(e)
            insertSyslog("error", "查询组织结构报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
def getMyOrganizationChildrenMap(id):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            if obj.ParentNode == id:
                sz.append(
                    {"name": obj.OrganizationName, "value": obj.ID, "children": getMyOrganizationChildrenMap(obj.ID)})
        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
# 组织机构建模
# 加载工作台
@app.route('/organization')
def organization():
    return render_template('sysOrganization.html')


@app.route('/allOrganizations/Find')
def OrganizationsFind():
    if request.method == 'GET':
        data = request.values # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page']) # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages-1) * rowsnumber + rowsnumber #截止页
                total = db_session.query(func.count(Organization.ID)).scalar()
                organiztions = db_session.query(Organization).all()[inipage:endpage]
                #ORM模型转换json格式
                jsonorganzitions = json.dumps(organiztions, cls=AlchemyEncoder, ensure_ascii=False)
                jsonorganzitions = '{"total"'+":"+str(total)+',"rows"' +":\n" + jsonorganzitions + "}"
                return jsonorganzitions
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:"+ str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allOrganizations/Update', methods=['POST', 'GET'])
def allOrganizationsUpdate():
    if request.method == 'POST':

        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                organizationid = int(data['ID'])
                organization = db_session.query(Organization).filter_by(ID=organizationid).first()
                organization.OrganizationCode = data['OrganizationCode']
                organization.OrganizationName = data['OrganizationName']
                organization.ParentCode = data['ParentNode']
                organization.OrganizationSeq = data['OrganizationSeq']
                organization.Description = data['Description']
                organization.CreatePerson = data['CreatePerson']
                organization.CreateDate = data['CreateDate']
                organization.Img = data['Img']
                organization.Color = data['Color']
                db_session.commit()
                insertSyslog("success", "更新组织" + data['OrganizationName'] + "的组织更新成功", current_user.Name)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "更新组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allOrganizations/Delete', methods=['POST', 'GET'])
def allOrganizationsDelete():
    if request.method == 'POST':
        data = request.values
        try:
            #   jsonDict = data.to_dict(
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    # for subkey in list(key):
                    Organizationid = int(key)
                    try:
                        oclass = db_session.query(Organization).filter_by(ID=Organizationid).first()
                        db_session.delete(oclass)
                        db_session.commit()
                        insertSyslog("success", "删除组织ID为" + str(Organizationid) + "的组织删除成功", current_user.Name)
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        insertSyslog("error", "删除组织报错Error：" + str(ee), current_user.Name)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "删除组织报错Error：" + str(e), current_user.Name)
            # return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allOrganizations/Create', methods=['POST', 'GET'])
def allOrganizationsCreate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                if data['Img'] == "":
                    DspImg = "antonio.jpg"
                else:
                    DspImg = data['Img']

                if data['Color'] == "":
                    DspColor = "#1696d3"
                else:
                    DspColor = data['Color']
                db_session.add(
                    Organization(OrganizationCode=data['OrganizationCode'],
                                 OrganizationName=data['OrganizationName'],
                                 ParentNode=data['ParentNode'],
                                 OrganizationSeq=data['OrganizationSeq'],
                                 Description=data['Description'],
                                 CreatePerson=data['CreatePerson'],
                                 CreateDate=datetime.datetime.now(),Img = DspImg,Color = DspColor))
                db_session.commit()
                insertSyslog("success", "新增组织" + data['OrganizationName'] + "的组织新增成功", current_user.Name)
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "新增组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allOrganizations/Search', methods=['POST', 'GET'])
def allOrganizationsSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                strconditon = "%" + data['condition'] + "%"
                organizations = db_session.query(Organization).filter(Organization.OrganizationName.like(strconditon)).all()
                total = Counter(organizations)
                jsonorganizations = json.dumps(organizations, cls=AlchemyEncoder, ensure_ascii=False)
                jsonorganizations = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonorganizations + "}"
                return jsonorganizations
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询组织报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# @app.route('/allOrganizations/parentNode')
# def getParentNode():
#     if request.method == 'GET':
#         parentNode = db_session.query(Organization.ID, Organization.ParentNode).all()
#         print(parentNode)
#         data = []
#         for tu in parentNode:
#             li = list(tu)
#             node = li[0]
#             data.append(node)
#         parent_node = []
#         data = set(data)  #去除重复
#         for node in data:
#             text = {'text': node}
#             parent_node.append(text)
#         parentNode = json.dumps(parent_node, cls=AlchemyEncoder, ensure_ascii=False)
#         return parentNode

# 生产建模
# 加载工作台
@app.route('/Enterprise')
def enterprise():
    return render_template('sysEnterprise.html')


# 查找
@app.route('/allEnterprises/Find')
def EnterprisesFind():
    if request.method == 'GET':
        data = request.values
        EnterpriseIFS = Model.core.EnterpriseWebIFS("EnterpriseFind")
        re = EnterpriseIFS.EnterprisesFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allEnterprises/Update', methods=['POST', 'GET'])
def allEnterprisesUpdate():
    if request.method == 'POST':
        data = request.values
        EnterpriseIFS = Model.core.EnterpriseWebIFS("EnterpriseUpdate")
        re = EnterpriseIFS.allEnterprisesUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allEnterprises/Delete', methods=['POST', 'GET'])
def allEnterprisesDelete():
    if request.method == 'POST':
        data = request.values
        EnterpriseIFS = Model.core.EnterpriseWebIFS("EnterpriseDelete")
        re = EnterpriseIFS.allEnterprisesDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allEnterprises/Create', methods=['POST', 'GET'])
def allEnterprisesCreate():
    if request.method == 'POST':
        data = request.values
        EnterpriseIFS = Model.core.EnterpriseWebIFS("EnterpriseCreate")
        re = EnterpriseIFS.allEnterprisesCreate(data)
        return re

# 父节点树形结构图
def getOrganizationList(id=0):
    sz = []
    try:
        organizations = db_session.query(Organization).filter().all()
        for obj in organizations:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "text": obj.OrganizationName, "children": getOrganizationList(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'
        # data = string(sz)
        # data.replace(srep, '')

        return sz
    except Exception as e:
        print(e)
        insertSyslog("error", "查询组织树形结构报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 加载菜单列表
@app.route('/Enterprize/parentNode')
def parentNode():
    if request.method == 'GET':
        try:
            data = getEnterprizeList()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "加父级载菜单列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

def getEnterprizeList(id=0):
    sz = []
    try:
        enterprises = db_session.query(Enterprise).all()
        for obj in enterprises:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "text": obj.EnterpriseName, "children": getEnterprizeList(obj.ID)})
        return sz
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "加父级载菜单列表报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/allEnterprises/Search', methods=['POST', 'GET'])
def allEnterprisesSearch():
    if request.method == 'POST':
        data = request.values
        EnterpriseIFS = Model.core.EnterpriseWebIFS("EnterpriseSearch")
        re = EnterpriseIFS.allEnterprisesSearch(data)
        return re

        # 加载工作台


@app.route('/Factory')
def factory():
    return render_template('sysFactory.html')


@app.route('/allFactorys/Find')
def FactorysFind():
    if request.method == 'GET':
        data = request.values
        FactoryIFS = Model.core.FactoryWebIFS("FactoryFind")
        re = FactoryIFS.FactorysFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allFactorys/Update', methods=['POST', 'GET'])
def allFactorysUpdate():
    if request.method == 'POST':
        data = request.values
        FactoryIFS = Model.core.FactoryWebIFS("FactoryUpdate")
        re = FactoryIFS.allFactorysUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allFactorys/Delete', methods=['POST', 'GET'])
def allFactorysDelete():
    if request.method == 'POST':
        data = request.values
        FactoryIFS = Model.core.FactoryWebIFS("FactoryDelete")
        re = FactoryIFS.allFactorysDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allFactorys/Create', methods=['POST', 'GET'])
def allFactorysCreate():
    if request.method == 'POST':
        data = request.values
        FactoryIFS = Model.core.FactoryWebIFS("FactoryCreate")
        re = FactoryIFS.allFactorysCreate(data)
        return re


@app.route('/allFactorys/Search', methods=['POST', 'GET'])
def allFactorysSearch():
    if request.method == 'POST':
        data = request.values
        FactoryIFS = Model.core.FactoryWebIFS("FactorySearch")
        re = FactoryIFS.allFactorysSearch(data)
        return re


# 加载工作台
@app.route('/Area')
def getRootArea():
    return render_template('sysArea.html')


@app.route('/allAreas/Find')
def AreasFind():
    if request.method == 'GET':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaFind")
        re = AreaIFS.AreasFind(data)
        logger.info(re)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allAreas/Update', methods=['POST', 'GET'])
def allAreasUpdate():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaUpdate")
        re = AreaIFS.allAreasUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allAreas/Delete', methods=['POST', 'GET'])
def allAreasDelete():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaDelete")
        re = AreaIFS.allAreasDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allAreas/Create', methods=['POST', 'GET'])
def allAreasCreate():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaCreate")
        re = AreaIFS.allAreasCreate(data)
        return re


@app.route('/allAreas/Search', methods=['POST', 'GET'])
def allAreasSearch():
    if request.method == 'POST':
        data = request.values
        AreaIFS = Model.core.AreaWebIFS("AreaSearch")
        re = AreaIFS.allAreasSearch(data)
        return re

# 生产线
# 加载工作台
@app.route('/ProductLine')
def productLine():
    ID = db_session.query(Area.ID, Area.AreaName).all()
    data = []
    for tu in ID:
        li = list(tu)
        id = li[0]
        name = li[1]
        area_id = {'ID': id,'text':name}
        data.append(area_id)
    return render_template('sysProductLine.html', area_id=data)


@app.route('/allProductLines/Find')
def ProductLinesFind():
    if request.method == 'GET':
        data = request.values
        ProductLineIFS = Model.core.ProductLineWebIFS("ProductLineFind")
        re = ProductLineIFS.ProductLinesFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductLines/Update', methods=['POST', 'GET'])
def allProductLinesUpdate():
    if request.method == 'POST':
        data = request.values
        ProductLineIFS = Model.core.ProductLineWebIFS("ProductLineUpdate")
        re = ProductLineIFS.allProductLinesUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allProductLines/Delete', methods=['POST', 'GET'])
def allProductLinesDelete():
    if request.method == 'POST':
        data = request.values
        ProductLineIFS = Model.core.ProductLineWebIFS("ProductLineDelete")
        re = ProductLineIFS.allProductLinesDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductLines/Create', methods=['POST', 'GET'])
def allProductLinesCreate():
    if request.method == 'POST':
        data = request.values
        ProductLineIFS = Model.core.ProductLineWebIFS("ProductLineCreate")
        re = ProductLineIFS.allProductLinesCreate(data)
        return re


@app.route('/allProductLines/Search', methods=['POST', 'GET'])
def allProductLinesSearch():
    if request.method == 'POST':
        data = request.values
        ProductLineIFS = Model.core.ProductLineWebIFS("ProductLineSearch")
        re = ProductLineIFS.allProductLinesSearch(data)
        return re


# 加载工作台
@app.route('/ProcessUnit')
def processUnit():
    ID = db_session.query(ProductLine.ID, ProductLine.PLineName).all()
    data = []
    for tu in ID:
        li = list(tu)
        id = li[0]
        name = li[1]
        ProductLine_id = {'ID': id, 'text':name}
        data.append(ProductLine_id)
    return render_template('sysProcessUnit.html', productLine_id=data)


@app.route('/allProcessUnits/Find')
def ProcessUnitsFind():
    if request.method == 'GET':
        data = request.values
        ProcessUnitIFS = Model.core.ProcessUnitWebIFS("ProcessUnitFind")
        re = ProcessUnitIFS.ProcessUnitsFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProcessUnits/Update', methods=['POST', 'GET'])
def allProcessUnitsUpdate():
    if request.method == 'POST':
        data = request.values
        ProcessUnitIFS = Model.core.ProcessUnitWebIFS("ProcessUnitUpdate")
        re = ProcessUnitIFS.allProcessUnitsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allProcessUnits/Delete', methods=['POST', 'GET'])
def allProcessUnitsDelete():
    if request.method == 'POST':
        data = request.values
        ProcessUnitIFS = Model.core.ProcessUnitWebIFS("ProcessUnitDelete")
        re = ProcessUnitIFS.allProcessUnitsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProcessUnits/Create', methods=['POST', 'GET'])
def allProcessUnitsCreate():
    if request.method == 'POST':
        data = request.values
        ProcessUnitIFS = Model.core.ProcessUnitWebIFS("ProcessUnitCreate")
        re = ProcessUnitIFS.allProcessUnitsCreate(data)
        return re


@app.route('/allProcessUnits/Search', methods=['POST', 'GET'])
def allProcessUnitsSearch():
    if request.method == 'POST':
        data = request.values
        ProcessUnitIFS = Model.core.ProcessUnitWebIFS("ProcessUnitSearch")
        re = ProcessUnitIFS.allProcessUnitsSearch(data)
        return re

# 设备建模
@app.route('/Pequipment')
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

# 设备建模查询
@app.route('/equipmentModel/pequipmentFind', methods=['POST', 'GET'])
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
@app.route('/equipmentModel/pequipmentCreate', methods=['POST', 'GET'])
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
@app.route('/equipmentModel/pequipmentUpdate', methods=['POST', 'GET'])
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
@app.route('/equipmentModel/pequipmentDelete', methods=['POST', 'GET'])
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

# 设备详细信息
@app.route('/Equipment')
def equipment():
    ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
    data = []
    for tu in ID:
        li = list(tu)
        id = li[0]
        name = li[1]
        processUnit_id = {'ID': id, 'text':name}
        data.append(processUnit_id)
    return render_template('sysEquipment.html', ProcessUnit_id=data)


@app.route('/allEquipments/Find')
def EquipmentsFind():
    if request.method == 'GET':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentFind")
        re = EquipmentIFS.EquipmentsFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allEquipments/Update', methods=['POST', 'GET'])
def allEquipmentsUpdate():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentUpdate")
        re = EquipmentIFS.allEquipmentsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allEquipments/Delete', methods=['POST', 'GET'])
def allEquipmentsDelete():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentDelete")
        re = EquipmentIFS.allEquipmentsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allEquipments/Create', methods=['POST', 'GET'])
def allEquipmentsCreate():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentCreate")
        re = EquipmentIFS.allEquipmentsCreate(data)
        return re


@app.route('/allEquipments/Search', methods=['POST', 'GET'])
def allEquipmentsSearch():
    if request.method == 'POST':
        data = request.values
        EquipmentIFS = Model.core.EquipmentWebIFS("EquipmentSearch")
        re = EquipmentIFS.allEquipmentsSearch(data)
        return re


# 加载工作台
@app.route('/ProductRule')
def productRule():
    return render_template('sysProductRule.html')


@app.route('/allProductRules/Find')
def ProductRulesFind():
    if request.method == 'GET':
        data = request.values
        ProductRuleIFS = Model.core.ProductRuleWebIFS("ProductRuleFind")
        re = ProductRuleIFS.ProductRulesFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductRules/Update', methods=['POST', 'GET'])
def allProductRulesUpdate():
    if request.method == 'POST':
        data = request.values
        ProductRuleIFS = Model.core.ProductRuleWebIFS("ProductRuleUpdate")
        re = ProductRuleIFS.allProductRulesUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allProductRules/Delete', methods=['POST', 'GET'])
def allProductRulesDelete():
    if request.method == 'POST':
        data = request.values
        ProductRuleIFS = Model.core.ProductRuleWebIFS("ProductRuleDelete")
        re = ProductRuleIFS.allProductRulesDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductRules/Create', methods=['POST', 'GET'])
def allProductRulesCreate():
    if request.method == 'POST':
        data = request.values
        ProductRuleIFS = Model.core.ProductRuleWebIFS("ProductRuleCreate")
        re = ProductRuleIFS.allProductRulesCreate(data)
        return re


@app.route('/allProductRules/Search', methods=['POST', 'GET'])
def allProductRulesSearch():
    if request.method == 'POST':
        data = request.values
        ProductRuleIFS = Model.core.ProductRuleWebIFS("ProductRuleSearch")
        re = ProductRuleIFS.allProductRulesSearch(data)
        return re



# 加载工作台
@app.route('/ZYPlan')
def zYPlan():
    try:
        product_info = db_session.query(ProductRule.PRCode, ProductRule.PRName).all()
        # print(product_info)
        data_pro = []
        for tu in product_info:
            li = list(tu)
            prcode = li[0]
            name = li[1]
            pro_info = {'PRCode': prcode, 'text': name}
            data_pro.append(pro_info)

        proUnit_info = db_session.query(ProcessUnit.PUCode, ProcessUnit.PUName).all()
        # print(proUnit_info)
        data_pucode = []
        for tu in proUnit_info:
            li = list(tu)
            pucode = li[0]
            name = li[1]
            pro_info = {'PUCode': pucode, 'text': name}
            data_pucode.append(pro_info)
        return render_template('sysZYPlan.html', Product_info=data_pro, ProcessUnit_info=data_pucode, Unit=WeightUnit)
    except Exception as e:
        print(e)
        logger.error(e)
    return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allZYPlans/Find')
def ZYPlansFind():
    if request.method == 'GET':
        data = request.values
        ZYPlanIFS = Model.core.ZYPlanWebIFS("ZYPlanFind")
        re = ZYPlanIFS.ZYPlansFind(data)
        return re

# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allZYPlans/Update', methods=['POST', 'GET'])
def allZYPlansUpdate():
    if request.method == 'POST':
        data = request.values
        ZYPlanIFS = Model.core.ZYPlanWebIFS("ZYPlanUpdate")
        re = ZYPlanIFS.allZYPlansUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allZYPlans/Delete', methods=['POST', 'GET'])
def allZYPlansDelete():
    if request.method == 'POST':
        data = request.values
        ZYPlanIFS = Model.core.ZYPlanWebIFS("ZYPlanDelete")
        re = ZYPlanIFS.allZYPlansDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allZYPlans/Create', methods=['POST', 'GET'])
def allZYPlansCreate():
    if request.method == 'POST':
        data = request.values
        ZYPlanIFS = Model.core.ZYPlanWebIFS("ZYPlanCreate")
        re = ZYPlanIFS.allZYPlansCreate(data)
        return re


@app.route('/allZYPlans/Search', methods=['POST', 'GET'])
def allZYPlansSearch():
    if request.method == 'POST':
        data = request.values
        ZYPlanIFS = Model.core.ZYPlanWebIFS("ZYPlanSearch")
        re = ZYPlanIFS.allZYPlansSearch(data)
        return re


# 加载工作台
@app.route('/ZYTask')
def zYTask():
    try:
        product_info = db_session.query(ProductRule.ID, ProductRule.PRName).all()
        # print(product_info)
        data_pro = []
        for tu in product_info:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_info = {'ID': id, 'text': name}
            data_pro.append(pro_info)

        productUnit_info = db_session.query(ProductUnit.PUID, ProductUnit.PDUnitName).all()
        # print(product_info)
        data_proUnit = []
        for tu in productUnit_info:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_info = {'ID': id, 'text': name}
            data_proUnit.append(pro_info)

        batch_id = db_session.query(ZYPlan.BatchID).all()
        # print(product_info)
        data_batch = []
        for tu in batch_id:
            li = list(tu)
            id = li[0]
            pro_info = {'ID': id}
            data_batch.append(pro_info)
        return render_template('sysZYTask.html', Data_pro=data_pro, Unit=WeightUnit, Data_proUnit=data_proUnit, Data_batch=data_batch)
    except Exception as e:
        print(e)
        logger.error(e)
    return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allZYTasks/Find')
def ZYTasksFind():
    if request.method == 'GET':
        data = request.values
        ZYTaskIFS = Model.core.ZYTaskWebIFS("ZYTaskFind")
        re = ZYTaskIFS.ZYTasksFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allZYTasks/Update', methods=['POST', 'GET'])
def allZYTasksUpdate():
    if request.method == 'POST':
        data = request.values
        ZYTaskIFS = Model.core.ZYTaskWebIFS("ZYTaskUpdate")
        re = ZYTaskIFS.allZYTasksUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allZYTasks/Delete', methods=['POST', 'GET'])
def allZYTasksDelete():
    if request.method == 'POST':
        data = request.values
        ZYTaskIFS = Model.core.ZYTaskWebIFS("ZYTaskDelete")
        re = ZYTaskIFS.allZYTasksDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allZYTasks/Create', methods=['POST', 'GET'])
def allZYTasksCreate():
    if request.method == 'POST':
        data = request.values
        ZYTaskIFS = Model.core.ZYTaskWebIFS("ZYTaskCreate")
        re = ZYTaskIFS.allZYTasksCreate(data)
        return re


@app.route('/allZYTasks/Search', methods=['POST', 'GET'])
def allZYTasksSearch():
    if request.method == 'POST':
        data = request.values
        ZYTaskIFS = Model.core.ZYTaskWebIFS("ZYTaskSearch")
        re = ZYTaskIFS.allZYTasksSearch(data)
        return re


# 加载工作台
@app.route('/ProductControlTask')
def productControlTask():
    try:
        product_def_ID = db_session.query(ProductRule.ID,ProductRule.PRName).all()
        data1 = []
        for tu in product_def_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_def_id = {'ID': id, 'text':name}
            data1.append(pro_def_id)

        productUnit_ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
        data = []
        for tu in productUnit_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_unit_id = {'ID': id, 'text':name}
            data.append(pro_unit_id)
        return render_template('sysProductControlTask.html', Product_def_ID= data1, Product_unit_ID=data)
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allProductControlTasks/Find')
def ProductControlTasksFind():
    if request.method == 'GET':
        data = request.values
        ProductControlTaskIFS = Model.core.ProductControlTaskWebIFS("ProductControlTaskFind")
        re = ProductControlTaskIFS.ProductControlTasksFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductControlTasks/Update', methods=['POST', 'GET'])
def allProductControlTasksUpdate():
    if request.method == 'POST':
        data = request.values
        ProductControlTaskIFS = Model.core.ProductControlTaskWebIFS("ProductControlTaskUpdate")
        re = ProductControlTaskIFS.allProductControlTasksUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allProductControlTasks/Delete', methods=['POST', 'GET'])
def allProductControlTasksDelete():
    if request.method == 'POST':
        data = request.values
        ProductControlTaskIFS = Model.core.ProductControlTaskWebIFS("ProductControlTaskDelete")
        re = ProductControlTaskIFS.allProductControlTasksDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductControlTasks/Create', methods=['POST', 'GET'])
def allProductControlTasksCreate():
    if request.method == 'POST':
        data = request.values
        ProductControlTaskIFS = Model.core.ProductControlTaskWebIFS("ProductControlTaskCreate")
        re = ProductControlTaskIFS.allProductControlTasksCreate(data)
        return re


@app.route('/allProductControlTasks/Search', methods=['POST', 'GET'])
def allProductControlTasksSearch():
    if request.method == 'POST':
        data = request.values
        ProductControlTaskIFS = Model.core.ProductControlTaskWebIFS("ProductControlTaskSearch")
        re = ProductControlTaskIFS.allProductControlTasksSearch(data)
        return re


# 加载工作台
@app.route('/ProductParameter')
def productParameter():
    try:
        product_def_ID = db_session.query(ProductRule.ID, ProductRule.PRName).all()
        data1 = []
        for tu in product_def_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_def_id = {'ID': id, 'text':name}
            data1.append(pro_def_id)

        productUnit_ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
        data = []
        for tu in productUnit_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_unit_id = {'ID': id, 'text':name}
            data.append(pro_unit_id)
        return render_template('sysProductParameter.html', Product_def_ID= data1, Product_unit_ID=data)
    except Exception as e:
        print(e)
        logger.error(e)
    return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allProductParameters/Find')
def ProductParametersFind():
    if request.method == 'GET':
        data = request.values
        ProductParameterIFS = Model.core.ProductParameterWebIFS("ProductParameterFind")
        re = ProductParameterIFS.ProductParametersFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductParameters/Update', methods=['POST', 'GET'])
def allProductParametersUpdate():
    if request.method == 'POST':
        data = request.values
        ProductParameterIFS = Model.core.ProductParameterWebIFS("ProductParameterUpdate")
        re = ProductParameterIFS.allProductParametersUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allProductParameters/Delete', methods=['POST', 'GET'])
def allProductParametersDelete():
    if request.method == 'POST':
        data = request.values
        ProductParameterIFS = Model.core.ProductParameterWebIFS("ProductParameterDelete")
        re = ProductParameterIFS.allProductParametersDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductParameters/Create', methods=['POST', 'GET'])
def allProductParametersCreate():
    if request.method == 'POST':
        data = request.values
        ProductParameterIFS = Model.core.ProductParameterWebIFS("ProductParameterCreate")
        re = ProductParameterIFS.allProductParametersCreate(data)
        return re


@app.route('/allProductParameters/Search', methods=['POST', 'GET'])
def allProductParametersSearch():
    if request.method == 'POST':
        data = request.values
        ProductParameterIFS = Model.core.ProductParameterWebIFS("ProductParameterSearch")
        re = ProductParameterIFS.allProductParametersSearch(data)
        return re


# 加载工作台
@app.route('/MaterialType')
def materialType():
    return render_template('sysMaterialType.html')


@app.route('/allMaterialTypes/Find')
def MaterialTypesFind():
    if request.method == 'GET':
        data = request.values
        MaterialTypeIFS = Model.core.MaterialTypeWebIFS("MaterialTypeFind")
        re = MaterialTypeIFS.MaterialTypesFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allMaterialTypes/Update', methods=['POST', 'GET'])
def allMaterialTypesUpdate():
    if request.method == 'POST':
        data = request.values
        MaterialTypeIFS = Model.core.MaterialTypeWebIFS("MaterialTypeUpdate")
        re = MaterialTypeIFS.allMaterialTypesUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allMaterialTypes/Delete', methods=['POST', 'GET'])
def allMaterialTypesDelete():
    if request.method == 'POST':
        data = request.values
        MaterialTypeIFS = Model.core.MaterialTypeWebIFS("MaterialTypeDelete")
        re = MaterialTypeIFS.allMaterialTypesDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allMaterialTypes/Create', methods=['POST', 'GET'])
def allMaterialTypesCreate():
    if request.method == 'POST':
        data = request.values
        MaterialTypeIFS = Model.core.MaterialTypeWebIFS("MaterialTypeCreate")
        re = MaterialTypeIFS.allMaterialTypesCreate(data)
        return re


@app.route('/allMaterialTypes/Search', methods=['POST', 'GET'])
def allMaterialTypesSearch():
    if request.method == 'POST':
        data = request.values
        MaterialTypeIFS = Model.core.MaterialTypeWebIFS("MaterialTypeSearch")
        re = MaterialTypeIFS.allMaterialTypesSearch(data)
        return re


# 加载工作台
@app.route('/Material')
def material():
    ID = db_session.query(MaterialType.ID, Material.MATName).all()
    data = []
    for tu in ID:
        li = list(tu)
        id = li[0]
        name = li[1]
        materialType_id = {'ID': id,'text':name}
        data.append(materialType_id)
    return render_template('sysMaterial.html', Material_ID=data)


@app.route('/allMaterials/Find')
def MaterialsFind():
    if request.method == 'GET':
        data = request.values
        MaterialIFS = Model.core.MaterialWebIFS("MaterialFind")
        re = MaterialIFS.MaterialsFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allMaterials/Update', methods=['POST', 'GET'])
def allMaterialsUpdate():
    if request.method == 'POST':
        data = request.values
        MaterialIFS = Model.core.MaterialWebIFS("MaterialUpdate")
        re = MaterialIFS.allMaterialsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allMaterials/Delete', methods=['POST', 'GET'])
def allMaterialsDelete():
    if request.method == 'POST':
        data = request.values
        MaterialIFS = Model.core.MaterialWebIFS("MaterialDelete")
        re = MaterialIFS.allMaterialsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allMaterials/Create', methods=['POST', 'GET'])
def allMaterialsCreate():
    if request.method == 'POST':
        data = request.values
        MaterialIFS = Model.core.MaterialWebIFS("MaterialCreate")
        re = MaterialIFS.allMaterialsCreate(data)
        return re


@app.route('/allMaterialPlanBOMS', methods=['POST', 'GET'])
def allMaterialPlanBOMS():
    if request.method == 'GET':
        data = request.values
        MaterialBOMIFS = Model.core.MaterialBOMWebIFS("MaterialCreate")
        re = MaterialBOMIFS.MaterialBOMsFind(data)
        return re


@app.route('/allMaterials/Search', methods=['POST', 'GET'])
def allMaterialsSearch():
    if request.method == 'POST':
        data = request.values
        MaterialIFS = Model.core.MaterialWebIFS("MaterialSearch")
        re = MaterialIFS.allMaterialsSearch(data)
        return re


# 加载工作台
@app.route('/MaterialBOM')
def materialBOM():
    try:
        material_ID = db_session.query(Material.ID,Material.MATName).all()
        data_material = []
        for tu in material_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            material_id = {'ID': id,'text':name}
            data_material.append(material_id)

        product_def_ID = db_session.query(ProductRule.ID, ProductRule.PRName).all()
        data1 = []
        for tu in product_def_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_def_id = {'ID': id, 'text':name}
            data1.append(pro_def_id)

        productUnit_ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
        data = []
        for tu in productUnit_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_unit_id = {'ID': id, 'text':name}
            data.append(pro_unit_id)

        material_Type_ID = db_session.query(MaterialType.ID, MaterialType.MATTypeName).all()
        data_material_typeID = []
        for tu in material_Type_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            material_type_id = {'ID': id, 'text':name}
            data_material_typeID.append(material_type_id)
        return render_template('sysMaterialBOM.html', Material_ID=data_material,
                               Product_def_ID= data1, Product_unit_ID=data,
                               MaterialType_ID=data_material_typeID)
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allMaterialBOMs/Find')
def MaterialBOMsFind():
    if request.method == 'GET':
        data = request.values
        MaterialBOMIFS = Model.core.MaterialBOMWebIFS("MaterialBOMFind")
        re = MaterialBOMIFS.MaterialBOMsFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allMaterialBOMs/Update', methods=['POST', 'GET'])
def allMaterialBOMsUpdate():
    if request.method == 'POST':
        data = request.values
        MaterialBOMIFS = Model.core.MaterialBOMWebIFS("MaterialBOMUpdate")
        re = MaterialBOMIFS.allMaterialBOMsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allMaterialBOMs/Delete', methods=['POST', 'GET'])
def allMaterialBOMsDelete():
    if request.method == 'POST':
        data = request.values
        MaterialBOMIFS = Model.core.MaterialBOMWebIFS("MaterialBOMDelete")
        re = MaterialBOMIFS.allMaterialBOMsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allMaterialBOMs/Create', methods=['POST', 'GET'])
def allMaterialBOMsCreate():
    if request.method == 'POST':
        data = request.values
        MaterialBOMIFS = Model.core.MaterialBOMWebIFS("MaterialBOMCreate")
        re = MaterialBOMIFS.allMaterialBOMsCreate(data)
        return re


@app.route('/allMaterialBOMs/Search', methods=['POST', 'GET'])
def allMaterialBOMsSearch():
    if request.method == 'POST':
        data = request.values
        MaterialBOMIFS = Model.core.MaterialBOMWebIFS("MaterialBOMSearch")
        re = MaterialBOMIFS.allMaterialBOMsSearch(data)
        return re


# 加载工作台
@app.route('/ZYPlanMaterial')
def zYPlanMaterial():
    return render_template('sysZYPlanMaterial.html')


@app.route('/allZYPlanMaterials/Find')
def ZYPlanMaterialsFind():
    if request.method == 'GET':
        data = request.values
        ZYPlanMaterialIFS = Model.core.ZYPlanMaterialWebIFS("ZYPlanMaterialFind")
        re = ZYPlanMaterialIFS.ZYPlanMaterialsFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allZYPlanMaterials/Update', methods=['POST', 'GET'])
def allZYPlanMaterialsUpdate():
    if request.method == 'POST':
        data = request.values
        ZYPlanMaterialIFS = Model.core.ZYPlanMaterialWebIFS("ZYPlanMaterialUpdate")
        re = ZYPlanMaterialIFS.allZYPlanMaterialsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allZYPlanMaterials/Delete', methods=['POST', 'GET'])
def allZYPlanMaterialsDelete():
    if request.method == 'POST':
        data = request.values
        ZYPlanMaterialIFS = Model.core.ZYPlanMaterialWebIFS("ZYPlanMaterialDelete")
        re = ZYPlanMaterialIFS.allZYPlanMaterialsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allZYPlanMaterials/Create', methods=['POST', 'GET'])
def allZYPlanMaterialsCreate():
    if request.method == 'POST':
        data = request.values
        ZYPlanMaterialIFS = Model.core.ZYPlanMaterialWebIFS("ZYPlanMaterialCreate")
        re = ZYPlanMaterialIFS.allZYPlanMaterialsCreate(data)
        return re


@app.route('/allZYPlanMaterials/Search', methods=['POST', 'GET'])
def allZYPlanMaterialsSearch():
    if request.method == 'POST':
        data = request.values
        ZYPlanMaterialIFS = Model.core.ZYPlanMaterialWebIFS("ZYPlanMaterialSearch")
        re = ZYPlanMaterialIFS.allZYPlanMaterialsSearch(data)
        return re


# 加载工作台
@app.route('/ProductUnit')
def productUnit():
    try:
        product_def_ID = db_session.query(ProductRule.ID, ProductRule.PRName).all()
        data1 = []
        for tu in product_def_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_def_id = {'ID': id, 'text':name}
            data1.append(pro_def_id)

        productUnit_ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
        data = []
        for tu in productUnit_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_unit_id = {'ID': id, 'text':name}
            data.append(pro_unit_id)
        return render_template('sysProductUnit.html', Product_def_ID= data1, Product_unit_ID=data)
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allProductUnits/Find')
def ProductUnitsFind():
    if request.method == 'GET':
        data = request.values
        ProductUnitIFS = Model.core.ProductUnitWebIFS("ProductUnitFind")
        re = ProductUnitIFS.ProductUnitsFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductUnits/Update', methods=['POST', 'GET'])
def allProductUnitsUpdate():
    if request.method == 'POST':
        data = request.values
        ProductUnitIFS = Model.core.ProductUnitWebIFS("ProductUnitUpdate")
        re = ProductUnitIFS.allProductUnitsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allProductUnits/Delete', methods=['POST', 'GET'])
def allProductUnitsDelete():
    if request.method == 'POST':
        data = request.values
        ProductUnitIFS = Model.core.ProductUnitWebIFS("ProductUnitDelete")
        re = ProductUnitIFS.allProductUnitsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductUnits/Create', methods=['POST', 'GET'])
def allProductUnitsCreate():
    if request.method == 'POST':
        data = request.values
        ProductUnitIFS = Model.core.ProductUnitWebIFS("ProductUnitCreate")
        re = ProductUnitIFS.allProductUnitsCreate(data)
        return re


@app.route('/allProductUnits/Search', methods=['POST', 'GET'])
def allProductUnitsSearch():
    if request.method == 'POST':
        data = request.values
        ProductUnitIFS = Model.core.ProductUnitWebIFS("ProductUnitSearch")
        re = ProductUnitIFS.allProductUnitsSearch(data)
        return re


# 加载工作台
@app.route('/ProductUnitRoute')
def productUnitRoute():
    try:
        product_def_ID = db_session.query(ProductRule.ID, ProductRule.PRName).all()
        data1 = []
        for tu in product_def_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_def_id = {'ID': id, 'text':name}
            data1.append(pro_def_id)

        productUnit_ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
        data = []
        for tu in productUnit_ID:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_unit_id = {'ID': id, 'text':name}
            data.append(pro_unit_id)
        return render_template('sysProductUnitRoute.html', Product_def_ID=data1, ProductUnit_ID=data)
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)



@app.route('/allProductUnitRoutes/Find')
def ProductUnitRoutesFind():
    if request.method == 'GET':
        data = request.values
        ProductUnitRouteIFS = Model.core.ProductUnitRouteWebIFS("ProductUnitRouteFind")
        re = ProductUnitRouteIFS.ProductUnitRoutesFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductUnitRoutes/Update', methods=['POST', 'GET'])
def allProductUnitRoutesUpdate():
    if request.method == 'POST':
        data = request.values
        ProductUnitRouteIFS = Model.core.ProductUnitRouteWebIFS("ProductUnitRouteUpdate")
        re = ProductUnitRouteIFS.allProductUnitRoutesUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allProductUnitRoutes/Delete', methods=['POST', 'GET'])
def allProductUnitRoutesDelete():
    if request.method == 'POST':
        data = request.values
        ProductUnitRouteIFS = Model.core.ProductUnitRouteWebIFS("ProductUnitRouteDelete")
        re = ProductUnitRouteIFS.allProductUnitRoutesDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allProductUnitRoutes/Create', methods=['POST', 'GET'])
def allProductUnitRoutesCreate():
    if request.method == 'POST':
        data = request.values
        ProductUnitRouteIFS = Model.core.ProductUnitRouteWebIFS("ProductUnitRouteCreate")
        re = ProductUnitRouteIFS.allProductUnitRoutesCreate(data)
        return re


@app.route('/allProductUnitRoutes/Search', methods=['POST', 'GET'])
def allProductUnitRoutesSearch():
    if request.method == 'POST':
        data = request.values
        ProductUnitRouteIFS = Model.core.ProductUnitRouteWebIFS("ProductUnitRouteSearch")
        re = ProductUnitRouteIFS.allProductUnitRoutesSearch(data)
        return re


# 加载工作台
@app.route('/SchedulePlan')
def schedulePlan():
    return render_template('sysSchedulePlan.html')


@app.route('/allSchedulePlans/Find')
def SchedulePlansFind():
    if request.method == 'GET':
        data = request.values
        SchedulePlanIFS = Model.core.SchedulePlanWebIFS("SchedulePlanFind")
        re = SchedulePlanIFS.SchedulePlansFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allSchedulePlans/Update', methods=['POST', 'GET'])
def allSchedulePlansUpdate():
    if request.method == 'POST':
        data = request.values
        SchedulePlanIFS = Model.core.SchedulePlanWebIFS("SchedulePlanUpdate")
        re = SchedulePlanIFS.allSchedulePlansUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allSchedulePlans/Delete', methods=['POST', 'GET'])
def allSchedulePlansDelete():
    if request.method == 'POST':
        data = request.values
        SchedulePlanIFS = Model.core.SchedulePlanWebIFS("SchedulePlanDelete")
        re = SchedulePlanIFS.allSchedulePlansDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allSchedulePlans/Create', methods=['POST', 'GET'])
def allSchedulePlansCreate():
    if request.method == 'POST':
        data = request.values
        SchedulePlanIFS = Model.core.SchedulePlanWebIFS("SchedulePlanCreate")
        re = SchedulePlanIFS.allSchedulePlansCreate(data)
        return re


@app.route('/allSchedulePlans/Search', methods=['POST', 'GET'])
def allSchedulePlansSearch():
    if request.method == 'POST':
        data = request.values
        SchedulePlanIFS = Model.core.SchedulePlanWebIFS("SchedulePlanSearch")
        re = SchedulePlanIFS.allSchedulePlansSearch(data)
        return re


# 加载工作台
@app.route('/ZYPlanGuid/planmanager')
def planManager():
    product_info = db_session.query(ProductRule.PRCode, ProductRule.PRName).all()
    # print(product_info)
    data_pro = []
    for tu in product_info:
        li = list(tu)
        prcode = li[0]
        name = li[1]
        pro_info = {'PRCode': prcode, 'text': name}
        data_pro.append(pro_info)

    proUnit_info = db_session.query(Unit.UnitCode, Unit.UnitName).all()
    data_pucode = []
    for tu in proUnit_info:
        li = list(tu)
        pucode = li[0]
        name = li[1]
        pro_info = {'UnitCode': pucode, 'text': name}
        data_pucode.append(pro_info)
    return render_template('planmanager.html', Product_info=data_pro, Unit=data_pucode)


@app.route('/allPlanManagers/Find')
def PlanManagersFind():
    if request.method == 'GET':
        data = request.values
        PlanManagerIFS = Model.core.PlanManagerWebIFS("PlanManagerFind")
        re = PlanManagerIFS.PlanManagersFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allPlanManagers/Update', methods=['POST', 'GET'])
def allPlanManagersUpdate():
    if request.method == 'POST':
        data = request.values
        PlanManagerIFS = Model.core.PlanManagerWebIFS("PlanManagerUpdate")
        re = PlanManagerIFS.allPlanManagersUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allPlanManagers/Delete', methods=['POST', 'GET'])
def allPlanManagersDelete():
    if request.method == 'POST':
        data = request.values
        PlanManagerIFS = Model.core.PlanManagerWebIFS("PlanManagerDelete")
        re = PlanManagerIFS.allPlanManagersDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allPlanManagers/Create', methods=['POST', 'GET'])
def allPlanManagersCreate():
    if request.method == 'POST':
        data = request.values
        PlanManagerIFS = Model.core.PlanManagerWebIFS("PlanManagerCreate")
        re = PlanManagerIFS.allPlanManagersCreate(data)
        BatchID = data['BatchID']
        PlanManageID = db_session.query(Model.core.PlanManager.ID).filter_by(BatchID=BatchID).first()
        PlanManageID = PlanManageID[0]
        userName = current_user.Name
        Desc = "计划向导生成计划planmanager"
        Type = Model.Global.Type.NEW.value
        PlanCreate = ctrlPlan('PlanCreate')
        bReturn = PlanCreate.createWorkFlowEventPlan(PlanManageID, userName, Desc, Type)
        if(bReturn == False):
            re = False
        PlanManageID = PlanManageID
        AuditStatus = Model.Global.AuditStatus.Unaudited.value
        DescF = "计划向导生成计划planmanager"
        cReturn = PlanCreate.createWorkFlowStatus(PlanManageID, None, None, AuditStatus, DescF)
        if (cReturn == False):
            re = False
        return re


@app.route('/allPlanManagers/Search', methods=['POST', 'GET'])
def allPlanManagersSearch():
    if request.method == 'POST':
        data = request.values
        PlanManagerIFS = Model.core.PlanManagerWebIFS("PlanManagerSearch")
        re = PlanManagerIFS.allPlanManagersSearch(data)
        return re


# 加载工作台
@app.route('/Unit')
def unit():
    return render_template('sysUnit.html')


@app.route('/allUnits/Find')
def UnitsFind():
    if request.method == 'GET':
        data = request.values
        UnitIFS = Model.core.UnitWebIFS("UnitFind")
        re = UnitIFS.UnitsFind(data)
        return re


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allUnits/Update', methods=['POST', 'GET'])
def allUnitsUpdate():
    if request.method == 'POST':
        data = request.values
        UnitIFS = Model.core.UnitWebIFS("UnitUpdate")
        re = UnitIFS.allUnitsUpdate(data)
        return re


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allUnits/Delete', methods=['POST', 'GET'])
def allUnitsDelete():
    if request.method == 'POST':
        data = request.values
        UnitIFS = Model.core.UnitWebIFS("UnitDelete")
        re = UnitIFS.allUnitsDelete(data)
        return re


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allUnits/Create', methods=['POST', 'GET'])
def allUnitsCreate():
    if request.method == 'POST':
        data = request.values
        UnitIFS = Model.core.UnitWebIFS("UnitCreate")
        re = UnitIFS.allUnitsCreate(data)
        return re


@app.route('/allUnits/Search', methods=['POST', 'GET'])
def allUnitsSearch():
    if request.method == 'POST':
        data = request.values
        UnitIFS = Model.core.UnitWebIFS("UnitSearch")
        re = UnitIFS.allUnitsSearch(data)
        return re


def getOrganizationChildren(id=0):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "colorScheme": obj.Color, "image": obj.Img, "title": obj.OrganizationName,
                           "items": getOrganizationChildren(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'
        # data = string(sz)
        # data.replace(srep, '')
        return sz
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "获取树形结构菜单报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/Organization/Find')
def OrganizationFind():
    if request.method == 'GET':
        try:
            # data = load()
            data = getOrganizationChildren(id=0)
            # organizations = db_session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 建立会话
# 主页面路由
# 保护路由只让已认证的用户访问，如果未认证的用户访问这个路由，Flask-Login 会拦截请求，把用户发往登录页面。
def isIn(source,target):
    count = 0
    for index in source:
        if index in target:
            count += 1
            if count <= len(source):
                return True
            return False
app.add_template_global(isIn,'isIn')


@app.route('/')
@login_required
def hello_world():
    return render_template('main.html')


# 加载工作台
@app.route('/workbench')
def workbenck():
    return render_template('workbench.html')


# 工作台菜单role
@app.route('/sysrole')
def sysrole():
    dataRoleInfo = []
    roleNames = db_session.query(Role.ID, Role.RoleName).all()
    for role in roleNames:
        li = list(role)
        id = li[0]
        name = li[1]
        roleName = {'RoleID': id, 'RoleName': name}
        dataRoleInfo.append(roleName)
    return render_template('sysRole.html', RoleInfos=dataRoleInfo)


# role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allroles/Update', methods=['POST', 'GET'])
def allrolesUpdate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                Roleid = int(data['ID'])
                role = db_session.query(Role).filter_by(ID=Roleid).first()
                role.RoleName = data['RoleName']
                role.RoleSeq = data['RoleSeq']
                role.Description = data['Description']
                role.CreatePerson = data['CreatePerson']
                role.CreateDate = data['CreateDate']
                role.ParentNode = data['ParentNode']
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "更新角色报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
# 解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allroles/Delete', methods=['POST', 'GET'])
def allrolesDelete():
    if request.method == 'POST':
        data = request.values
        try:
            #   jsonDict = data.to_dict(
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    # for subkey in list(key):
                    Roleid = int(key)
                    try:
                        oclass = db_session.query(Role).filter_by(ID=Roleid).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        insertSyslog("error", "删除角色报错Error：" + str(ee), current_user.Name)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder, ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "删除角色报错Error：" + str(e), current_user.Name)
            # return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allroles/Create', methods=['POST', 'GET'])
def allrolesCreate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(Role(RoleName=data['RoleName'],
                                 RoleSeq=data['RoleSeq'],
                                 Description=data['Description'],
                                 CreatePerson=data['CreatePerson'],
                                 CreateDate= datetime.datetime.now(),
                                 ParentNode = data['ParentNode']
                                 ))
                db_session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "创建角色报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:"+ str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


#role查询数据，通过传入的json数据，解析之后进行相应更新
#采用服务端数据分页，通过easyui-datagrid传入的页数和每页包含的记录数回传
#注意写easyui-datagrid的json数据格式！特别是最开始部分"total":20,"rows":[]}
@app.route('/allroles/Find')
def allrolesFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(func.count(Role.ID)).scalar()
                roles = db_session.query(Role).all()[inipage:endpage]
                # ORM模型转换json格式
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询角色列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allroles/Search', methods=['POST', 'GET'])
def allrolesSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                strconditon = "%" + data['condition'] + "%"
                roles = db_session.query(Role).filter(Role.RoleName.like(strconditon)).all()
                total = Counter(roles)
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "擦护心角色列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载工作台
@app.route('/Myorganization')
def myorganization():
    return render_template('Myorganization.html')


def getMyOrganizationChildren(id=0):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "text": obj.OrganizationName, "children": getMyOrganizationChildren(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'
        # data = string(sz)
        # data.replace(srep, '')
        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


def getMyEnterprise(id=0):
    sz = []
    try:
        orgs = db_session.query(Organization).filter().all()
        for obj in orgs:
            sz.append({"id": obj.ID, "text": obj.OrganizationName, "group": obj.ParentNode})
        # data = string(sz)"'"
        # data.replace(srep, '')
        return sz
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "获取树形结构报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/MyOp')
def MyOpFind():
    if request.method == 'GET':
        try:
            # data = load()
            data = getMyOrganizationChildren(id=0)
            # organizations = db_session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/Myenterprise')
def myenterprise():
    if request.method == 'GET':
        try:
            # data = load()
            data = getMyEnterprise(id=0)
            # organizations = db_session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/Myenterprise/Select')
def MyenterpriseSelect():
    if request.method == 'GET':
        odata = request.values
        try:
            json_str = json.dumps(odata.to_dict())
            if len(json_str) > 5:
                objid = int(odata['ID'])
                oclass = db_session.query(Model.system.Organization).filter_by(ID=objid).first()
                jsondata = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载工作台
@app.route('/createPlanWizard')
def createPlanWizard():
    try:
        product_info = db_session.query(ProductRule.ID, ProductRule.PRName).all()
        data = []
        for tu in product_info:
            li = list(tu)
            id = li[0]
            name = li[1]
            pro_info = {'ID': id, 'text':name}
            data.append(pro_info)
        dataUnitName = []
        unitNames = db_session.query(Unit.UnitCode, Unit.UnitName).all()
        for unit in unitNames:
            li = list(unit)
            id = li[0]
            name = li[1]
            unitName = {'UnitCode': id, 'UnitName': name}
            dataUnitName.append(unitName)
        dataPLineName = []
        pLineNames = db_session.query(ProductLine.PLineCode, ProductLine.PLineName).all()
        for pLine in pLineNames:
            li = list(pLine)
            id = li[0]
            name = li[1]
            pLineName = {'PLineCode': id, 'PLineName': name}
            dataPLineName.append(pLineName)
        return render_template('createPlanWizard.html', Product_info=data, Unit=dataUnitName,PLine_info=dataPLineName)
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/getUnitByKg')
def getUnitByKg():
    if request.method == 'GET':
        try:
            UnitIFS = Model.core.UnitWebIFS("getUnitByKg")
            re = UnitIFS.getUnitByCondition("kg")
            jsondata = json.dumps(re, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/getdefaultPlanWeight')
def getdefaultPlanWeight():
    if request.method == 'GET':
        try:
            UnitIFS = Model.core.UnitWebIFS("getUnitByKg")
            re = UnitIFS.getUnitByCondition("kg")
            jsondata = json.dumps(re, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


def getProductRule():
    sz = []
    try:
        objs = db_session.query(Model.core.ProductRule).filter().all()
        iIndex = 0
        strSelected = "true"
        for obj in objs:
            if iIndex == 0:
                sz.append({"id": obj.ID, "text": obj.PRName, "selected": strSelected})
            else:
                iIndex = iIndex + 1
                sz.append({"id": obj.ID, "text": obj.PRName})

        # data = string(sz)"'"
        # data.replace(srep, '')
        return sz
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/treeProductRule')
def treeProductRule():
    if request.method == 'GET':
        try:
            # data = load()
            data = getProductRule()
            # organizations = db_session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# Opc服务配置
@app.route('/OpcServer')
def opcServer():
    return render_template('OpcServer.html')

# 返回Opc服务列表
@app.route('/OpcServer/Find')
def OpcServerFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(OpcServer.ID).count()
                if total > 0:
                    qDatas = db_session.query(OpcServer).all()[inipage:endpage]
                    # ORM模型转换json格式
                    jsonopcserver = json.dumps(qDatas, cls=Model.BSFramwork.AlchemyEncoder,
                                                  ensure_ascii=False)
                    jsonopcserver = '{"total"' + ":" + str(
                        total) + ',"rows"' + ":\n" + jsonopcserver + "}"
                    return jsonopcserver
                else:
                    return ""
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)
# 添加Opc服务配置
@app.route('/OpcServer/Create', methods=['POST', 'GET'])
def OpcServerCreate():
    if request.method == 'POST':
        try:
            data = request.values
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(
                    OpcServer(
                        ServerName=data['ServerName'],
                        URI=data['URI'],
                        Desc=data['Desc']))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 删除Opc服务配置
@app.route('/OpcServer/Delete', methods=['POST', 'GET'])
def OpcServerDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    OpcServerID = int(key)
                    try:
                        oclass = db_session.query(OpcServer).filter_by(ID=OpcServerID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 修改Opc服务
@app.route('/OpcServer/Update', methods=['POST', 'GET'])
def OpcServerUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                OpcServerID = int(data['ID'])
                oclass = db_session.query(OpcServer).filter_by(ID=OpcServerID).first()
                oclass.ServerName = data['ServerName']
                oclass.URI = data['URI']
                oclass.Desc = data['Desc']
                db_session.add(oclass)
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 查询Opc服务
@app.route('/OpcServer/Search', methods=['POST', 'GET'])
def OpcServerSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                ServerName = "%" + data['ServerName'] + "%"
                OpcServerscount = db_session.query(OpcServer).filter(
                    OpcServer.ServerName.like(ServerName)).all()
                total = Counter(OpcServerscount)
                jsonOpcServers = json.dumps(OpcServerscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                jsonOpcServers = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonOpcServers + "}"
                return jsonOpcServers
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 加载OPC-Tag
@app.route('/OpcTag/load')
def opcTagLoad():
    try:
        serverNames = db_session.query(OpcServer.ServerName).all()
        server_names = []
        for tu in serverNames:
            li = list(tu)
            name = li[0]
            ser_info = {'servername': name}
            server_names.append(ser_info)
        return render_template('OpcTagLoad.html', server_names=server_names)
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "加载OPC-Tag错误Error：" + str(e), current_user.Name)

@app.route('/OpcServer/Tag', methods=['POST', 'GET'])
def opcServerTag():
    if request.method == 'GET':
        data = request.values
        try:
            ServerName = data['ServerName']
            if ServerName is None:
                return
            URI = db_session.query(OpcServer.URI).filter_by(ServerName=ServerName).first()
            return URI[0]
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "获取OpcServer下的URI报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)



global id
id = 0
def printSelect(node, depth): # id:0, depth:1
    result = []
    global id
    id += 1 # 控制下一层
    if depth <= 2:
        for cNode in node.get_children():#[Node(TwoByteNodeId(i=86)), Node(TwoByteNodeId(i=85)), Node(TwoByteNodeId(i=87))]
            if len(cNode.get_children()) >= 0:
                if len(cNode.get_children()) > 0:
                    result.append({"id": id+1,
                                   "nodeId": cNode.nodeid.to_string(),
                                   "displayName": cNode.get_display_name().Text,
                                   "BrowseName": cNode.get_browse_name().to_string(),
                                   "state": 'closed',
                                   "children": printSelect(cNode, depth+1)
                                   })
                if len(cNode.get_children()) == 0:
                    result.append({"id": id + 1,
                                   "nodeId": cNode.nodeid.to_string(),
                                   "displayName": cNode.get_display_name().Text,
                                   "BrowseName": cNode.get_browse_name().to_string(),
                                   "state": 'open',
                                   "children": printSelect(cNode, depth + 1)
                                   })
        return result

# nodeid displayname browsename
# 连接opcua-client
@app.route('/opcuaClient/link', methods=['POST', 'GET'])
def opcuaClientLink():
    if request.method == 'POST':
        data = request.values
        try:
            # 连接opc服务
            URI = data["URI"]
            if URI is None or URI == '':
                return
            client = Client("%s"% URI)
            client.connect()
            # 获取根节点
            rootNode = client.get_root_node()
            tree_data = printSelect(rootNode, 1)
            tree_data = json.dumps(tree_data, cls=AlchemyEncoder, ensure_ascii=False)
            return tree_data
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "opcuaClient连接失败Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/opcuaClient/NodeLoadMore', methods=['POST', 'GET'])
def nodeLoad():
    if request.method == "POST":
        data = request.values
        try:
            rootNode = data['nodeId']
            id = data['id']
            URI = data["URI"]
            if rootNode is None or id is None or URI is None:
                return
            client = Client("%s" % URI)
            client.connect()
            rootNode = client.get_node(rootNode)
            tree_data = printSelect(rootNode, 1)
            tree_data = json.dumps(tree_data, cls=AlchemyEncoder, ensure_ascii=False)
            return tree_data
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "加载opcuaClient节点失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


def store_child(node, OpcServerID):
    for cNode in node.get_children():
        nodeId = cNode.nodeid.to_string()
        displayName = cNode.get_display_name().Text
        opcTag_c = OpcTag()
        opcTag_c.OpcServerID = OpcServerID
        opcTag_c.NodeID = nodeId
        opcTag_c.DisplayName = displayName
        opcTag_c.ParentID = node.nodeid.to_string()
        db_session.add(opcTag_c)
        db_session.commit()
        if len(cNode.get_children()) > 0:
            store_child(cNode, OpcServerID)

# 将所选OPC-Tag加载到数据库
@app.route("/opcuaClient/storeOpcTag", methods=['POST', 'GET'])
def storeOpcTag():
    if request.method == 'POST':
        data = request.values
        try:
            nodeId = data['nodeId']
            displayName = data['displayName']
            URI = data['URI']
            if nodeId is None or displayName is None or URI is None:
                return
            oclass = db_session.query(OpcTag).filter_by(NodeID=nodeId).first()
            if oclass:
                return
            client = Client("%s" % URI)
            client.connect()
            OpcServerID = db_session.query(OpcServer).filter_by(URI=URI).first().ID
            # 存储当前节点
            opcTag_r = OpcTag()
            opcTag_r.OpcServerID = OpcServerID
            opcTag_r.NodeID = nodeId
            opcTag_r.DisplayName = displayName
            db_session.add(opcTag_r)
            db_session.commit()
            # 存储子节点
            node = client.get_node(nodeId)
            store_child(node, OpcServerID)
            return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "OpcTag存储失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 配置采集策略模板
@app.route('/CollectParamsTemplate/config')
def collectParamsTemplateConfig():
    return render_template('collectParamsTemplateConfig.html')

@app.route('/CollectParamsTemplate/config/find', methods=['POST', 'GET'])
def templateFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(CollectParamsTemplate.ID).count()
                if total > 0:
                    qDatas = db_session.query(CollectParamsTemplate).all()[inipage:endpage]
                    # ORM模型转换json格式
                    jsonTemplateconfig = json.dumps(qDatas, cls=Model.BSFramwork.AlchemyEncoder,
                                                  ensure_ascii=False)
                    jsonTemplateconfig = '{"total"' + ":" + str(
                        total) + ',"rows"' + ":\n" + jsonTemplateconfig + "}"
                    return jsonTemplateconfig
                else:
                    return ""
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据加载失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)

@app.route('/CollectParamsTemplate/config/create', methods=['POST', 'GET'])
def templateCreate():
    if request.method == 'POST':
        try:
            data = request.values
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(
                    CollectParamsTemplate(
                        TemplateName=data['TemplateName'],
                        Desc=data['Desc']))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据创建失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectParamsTemplate/config/delete', methods=['POST', 'GET'])
def templateDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    TemplateID = int(key)
                    try:
                        oclass = db_session.query(CollectParamsTemplate).filter_by(ID=TemplateID).first()
                        oclass_params = db_session.query(CollectParams).filter_by(CollectParamsTemplateID=TemplateID).first()
                        db_session.delete(oclass)
                        if oclass_params is not None:
                            db_session.delete(oclass_params)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据删除失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectParamsTemplate/config/update', methods=['POST', 'GET'])
def templateUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                TemplateID = int(data['ID'])
                oclass = db_session.query(CollectParamsTemplate).filter_by(ID=TemplateID).first()
                oclass.TemplateName = data['TemplateName']
                oclass.TableName = data['TableName'],
                oclass.Desc = data['Desc']
                db_session.add(oclass)
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据更新失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectParamsTemplate/config/search', methods=['POST', 'GET'])
def templateSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                TemplateName = "%" + data['TemplateName'] + "%"
                Templatescount = db_session.query(CollectParamsTemplate).filter(
                    CollectParamsTemplate.TemplateName.like(TemplateName)).all()
                total = Counter(Templatescount)
                jsonTemplates = json.dumps(Templatescount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                jsonTemplates = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonTemplates + "}"
                return jsonTemplates
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据查询失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


# 采集模板配置
@app.route('/CollectParams/config')
def collectParamsConfig():
    TemplateNames = []
    TempNames = db_session.query(CollectParamsTemplate.TemplateName).all()
    for name in TempNames:
        li = list(name)
        name = li[0]
        temp_name = {'tempName': name}
        TemplateNames.append(temp_name)
    NodeID = []
    NodeIDs = db_session.query(OpcTag.NodeID).all()
    for nodeID in NodeIDs:
        li = list(nodeID)
        ID = li[0]
        node_id = {'nodeID': ID}
        NodeID.append(node_id)
    return render_template('collectParamsConfig.html', TempNames=TemplateNames, NodeID=NodeID)

def get_childs(ParentID):
    childs = db_session.query(OpcTag).filter_by(ParentID=ParentID).all()
    return childs

def getOpcTagList(depth, ParentID=None):
    sz = []
    try:
        opcTags = db_session.query(OpcTag).filter_by(ParentID=ParentID).all()
        if depth<=1:
            for obj in opcTags:
                if obj.ParentID == ParentID:
                    if len(get_childs(ParentID)) > 0:
                        sz.append({"id": obj.ID,
                                   "NodeId": obj.NodeID,
                                   "Desc": obj.Note,
                                   "state": 'closed',
                                   "children": getOpcTagList(depth+1, ParentID=obj.NodeID)})
                    if len(get_childs(ParentID)) == 0:
                        sz.append({"id": obj.ID,
                                   "NodeId": obj.NodeID,
                                   "Desc": obj.Note,
                                   "state": 'open',
                                   "children": getOpcTagList(depth+1, ParentID=obj.NodeID)})
            return sz
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "getOpcTagList加载父级菜单列表报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/NodeID/LoadMore', methods=['POST', 'GET'])
def nodeIdLoadMore():
    if request.method == "POST":
        data = request.values
        try:
            id = data['id']
            rootNode = db_session.query(OpcTag.NodeID).filter_by(ID=id).first()[0]
            # print(rootNode)
            if rootNode is None:
                return
            tree_data = getOpcTagList(depth=0, ParentID=rootNode)
            tree_data = json.dumps(tree_data, cls=AlchemyEncoder, ensure_ascii=False)
            return tree_data
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "加载NodeID变量节点失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectParams/OpcTagLoad', methods=['POST', 'GET'])
def OpcTagLoad():
    if request.method == 'POST':
        try:
            data = getOpcTagList(depth=0)
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "路由/CollectParams/OpcTagLoad生成OpcTag树形图报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectParams/store', methods=['POST', 'GET'])
def collectParams():
    if request.method == 'GET':
        data = request.values
        try:
            CollectParamsTemplateID = data['CollectParamsTemplateID']
            Ids = data['OpcTags']
            Ids = json.loads(Ids)
            if CollectParamsTemplateID is None or Ids is None:
                return
            if len(Ids) > 0:
                for Id in Ids:
                    # 判断当前模板是否存在
                    object = db_session.query(CollectParams).filter(and_(CollectParams.OpcTagID==Id['nodeId'],CollectParams.CollectParamsTemplateID==CollectParamsTemplateID)).first()
                    if object is not None:
                        db_session.delete(object)
                        db_session.commit()
                        db_session.add(
                            CollectParams(
                                CollectParamsTemplateID=CollectParamsTemplateID,
                                OpcTagID=Id['nodeId']))
                        db_session.commit()
                    else:
                        db_session.add(CollectParams(CollectParamsTemplateID=CollectParamsTemplateID,
                                                     OpcTagID=Id['nodeId']))
                        db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParams数据创建失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

def transform(IDs):
    Datas = []
    for ID in IDs:
        # 查询OpcTagID
        OpcTagID = db_session.query(CollectParams.OpcTagID).filter_by(ID=ID).first()[0]
        # 通过OpcTagID查询NodeID
        NodeID = db_session.query(OpcTag.NodeID).filter_by(ID=OpcTagID).first()[0]
        # 查询CollectParamsTemplateID
        tempID = db_session.query(CollectParams.CollectParamsTemplateID).filter_by(ID=ID).first()
        # 通过CollectParamsTemplateID查询TemplateName
        tempName = db_session.query(CollectParamsTemplate.TemplateName).filter_by(ID=tempID).first()
        Desc = db_session.query(CollectParams.Desc).filter_by(ID=ID).first()[0]
        Datas.append({"TemplateName": tempName, "NodeID": NodeID, "Desc": Desc})
    return Datas

@app.route('/CollectParams/find', methods=['POST', 'GET'])
def collectParamsFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(CollectParams.ID).count()
                if total > 0:
                    # 查询模板ID
                    IDs = db_session.query(CollectParams.ID).all()[inipage:endpage]
                    Datas = transform(IDs)
                    # ORM模型转换json格式
                    jsonCollectParams= json.dumps(Datas)
                    jsonCollectParams = '{"total"' + ":" + str(
                        total) + ',"rows"' + ":\n" + jsonCollectParams + "}"
                    return jsonCollectParams
                else:
                    return ""
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParams数据加载失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)


@app.route('/CollectParams/create', methods=['POST', 'GET'])
def collectParamsCreate():
    if request.method == 'POST':
        try:
            data = request.values
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                tempName = data['TemplateName']
                NodeId = data['NodeID']
                Desc = data['Desc']
                if tempName is None or NodeId is None:
                    return
                CollectParamsTemplateID = db_session.query(CollectParamsTemplate.ID).filter_by(TemplateName=tempName).first()[0]
                OpcTagID = db_session.query(OpcTag.ID).filter_by(NodeID=NodeId).first()[0]
                object = db_session.query(CollectParams).filter(
                    CollectParams.OpcTagID == OpcTagID and CollectParams.CollectParamsTemplateID == CollectParamsTemplateID).first()
                if object is not None:
                    return
                db_session.add(
                    CollectParams(
                        CollectParamsTemplateID= CollectParamsTemplateID,
                        OpcTagID= OpcTagID,
                        Desc=Desc))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据创建失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


@app.route('/CollectParams/delete', methods=['POST', 'GET'])
def collectParamsDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                NodeIDs = json.loads(data['NodeID'])
                for NodeID in NodeIDs:
                    if NodeID['nodeId'] is None or NodeID['nodeId'] == '':
                        continue
                    OpcTagID = db_session.query(OpcTag.ID).filter_by(NodeID=NodeID['nodeId']).first()[0]
                    try:
                        oclass = db_session.query(CollectParams).filter_by(OpcTagID=OpcTagID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
            return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据删除失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


@app.route('/CollectParams/update', methods=['POST', 'GET'])
def collectParamsUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                TempName = data['TemplateName']
                nodeID = data['NodeID']
                TempID = db_session.query(CollectParamsTemplate.ID).filter_by(TemplateName=TempName).first()[0]
                OpcTagID = db_session.query(OpcTag.ID).filter_by(NodeID=nodeID).first()[0]
                ID_byOpcTagID = db_session.query(CollectParams.ID).filter_by(OpcTagID=OpcTagID).first()
                if ID_byOpcTagID is None:
                    ID_byTempID = db_session.query(CollectParams.ID).filter_by(CollectParamsTemplateID=TempID).first()
                    if ID_byTempID is None: # 两者为空则相当于添加一个新的策略
                        oclass = CollectParams()
                        oclass.CollectParamsTemplateID = TempID
                        oclass.OpcTagID = OpcTagID
                        oclass.Desc = data['Desc']
                        db_session.add(oclass)
                        db_session.commit()
                        return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                      ensure_ascii=False)
                    # 改变NodeID的情况
                    oclass = db_session.query(CollectParams).filter_by(ID=ID_byTempID).first()
                    oclass.CollectParamsTemplateID = TempID
                    oclass.OpcTagID = OpcTagID
                    oclass.Desc = data['Desc']
                    db_session.add(oclass)
                    db_session.commit()
                    return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
                # 改变模板的情况
                oclass = db_session.query(CollectParams).filter_by(ID=ID_byOpcTagID).first()
                oclass.OpcTagID = OpcTagID
                oclass.CollectParamsTemplateID = TempID
                oclass.Desc = data['Desc']
                db_session.add(oclass)
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据更新失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectParams/search', methods=['POST', 'GET'])
def collectParamsSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                TemplateName = data['TemplateName']
                tempId = db_session.query(CollectParamsTemplate.ID).filter_by(TemplateName=TemplateName).first()
                IDs = db_session.query(CollectParams.ID).filter_by(CollectParamsTemplateID=tempId).all()
                total = db_session.query(CollectParams.ID).filter_by(CollectParamsTemplateID=tempId).count()
                Datas = transform(IDs)
                jsonTemplates = json.dumps(Datas)
                jsonTemplates = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonTemplates + "}"
                return jsonTemplates
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectParamsTemplate数据查询失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 配置采集策略
@app.route('/Collectionstrategy/config')
def collectionstrategyConfig():
    return render_template('CollectionstrategyConfig.html')

@app.route('/Collectionstrategy/config/find', methods=['POST', 'GET'])
def strategyFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(func.count(Collectionstrategy.ID)).scalar()
                Collectionstrategys = db_session.query(Collectionstrategy).all()[inipage:endpage]
                # ORM模型转换json格式
                jsonStrategys = json.dumps(Collectionstrategys, cls=AlchemyEncoder, ensure_ascii=False)
                jsonStrategys = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonStrategys + "}"
                return jsonStrategys
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询角色列表报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/Collectionstrategy/config/create', methods=['POST', 'GET'])
def strategyCreate():
    if request.method == 'POST':
        try:
            data = request.values
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(
                    Collectionstrategy(
                        Interval=data['Interval'],
                        NodeID=data['NodeID'],
                        StrategyName=data['StrategyName'],
                        Desc=data['Desc']
                    ))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Collectionstrategy数据创建失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/Collectionstrategy/config/delete', methods=['POST', 'GET'])
def strategyDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    StrategyID = int(key)
                    try:
                        oclass = db_session.query(Collectionstrategy).filter_by(ID=StrategyID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Collectionstrategy数据删除失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/Collectionstrategy/config/update', methods=['POST', 'GET'])
def strategyUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                StrategyID = int(data['ID'])
                oclass = db_session.query(Collectionstrategy).filter_by(ID=StrategyID).first()
                oclass.Interval = data['Interval']
                oclass.NodeID = data['NodeID']
                oclass.StrategyName = data['StrategyName']
                oclass.Desc = data['Desc']
                db_session.add(oclass)
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Collectionstrategy数据更新失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/Collectionstrategy/config/search', methods=['POST', 'GET'])
def strategySearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                StrategyName = "%" + data['StrategyName'] + "%"
                Strategyscount = db_session.query(Collectionstrategy).filter(
                    Collectionstrategy.StrategyName.like(StrategyName)).all()
                total = Counter(Strategyscount)
                jsonStrategys = json.dumps(Strategyscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                jsonStrategys = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonStrategys + "}"
                return jsonStrategys
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Collectionstrategy数据查询失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 采集任务
@app.route('/CollectTask/config')
def CollectTaskConfig():
    TemplateNames = []
    TempNames = db_session.query(CollectParamsTemplate.TemplateName).all()
    for name in set(TempNames):
        name = name[0]
        temp_name = {'tempName': name}
        TemplateNames.append(temp_name)
    StrategyNames = []
    straNames = db_session.query(Collectionstrategy.StrategyName).all()
    for strname in set(straNames):
        name = strname[0]
        stra_name = {'straName': name}
        StrategyNames.append(stra_name)
    CollectTaskNames = []
    TaskNames = db_session.query(CollectTask.CollectTaskName).all()
    for taskName in set(TaskNames):
        name = taskName[0]
        task_name = {'taskName': name}
        CollectTaskNames.append(task_name)
    return render_template('CollectTaskConfig.html',
                           TempNames=TemplateNames,
                           StrategyNames=StrategyNames,
                           CollectTaskNames=CollectTaskNames)

@app.route('/CollectTask/config/find', methods=['POST', 'GET'])
def CollectTaskFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(CollectTask.ID).count()
                if total > 0:
                    qDatas = db_session.query(CollectTask).all()[inipage:endpage]
                    # ORM模型转换json格式
                    jsonCollectTask = json.dumps(qDatas, cls=Model.BSFramwork.AlchemyEncoder,
                                                  ensure_ascii=False)
                    jsonCollectTask = '{"total"' + ":" + str(
                        total) + ',"rows"' + ":\n" + jsonCollectTask + "}"
                    return jsonCollectTask
                else:
                    return ""
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "jsonCollectTask数据加载失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)


@app.route('/CollectTask/config/create', methods=['POST', 'GET'])
def CollectTaskCreate():
    if request.method == 'POST':
        try:
            data = request.values
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(
                    CollectTask(
                        CollectTaskName=data['CollectTaskName'],
                        TableName=data['TableName'],
                        Desc=data['Desc'],
                        Enabled = data['Enabled']
                    ))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTask数据创建失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectTask/config/delete', methods=['POST', 'GET'])
def CollectTaskDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    CollectTaskID = int(key)
                    try:
                        oclass = db_session.query(CollectTask).filter_by(ID=CollectTaskID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                        oclass = db_session.query(CollectTaskCollection).filter_by(CollectTaskID=CollectTaskID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTask数据删除失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectTask/config/update', methods=['POST', 'GET'])
def CollectTaskUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                CollectTaskID = int(data['ID'])
                oclass = db_session.query(CollectTask).filter_by(ID=CollectTaskID).first()
                oclass.CollectTaskName = data['CollectTaskName']
                oclass.TableName = data['TableName']
                oclass.Enabled = int(data['Enabled'])
                oclass.Desc = data['Desc']
                db_session.add(oclass)
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTask数据更新失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectTask/config/search', methods=['POST', 'GET'])
def CollectTaskSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                CollectTaskName = "%" + data['CollectTaskName'] + "%"
                Taskscount = db_session.query(CollectTask).filter(
                    CollectTask.CollectTaskName.like(CollectTaskName)).all()
                total = Counter(Taskscount)
                jsonTasks = json.dumps(Taskscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                jsonTasks = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonTasks + "}"
                return jsonTasks
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTask数据查询失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 采集任务配置
@app.route('/CollectTaskConfig/find', methods=['POST', 'GET'])
def collectTaskCollection():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            TaskName = data['CollectTaskName']
            pages = int(data['page'])
            rowsnumber = int(data['rows'])
            inipage = (pages - 1) * rowsnumber + 0
            endpage = (pages - 1) * rowsnumber + rowsnumber
            if TaskName is None or TaskName == '':
                total = db_session.query(CollectTaskCollection).count()
                if total > 0:
                    qDatas = db_session.query(CollectTaskCollection).all()[inipage:endpage]
                    # ORM模型转换json格式
                    jsonCollectTask = json.dumps(qDatas, cls=Model.BSFramwork.AlchemyEncoder,
                                                 ensure_ascii=False)
                    jsonCollectTask = '{"total"' + ":" + str(
                        total) + ',"rows"' + ":\n" + jsonCollectTask + "}"
                    return jsonCollectTask
            if len(json_str) > 10:
                total = db_session.query(CollectTaskCollection).filter_by(CollectTaskName=TaskName).count()
                if total > 0:
                    qDatas = db_session.query(CollectTaskCollection).filter_by(CollectTaskName=TaskName).all()[inipage:endpage]
                    # ORM模型转换json格式
                    jsonCollectTask = json.dumps(qDatas, cls=Model.BSFramwork.AlchemyEncoder,
                                                  ensure_ascii=False)
                    jsonCollectTask = '{"total"' + ":" + str(
                        total) + ',"rows"' + ":\n" + jsonCollectTask + "}"
                    return jsonCollectTask
                else:
                    return
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "jsonCollectTask数据加载失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,ensure_ascii=False)


@app.route('/CollectTaskConfig/create', methods=['POST', 'GET'])
def TaskCollectionCreate():
    if request.method == 'POST':
        try:
            data = request.values
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                TemplateName = data['TemplateName']
                CollectParamsTemplateID = db_session.query(CollectParamsTemplate.ID).filter_by(
                    TemplateName=TemplateName).first()[0]
                StrategyName = data['StrategyName']
                CollectionStrategyID = db_session.query(Collectionstrategy.ID).filter_by(
                    StrategyName=StrategyName).first()[0]
                CollectTaskName = data['CollectTaskName']
                CollectTaskID = db_session.query(CollectTask.ID).filter_by(
                    CollectTaskName=CollectTaskName).first()[0]
                db_session.add(
                    CollectTaskCollection(
                        CollectParamsTemplateID=CollectParamsTemplateID,
                        TemplateName=TemplateName,
                        CollectionStrategyID=CollectionStrategyID,
                        StrategyName=StrategyName,
                        CollectTaskID=CollectTaskID,
                        CollectTaskName=CollectTaskName,
                        Desc=data['Desc'],
                    ))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTaskCollection数据创建失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectTaskConfig/delete', methods=['POST', 'GET'])
def TaskCollectionDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    ID = int(key)
                    try:
                        oclass = db_session.query(CollectTaskCollection).filter_by(ID=ID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTaskCollection数据删除失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectTaskConfig/update', methods=['POST', 'GET'])
def TaskCollectionUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = int(data['ID'])
                TemplateName = data['TemplateName']
                CollectParamsTemplateID = db_session.query(CollectParamsTemplate.ID).filter_by(
                    TemplateName=TemplateName).first()[0]
                StrategyName = data['StrategyName']
                CollectionStrategyID = db_session.query(Collectionstrategy.ID).filter_by(
                    StrategyName=StrategyName).first()[0]
                CollectTaskName = data['CollectTaskName']
                CollectTaskID = db_session.query(CollectTask.ID).filter_by(
                    CollectTaskName=CollectTaskName).first()[0]
                oclass = db_session.query(CollectTaskCollection).filter_by(ID=ID).first()
                oclass.TemplateName = TemplateName
                oclass.CollectParamsTemplateID = CollectParamsTemplateID
                oclass.StrategyName = StrategyName
                oclass.CollectionStrategyID = CollectionStrategyID
                oclass.CollectTaskName = CollectTaskName
                oclass.CollectTaskID = CollectTaskID
                oclass.Desc = data['Desc']
                db_session.add(oclass)
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTaskCollection数据更新失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectTaskConfig/search', methods=['POST', 'GET'])
def TaskCollectionSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                CollectTaskName = "%" + data['CollectTaskName'] + "%"
                count = db_session.query(CollectTaskCollection).filter(
                    CollectTaskCollection.CollectTaskName.like(CollectTaskName)).all()
                total = Counter(count)
                jsonTasks = json.dumps(count, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                jsonTasks = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonTasks + "}"
                return jsonTasks
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "CollectTaskCollection数据查询失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectTaskConfig/load', methods=['POST', 'GET'])
def Taskload():
    if request.method == 'GET':
        try:
            task_dict = make_dynamic_classes()
            return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Task数据加载失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#计划向导生成的计划查询
@app.route('/ZYPlanGuid/searchPlanmanager', methods=['POST', 'GET'])
def searchPlanmanager():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ABatchID = data['ABatchID']  # 批次号
                total = db_session.query(PlanManager).filter(PlanManager.BatchID == ABatchID).count()
                planManagers = db_session.query(PlanManager).filter(PlanManager.BatchID == ABatchID).all()[inipage:endpage]
                planManagers = json.dumps(planManagers, cls=AlchemyEncoder, ensure_ascii=False)
                jsonPlanManagers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + planManagers + "}"
                return jsonPlanManagers
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划向导生成的计划查询报错Error：" + str(e), current_user.Name)

#菜单权限控制
@app.route('/ZYPlanGuid/menuRedirect', methods=['POST', 'GET'])
def menuRedirect():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        try:
            menuName = data['menuName']
            RoleNames = db_session.query(User.RoleName).filter(User.Name == current_user.Name).all()
            flag = 'OK'
            for rN in RoleNames:
                roleID = db_session.query(Role.ID).filter(Role.RoleName == rN[0]).first()
                menus = db_session.query(Menu.ModuleName).join(Role_Menu, isouter=True).filter_by(Role_ID=roleID).all()
                for menu in menus:
                    if(menu[0] == menuName):
                        return 'OK'
                    else:
                        flag = '当前用户没有此操作权限！'
            return flag
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划向导生成计划报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
# 计划向导生成计划
@app.route('/ZYPlanGuid/makePlan', methods=['POST', 'GET'])
def makePlan():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                AProductRuleID = int(data['AProductRuleID'])# 产品定义ID
                APlanWeight = data['APlanWeight']# 计划重量
                APlanDate = data['APlanDate']# 计划生产日期
                ABatchID = data['ABatchID']# 批次号
                ABrandName = data['ABrandName'] # 产品名称
                PLineName = data['PLineName']#生产线名字
                AUnit = data['AUnit']#d单位
                PlanCreate = ctrlPlan('PlanCreate')
                userName = current_user.Name
                ABrandID = AProductRuleID
                re = PlanCreate.createLinePlanManager(AProductRuleID, APlanWeight, APlanDate, ABatchID, ABrandID, ABrandName, PLineName, AUnit, userName)
                re = json.dumps(re)
                return re
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划向导生成计划报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 生产管理部审核计划
@app.route('/ZYPlanGuid/checkPlanManager', methods=['POST', 'GET'])
def checkPlanManager():
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclassplan = db_session.query(PlanManager).filter_by(ID=id).first()
                        oclassplan.PlanStatus = Model.Global.PlanStatus.Checked.value
                        userName = current_user.Name
                        oclassNodeColl = db_session.query(Model.node.NodeCollection).filter_by(oddNum=id, name="审核计划").first()
                        oclassNodeColl.status = Model.node.NodeStatus.PASSED.value
                        oclassNodeColl.oddUser = userName
                        oclassNodeColl.opertionTime = datetime.datetime.now()
                        oclassNodeColl.seq = 1
                        db_session.commit()
                        # oclassW = db_session.query(WorkFlowStatus).filter_by(PlanManageID=id).first()
                        # oclassW.AuditStatus = Model.Global.AuditStatus.Checked.value
                        # oclassW.DescF = "生产管理部审核计划"
                        # Desc = "生产管理部审核计划"
                        # Type = Model.Global.Type.NEW.value
                        # PlanCreate = ctrlPlan('PlanCreate')
                        # wReturn = PlanCreate.createWorkFlowEventPlan(id, userName, Desc, Type)
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        insertSyslog("error", "生产管理部审核计划报错Error：" + str(ee), current_user.Name)
                        return json.dumps([{"status": "Error:" + str(ee)}], cls=AlchemyEncoder, ensure_ascii=False)
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "生产管理部审核计划报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 计划下发查询
@app.route('/RealsePlanManagersearch')
def RealsePlanManagersearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                Name = current_user.Name
                total = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus == "11").count()
                oclass = db_session.query(PlanManager).filter(
                    PlanManager.PlanStatus == "11").order_by(desc("PlanBeginTime")).all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划下发查询报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

# 下发计划生成ZY计划、任务
@app.route('/ZYPlanGuid/createZYPlanZYtask', methods=['POST', 'GET'])
def createZYPlanZYtask():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        PlanCreate = ctrlPlan('PlanCreate')
                        returnmsg = PlanCreate.createZYPlanZYTask(id)
                        if(returnmsg == False):
                            return 'NO'
                        oclassplan = db_session.query(PlanManager).filter_by(ID=id).first()
                        oclassplan.PlanStatus = Model.Global.PlanStatus.Realse.value
                        oclassZYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == oclassplan.BatchID).all()
                        for zyp in oclassZYPlans:
                            zyp.ZYPlanStatus = Model.Global.ZYPlanStatus.Realse.value
                        oclassZYTasks = db_session.query(ZYTask).filter(ZYTask.BatchID == oclassplan.BatchID).all()
                        for task in oclassZYTasks:
                            task.TaskStatus = Model.Global.TASKSTATUS.Realse.value
                        userName = current_user.Name
                        oclassNodeColl = db_session.query(Model.node.NodeCollection).filter_by(oddNum=id,
                                                                                               name="计划下发").first()
                        oclassNodeColl.status = Model.node.NodeStatus.PASSED.value
                        oclassNodeColl.oddUser = userName
                        oclassNodeColl.opertionTime = datetime.datetime.now()
                        oclassNodeColl.seq = 2
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        insertSyslog("error", "下发计划生成ZY计划、任务报错Error" + string(ee), current_user.Name)
                        return 'NO'
                return 'OK'
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "下发计划生成ZY计划、任务报错Error：" + str(e), current_user.Name)
            return 'NO'


# 下发后的计划撤回，删除ZYplan，ZYtask
@app.route('/ZYPlanGuid/RecallPlan', methods=['POST', 'GET'])
def RecallPlan():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        ABatchID = id  # 批次号
                        planM = db_session.query(PlanManager).filter_by(BatchID=ABatchID).first()
                        if (planM.PlanStatus != "20"):
                            return "只能是已下发状态的计划才能撤回！"
                        else:
                            pass
                        zYPlans = db_session.query(ZYPlan).filter_by(BatchID=ABatchID).all()
                        for zYPlan in zYPlans:
                            if (zYPlan.LockStatus == "10"):
                                return "计划状态已锁定，不允许撤回！"
                            else:
                                pass
                        zYTasks = db_session.query(ZYTask).filter_by(BatchID=ABatchID).all()
                        for zYTask in zYTasks:
                            if (zYTask.LockStatus == "10"):
                                return "任务状态已锁定，不允许撤回！"
                            else:
                                pass
                        for zYPl in zYPlans:
                            try:
                                oclass = db_session.query(ZYPlan).filter_by(ID=zYPl.ID).first()
                                db_session.delete(oclass)
                                oclassZ = db_session.query(WorkFlowEventZYPlan).filter_by(WorkFlowEventZYPlan.ZYPlanID == zYPl.ID).first()
                                db_session.delete(oclassZ)
                                db_session.commit()
                            except Exception as ee:
                                db_session.rollback()
                                logger.error(ee)
                                insertSyslog("error", "删除批次计划信息报错Error" + string(ee), current_user.Name)
                                return json.dumps([{"status": "Error:" + str(ee)}], cls=AlchemyEncoder, ensure_ascii=False)
                        for zYTask in zYTasks:
                            try:
                                oclass = db_session.query(ZYTask).filter_by(ID=zYTask.ID).first()
                                db_session.delete(oclass)
                                db_session.commit()
                            except Exception as ee:
                                db_session.rollback()
                                print(ee)
                                logger.error(ee)
                                insertSyslog("error", "删除批次任务信息报错Error" + string(ee), current_user.Name)
                                return json.dumps([{"status": "Error:" + str(ee)}], cls=AlchemyEncoder, ensure_ascii=False)
                        planM.PlanStatus = Model.Global.PlanStatus.Recall.value
                        userName = current_user.Name
                        oclassNodeColl = db_session.query(Model.node.NodeCollection).filter_by(oddNum=id,
                                                                                               name=Model.node.flowPathNameJWXSP.B.value).first()
                        oclassNodeColl.status = Model.node.NodeStatus.NOTEXE.value
                        oclassNodeColl.oddUser = userName
                        oclassNodeColl.opertionTime = datetime.datetime.now()
                        oclassNodeColl.seq = 0
                        oclassNodeCollA = db_session.query(Model.node.NodeCollection).filter_by(oddNum=id,
                                                                                               name=Model.node.flowPathNameJWXSP.A.value).first()
                        oclassNodeCollA.status = Model.node.NodeStatus.NOTEXE.value
                        oclassNodeCollA.oddUser = userName
                        oclassNodeCollA.opertionTime = datetime.datetime.now()
                        oclassNodeCollA.seq = 0
                        db_session.commit()
                        return 'OK'
                    except Exception as e:
                        db_session.rollback()
                        print(e)
                        logger.error(e)
                        insertSyslog("error", "撤回批次计划报错Error：" + str(e), current_user.Name)
                        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "撤回批次计划报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 计划向导获取批次物料明细
@app.route('/ZYPlanGuid/CriticalMaterials', methods=['POST', 'GET'])
def criticalMaterials():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ABatchID = data['ABatchID']
                total = db_session.query(ZYPlanMaterial).filter(ZYPlanMaterial.BatchID == ABatchID).count()
                zyMaterials = db_session.query(ZYPlanMaterial).filter(ZYPlanMaterial.BatchID == ABatchID).all()[inipage:endpage]
                jsonzyMaterials = json.dumps(zyMaterials, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzyMaterials = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonzyMaterials + "}"
                return jsonzyMaterials
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划向导获取批次物料明细报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 批次号判重
@app.route('/ZYPlanGuid/isBatchNumber', methods=['POST', 'GET'])
def isBatchNumber():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                isExist = ''#前台判断标识：OK为批次号可用，NO为此批次号已存在
                ABatchID = data['ABatchID']
                BatchID = db_session.query(PlanManager.BatchID).filter(PlanManager.BatchID == ABatchID).first()
                if(BatchID == None):
                    isExist = 'OK'
                else:
                    isExist = 'NO'
                isExist = json.dumps(isExist)
                return isExist
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "批次号判重报错Error：" + str(e), current_user.Name)
            return 'NO'

# 计划向导重量校验
@app.route('/ZYPlanGuid/weightCheck', methods=['POST', 'GET'])
def weightCheck():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                PUID = data['PUID']
                LowLimit,HighLimit = db_session.query(ProductControlTask.LowLimit, ProductControlTask.HighLimit).filter(ProductControlTask.PUID == PUID).first()
                return LowLimit,HighLimit
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划向导重量校验报错Error：" + str(e), current_user.Name)

# 获取批次计划信息
@app.route('/ZYPlanGuid/searchZYPlan', methods=['POST', 'GET'])
def searchZYPlan():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ABatchID = data['ABatchID']#批次号
                APlanDate = data['APlanDate']#计划日期
                total = db_session.query(ZYPlan).filter(ZYPlan.BatchID == ABatchID, ZYPlan.PlanDate == APlanDate).count()
                zYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == ABatchID, ZYPlan.PlanDate == APlanDate).order_by(desc("EnterTime")).all()[
                              inipage:endpage]
                jsonzYPlans = json.dumps(zYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzYPlans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonzYPlans + "}"
                return jsonzYPlans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "获取批次计划信息报错Error：" + str(e), current_user.Name)

# 前处理段监控
@app.route('/PreprocessingSectionMonitor')
def Preprocessing():
    return render_template('PreprocessingSectionMonitor.html')

# 运输段监控
@app.route('/TransportMonitor')
def Transport():
    return render_template('TransportMonitor.html')

# 投料段监控
@app.route('/FeedingSectionMonitor')
def FeedingSection():
    return render_template('FeedingSectionMonitor.html')

#生产线监控
@app.route('/processMonitorLine')
def processMonitor():
    return render_template('processMonitorLine.html')

def get_data_from_realtime_Decocting(batch,brand,tankOver,status):
    try:
        pool = redis.ConnectionPool(host=constant.REDIS_HOST, password=constant.REDIS_PASSWORD)  # 实现一个连接池
        redis_conn = redis.Redis(connection_pool=pool)
        Batch = redis_conn.get(batch)
        Brand = redis_conn.get(brand)
        TankOver = redis_conn.get(tankOver)
        Status = redis_conn.get(status)
        return Batch, Brand, TankOver, Status
    except Exception as e:
        print('连接实时数据服务器失败!')
        print('详细信息为:%s' % str(e))
        return

# 生产监控提取段——健胃消食片
@app.route('/processMonitorLine/extract')
def extract():
    if request.method == 'GET':
        try:
            Equips_data = {}
            equip1 = db_session.query(ProductionMonitor).filter_by(EQPName='提取设备一').first()
            Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-1',brand='t|PdtNR1101-1',tankOver='t|R1101_1_TQKGG_SB_Pat_CloseSwith',status='t|SB_R1101_1_StartProduction')
            equip1_data = {'a1': Batch,'a2': Brand,'a3':equip1.EQPCode,'a5':TankOver,'a6':Status}
            Equips_data.update(equip1_data)

            equip2 = db_session.query(ProductionMonitor).filter_by(EQPName='提取设备二').first()
            Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-2', brand='t|PdtNR1101-2',
                                                                    tankOver='t|R1101_2_TQKGG_SB_Pat_CloseSwith',
                                                                    status='t|SB_R1101_2_StartProduction')
            equip2_data = {'b1': Batch, 'b2': Brand, 'b3': equip2.EQPCode, 'b5': TankOver, 'b6': Status}
            Equips_data.update(equip2_data)

            equip3 = db_session.query(ProductionMonitor).filter_by(EQPName='提取设备三').first()
            Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-3', brand='t|PdtNR1101-3',
                                                                    tankOver='t|R1101_3_TQKGG_SB_Pat_CloseSwith',
                                                                    status='t|SB_R1101_3_StartProduction')
            equip3_data = {'c1': Batch, 'c2': Brand, 'c3': equip3.EQPCode, 'c5': TankOver, 'c6': Status}
            Equips_data.update(equip3_data)

            equip4 = db_session.query(ProductionMonitor).filter_by(EQPName='提取设备四').first()
            Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-4', brand='t|PdtNR1101-4',
                                                                    tankOver='t|R1101_4_TQKGG_SB_Pat_CloseSwith',
                                                                    status='t|SB_R1101_4_StartProduction')
            equip4_data = {'d1': Batch, 'd2': Brand, 'd3': equip4.EQPCode, 'd5': TankOver, 'd6': Status}
            Equips_data.update(equip4_data)

            equip5 = db_session.query(ProductionMonitor).filter_by(EQPName='提取设备五').first()
            Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-5', brand='t|PdtNR1101-5',
                                                                    tankOver='t|R1101_5_TQKGG_SB_Pat_CloseSwith',
                                                                    status='t|SB_R1101_5_StartProduction')
            equip5_data = {'e1': Batch, 'e2': Brand, 'e3': equip5.EQPCode, 'e5': TankOver, 'e6': Status}
            Equips_data.update(equip5_data)

            equip6 = db_session.query(ProductionMonitor).filter_by(EQPName='提取设备六').first()
            Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-6', brand='t|PdtNR1101-6',
                                                                    tankOver='t|R1101_6_TQKGG_SB_Pat_CloseSwith',
                                                                    status='t|SB_R1101_6_StartProduction')
            equip6_data = {'f1': Batch, 'f2': Brand, 'f3': equip6.EQPCode, 'f5': TankOver, 'f6': Status}
            Equips_data.update(equip6_data)
            jsonsz = json.dumps(Equips_data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsonsz
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "生长线监控提取段数据获取报错Error：" + str(e), current_user.Name)

def get_data_from_realtime_Standing(name,Unit=None):
    try:
        # 新建一个客户端,并在初始化的时候进行连接实时数据服务
        pool = redis.ConnectionPool(host=constant.REDIS_HOST, password=constant.REDIS_PASSWORD)  # 实现一个连接池
        share_data = redis.Redis(connection_pool=pool)
        if Unit == 'Concentrate':
            batch_tag = 't|MVRPC_' + name[-1]
            brand_tag = 't|MVRPM_' + name[-1]
            Batch = share_data.get(batch_tag)
            Brand = share_data.get(brand_tag)
            return Batch,Brand
        batch_tag = 't|PC' + name[4:]
        brand_tag = 't|PM' + name[4:]
        height_tag = 't|' + name[4:] + 'LT'
        volume_tag = 't|' + name[4:] + 'JZ'
        feed_time_tag = 't|' + name[4:] + 'MIN'

        Batch = share_data.get(batch_tag)
        Brand = share_data.get(brand_tag)
        Height = share_data.get(height_tag)
        Feed_time = share_data.get(feed_time_tag)
        Volume = share_data.get(volume_tag)
        return Batch, Brand, Height, Feed_time, Volume
    except Exception as e:
        print('连接实时数据服务器失败!')
        print('详细信息为:%s' % str(e))
        return

def get_integer(object,count=None):
    if object is None:
        return object
    return round(float(object),count)

def standing_consentrate_collect(a,b,c,d,e,f,g,h,j):
    Equips_data = {}
    equip1 = db_session.query(ProductionMonitor).filter_by(EQPName=a).first()
    Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-1', brand='t|PdtNR1101-1',
                                                                      tankOver='t|R1101_1_TQKGG_SB_Pat_CloseSwith',
                                                                      status='t|SB_R1101_1_StartProduction')
    equip1_data = {'a1': Batch, 'a2': Brand, 'a3': equip1.EQPCode, 'a5': TankOver, 'a6': Status}
    Equips_data.update(equip1_data)

    equip2 = db_session.query(ProductionMonitor).filter_by(EQPName=b).first()
    Batch, Brand, Status, Feed_time, Volume = get_data_from_realtime_Standing(name=b)
    equip2_data = {'b1': Batch, 'b2': get_integer(Feed_time),'b5': equip2.EQPCode, 'b6':Status, 'b7': get_integer(Volume,1)}
    Equips_data.update(equip2_data)

    equip3 = db_session.query(ProductionMonitor).filter_by(EQPName=c).first()
    Batch, Brand, Status, Feed_time, Volume = get_data_from_realtime_Standing(name=c)
    equip3_data = {'c1': Batch, 'c2': get_integer(Feed_time), 'c5': equip3.EQPCode, 'c6': Status,'c7': get_integer(Volume,1)}
    Equips_data.update(equip3_data)

    equip4 = db_session.query(ProductionMonitor).filter_by(EQPName=d).first()
    Batch, Brand, Status, Feed_time, Volume = get_data_from_realtime_Standing(name=d)
    equip4_data = {'d1': Batch, 'd2': get_integer(Feed_time), 'd5': equip4.EQPCode, 'd6': Status,'d7': get_integer(Volume,1)}
    Equips_data.update(equip4_data)

    equip5 = db_session.query(ProductionMonitor).filter_by(EQPName=e).first()
    Batch, Brand, TankOver, Status = get_data_from_realtime_Decocting(batch='t|BhNR1101-1', brand='t|PdtNR1101-1',
                                                            tankOver='t|R1101_1_TQKGG_SB_Pat_CloseSwith',
                                                            status='t|SB_R1101_1_StartProduction')
    equip5_data = {'e1': Batch, 'e2': Brand, 'e3': equip5.EQPCode, 'e5': TankOver, 'e6': Status}
    Equips_data.update(equip5_data)

    equip6 = db_session.query(ProductionMonitor).filter_by(EQPName=f).first()
    Batch, Brand, Status, Feed_time, Volume = get_data_from_realtime_Standing(name=f)
    equip6_data = {'f1': Batch, 'f2': get_integer(Feed_time), 'f5': equip6.EQPCode, 'f6': Status,'f7': get_integer(Volume,1)}
    Equips_data.update(equip6_data)

    equip7 = db_session.query(ProductionMonitor).filter_by(EQPName=g).first()
    Batch, Brand, Status, Feed_time, Volume = get_data_from_realtime_Standing(name=g)
    equip7_data = {'g1': Batch, 'g2': get_integer(Feed_time), 'g5': equip7.EQPCode, 'g6': Status,'g7': get_integer(Volume,1)}
    Equips_data.update(equip7_data)

    equip8 = db_session.query(ProductionMonitor).filter_by(EQPName=h).first()
    Batch, Brand, Status, Feed_time, Volume = get_data_from_realtime_Standing(name=h)
    equip8_data = {'h1': Batch, 'h2': get_integer(Feed_time), 'h5': equip8.EQPCode, 'h6': Status,'h7': get_integer(Volume,1)}
    Equips_data.update(equip8_data)

    equip9 = db_session.query(ProductionMonitor).filter_by(EQPName=j).first()
    Batch, Brand = get_data_from_realtime_Standing(j,Unit='Concentrate')
    equip9_data = {'i1': Batch, 'i2': Brand, 'i3': equip9.EQPCode}
    Equips_data.update(equip9_data)
    return Equips_data

# 生产监控静止浓缩段-健胃消食片
@app.route('/processMonitorLine/StandingAndConsentrate')
def StandingAndConsentrate():
    if request.method == 'GET':
        try:
            data = request.values
            group = data['group']
            if group is None:
                return
            if group == 'A':
                equipments_data = standing_consentrate_collect(a='提取设备一', b='静置设备1-1', c='静置设备1-2', d='静置设备1-3',
                                                               e='提取设备二', f='静置设备2-1', g='静置设备2-2', h='静置设备2-3',
                                                               j='浓缩设备1')
                jsonsz = json.dumps(equipments_data, cls=AlchemyEncoder, ensure_ascii=False)
                return jsonsz
            if group == 'B':
                equipments_data = standing_consentrate_collect(a='提取设备三', b='静置设备3-1', c='静置设备3-2', d='静置设备3-3',
                                                               e='提取设备四', f='静置设备4-1', g='静置设备4-2', h='静置设备4-3',
                                                               j='浓缩设备2')
                jsonsz = json.dumps(equipments_data, cls=AlchemyEncoder, ensure_ascii=False)
                return jsonsz
            if group == 'C':
                equipments_data = standing_consentrate_collect(a='提取设备五', b='静置设备5-1', c='静置设备5-2', d='静置设备5-3',
                                                               e='提取设备六', f='静置设备6-1', g='静置设备6-2', h='静置设备6-3',
                                                               j='浓缩设备3')
                jsonsz = json.dumps(equipments_data, cls=AlchemyEncoder, ensure_ascii=False)
                return jsonsz
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "生长线监控静止浓缩段数据获取报错Error：" + str(e), current_user.Name)

def get_data_Total_MixtureAndDry(num,Unit=None):
    try:
        pool = redis.ConnectionPool(host=constant.REDIS_HOST, password=constant.REDIS_PASSWORD)  # 实现一个连接池
        share_data = redis.Redis(connection_pool=pool)

        if Unit == 'Total_Mixture':
            batch_tag = 't|ZHPC_' + num
            brand_tag = 't|ZHPM_' + num
            temp_tag = 't|' + num + '_zonghunt'
            height_tag = 't|' + num + '_zonghunl'
            volume_tag = 't|ZH_' + num + 'TJ'
            flow_tag = 't|' + num + '_zonghunf'

            Batch = share_data.get(batch_tag)
            Brand = share_data.get(brand_tag)
            Height = share_data.get(height_tag)
            Volume = share_data.get(volume_tag)
            Temperature = share_data.get(temp_tag)
            Flow = share_data.get(flow_tag)
            return Batch, Brand, Height, Volume,Temperature,Flow
        if Unit == 'Dry':
            batch_tag = 't|PGPC_' + num
            brand_tag = 't|PGPM_' + num

            Batch = share_data.get(batch_tag)
            Brand = share_data.get(brand_tag)
            return Batch, Brand
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "生产监控总混干燥段获取数据报错Error：" + str(e), current_user.Name)

# 生产监控总混干燥段-健胃消食片
@app.route('/processMonitorLine/Total_MixtureAndDry')
def Total_MixtureAndDry():
    if request.method == 'GET':
        try:
            Equips_data = {}
            Batch, Brand, Height, Volume, Temperature,Flow = get_data_Total_MixtureAndDry(num='1',Unit='Total_Mixture')
            equip1_data = {'a1': Batch, 'a2': Brand, 'a3': get_integer(Height,1), 'a4': get_integer(Volume,1),
                           'a5': get_integer(Flow,1),'a6': get_integer(Temperature,1)}
            Equips_data.update(equip1_data)

            Batch, Brand = get_data_Total_MixtureAndDry(num='1',Unit='Dry')
            equip2_data = {'b1': Batch, 'b2': Brand}
            Equips_data.update(equip2_data)

            Batch, Brand, Height, Volume, Temperature, Flow = get_data_Total_MixtureAndDry(num='2',Unit='Total_Mixture')
            equip3_data = {'c1': Batch, 'c2': Brand, 'c3': get_integer(Height, 1), 'c4': get_integer(Volume, 1),
                           'c5': get_integer(Flow, 1), 'c6': get_integer(Temperature, 1)}
            Equips_data.update(equip3_data)

            Batch, Brand = get_data_Total_MixtureAndDry(num='2', Unit='Dry')
            equip4_data = {'d1': Batch, 'd2': Brand}
            Equips_data.update(equip4_data)
            jsonsz = json.dumps(Equips_data, cls=AlchemyEncoder, ensure_ascii=False)
            return jsonsz
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "生产监控总混干燥段返回数据报错Error：" + str(e), current_user.Name)




#任务确认
@app.route('/taskConfirm')
def taskConfirm():
    if request.method == 'GET':
        # data = request.values
        # ID = data['ID']
        # name = data['name']
        # BatchID = db_session.query(PlanManager.BatchID).filter(PlanManager.ID == ID).first()
        # PUID = db_session.query(ProductUnitRoute.PUID).filter(ProductUnitRoute.PDUnitRouteName == name).first()
        # zytasks = []
        # tasks = db_session.query(ZYTask).filter(ZYTask.PUID == PUID[0], ZYTask.BatchID == BatchID[0]).all()
        # for task in set(tasks):
        #     tas = {'ZYTask': task}
        #     zytasks.append(tas)
        # print(zytasks)
        return render_template('taskConfirm.html')

#任务确认获取工艺段
@app.route('/processMonitorLine/taskConfirmPuid', methods=['POST', 'GET'])
def taskConfirmPuidDate():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            # puids = db_session.query(ZYPlan.PUID).filter().all()
            # puidnews = []
            # for id in puids:
            #     if id not in puidnews:
            #         puidnews.append(id)
            # sz = []
            # for puid in puidnews:
            #     APUID = puid  # 工艺段编码
            #     PDCtrlTaskName = db_session.query(ProductControlTask.PDCtrlTaskName).filter_by(PUID=APUID).first()
            #     PUID = str(APUID)
            #     sz.append({"id": PUID[1:-2], "text": PDCtrlTaskName})
            sz = []
            ProcessUnits = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
            for procc in ProcessUnits:
                sz.append({"id": procc.ID, "text": procc.PUName})
            jsonsz = json.dumps(sz, cls=AlchemyEncoder, ensure_ascii=False)
            return jsonsz
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "任务确认获取工艺段报错Error：" + str(e), current_user.Name)

# 任务确认查询计划
@app.route('/processMonitorLine/planConfirmSearch', methods=['POST', 'GET'])
def planConfirmSearch():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                APUID = data['PUID']  # 工艺段编码
                if(APUID == "" or APUID == None):
                    total = db_session.query(ZYPlan).filter(ZYPlan.ZYPlanStatus.in_((31, 40, 50))).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.ZYPlanStatus.in_((31, 40, 50))).order_by(desc("EnterTime")).all()[inipage:endpage]
                else:
                    total = db_session.query(ZYPlan).filter(ZYPlan.ZYPlanStatus.in_((31, 40, 50)),
                                                            ZYPlan.PUID == APUID).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.ZYPlanStatus.in_((31, 40, 50)),
                                                              ZYPlan.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
                jsonZYPlans = json.dumps(ZYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonZYPlans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonZYPlans + "}"
                return jsonZYPlans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "任务确认查询计划报错Error：" + str(e), current_user.Name)

# #任务确认查询任务
# @app.route('/processMonitorLine/taskConfirmSearch', methods=['POST', 'GET'])
# def taskConfirmSearch():
#     if request.method == 'GET':
#         data = request.values  # 返回请求中的参数和form
#         try:
#             jsonstr = json.dumps(data.to_dict())
#             if len(jsonstr) > 10:
#                 pages = int(data['page'])  # 页数
#                 rowsnumber = int(data['rows'])  # 行数
#                 inipage = (pages - 1) * rowsnumber + 0  # 起始页
#                 endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
#                 APUID = data['PUID']  # 工艺段编码
#                 TaskStatus = data['TaskStatus']  # 任务的执行状态
#                 BatchID = data['BatchID']#批次号
#                 if(APUID == "" and TaskStatus == ""):
#                     total = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32,40,50))).count()
#                     ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32,40,50))).order_by(desc("EnterTime")).all()[inipage:endpage]
#                 elif(APUID != "" and TaskStatus == "" and BatchID == ""):
#                     total = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32, 40, 50)),
#                                                             ZYTask.PUID == APUID).count()
#                     ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32, 40, 50)),
#                                                               ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
#                 elif(APUID != "" and TaskStatus == "" and BatchID != ""):
#                     total = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
#                                                             ZYTask.TaskStatus.in_((32, 40, 50)),
#                                                             ZYTask.PUID == APUID).count()
#                     ZYTasks = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
#                                                               ZYTask.TaskStatus.in_((32, 40, 50)),
#                                                               ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
#                 elif (APUID == "" and TaskStatus != ""):
#                     total = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus).count()
#                     ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus).order_by(desc("EnterTime")).all()[inipage:endpage]
#                 elif (APUID != "" and TaskStatus != "" and BatchID == ""):
#                     total = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus,
#                                                             ZYTask.PUID == APUID).count()
#                     ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus,
#                                                               ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
#                 elif (APUID != "" and TaskStatus != "" and BatchID != ""):
#                     total = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
#                                                             ZYTask.TaskStatus == TaskStatus,
#                                                             ZYTask.PUID == APUID).count()
#                     ZYTasks = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
#                                                               ZYTask.TaskStatus == TaskStatus,
#                                                               ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
#                 jsonZYTasks = json.dumps(ZYTasks, cls=AlchemyEncoder, ensure_ascii=False)
#                 jsonZYTasks = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonZYTasks + "}"
#                 return jsonZYTasks
#         except Exception as e:
#             print(e)
#             logger.error(e)
#             insertSyslog("error", "获取任务确认的任务列表报错Error：" + str(e), current_user.Name)

# 任务确认查询任务
@app.route('/processMonitorLine/taskConfirmSearch', methods=['POST', 'GET'])
def taskConfirmSearch():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                data = request.values
                ID = data['ID']
                name = data['name']
                planM = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                BrandID = planM.BrandID
                BatchID = planM.BatchID
                PUID = db_session.query(ProductUnitRoute.PUID).filter(ProductUnitRoute.PDUnitRouteName == name, ProductUnitRoute.ProductRuleID == BrandID).first()
                total = db_session.query(ZYTask.ID).filter(ZYTask.PUID == PUID[0], ZYTask.BatchID == BatchID).count()
                tasks = db_session.query(ZYTask).filter(ZYTask.PUID == PUID[0], ZYTask.BatchID == BatchID).all()[inipage:endpage]
                jsonZYTasks = json.dumps(tasks, cls=AlchemyEncoder, ensure_ascii=False)
                jsonZYTasks = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonZYTasks + "}"
                return jsonZYTasks
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "获取任务确认的任务列表报错Error：" + str(e), current_user.Name)
#任务确认工艺段下的所有设备
@app.route('/processMonitorLine/searchAllEquipments', methods=['POST', 'GET'])
def searchAllEquipments():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                APUID = data['PUID']  # 工艺段编码
                dataequipmentNames = []
                equipmentNames = db_session.query(Equipment.ID,Equipment.EQPName).filter(Equipment.PUID == APUID).all()
                for equip in equipmentNames:
                    li = list(equip)
                    id = li[0]
                    name = li[1]
                    equipName = {'id': id, 'text': name}
                    dataequipmentNames.append(equipName)
                dataequipmentNames = json.dumps(dataequipmentNames, cls=AlchemyEncoder, ensure_ascii=False)
                return dataequipmentNames
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "任务确认工艺段下的所有设备报错Error：" + str(e), current_user.Name)

#任务确认保存设备code
@app.route('/processMonitorLine/saveEQPCode', methods=['POST', 'GET'])
def saveEQPCode():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                EQPCode = data['EQPCode']
                ID = data['ID']
                oclass = db_session.query(ZYTask).filter(ZYTask.ID == ID).first()
                PUID = oclass.PUID
                oclasstasks = db_session.query(ZYTask).filter(ZYTask.PUID == PUID,
                                                              ZYTask.BatchID == oclass.BatchID).all()
                equipments = db_session.query(Equipment).filter(Equipment.PUID == PUID).all()
                code1 = ""
                code2 = ""
                code3 = ""
                code4 = ""
                code5 = ""
                code6 = ""
                for i in range(len(equipments)):
                    if(i == 0):
                        code1 = equipments[i].ID
                    elif(i == 1):
                        code2 = equipments[i].ID
                    elif(i == 2):
                        code3 = equipments[i].ID
                    elif(i == 3):
                        code4 = equipments[i].ID
                    elif(i == 4):
                        code5 = equipments[i].ID
                    elif(i == 5):
                        code6 = equipments[i].ID
                if(EQPCode == None or EQPCode == ""):
                    for i in range(len(oclasstasks)):
                        if (i == 0):
                            oclasstasks[i].EquipmentID = code1
                            oclasstasks[i].TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                        elif (i == 1):
                            oclasstasks[i].EquipmentID = code2
                            oclasstasks[i].TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                        elif (i == 2):
                            oclasstasks[i].EquipmentID = code3
                            oclasstasks[i].TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                        elif (i == 3):
                            oclasstasks[i].EquipmentID = code4
                            oclasstasks[i].TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                        elif (i == 4):
                            oclasstasks[i].EquipmentID = code5
                            oclasstasks[i].TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                        elif (i == 5):
                            oclasstasks[i].EquipmentID = code6
                            oclasstasks[i].TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                else:
                    oclass.EquipmentID = EQPCode
                    oclass.TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                db_session.commit()
                IDm = db_session.query(PlanManager.ID).filter(PlanManager.BatchID == oclass.BatchID).first()
                IDm = IDm[0]
                flag = "TRUE"
                for task in oclasstasks:
                    if(task.TaskStatus != Model.Global.TASKSTATUS.COMFIRM.value):
                        flag = "FALSE"
                nameP = db_session.query(ProductUnitRoute.PDUnitRouteName).filter(ProductUnitRoute.PUID == PUID).first()
                na = nameP[0]
                if(flag == "TRUE"):
                    if(na == "备料段"):
                        aa = '（备料段）任务确认'
                        updateNodeA(IDm,aa)
                    elif(na == "煎煮段"):
                        bb = '（煎煮段）任务确认'
                        updateNodeA(IDm, bb)
                    elif (na == "浓缩段"):
                        cc = '（浓缩段）任务确认'
                        updateNodeA(IDm, cc)
                    elif (na == "喷雾干燥段"):
                        dd = '（喷雾干燥段）任务确认'
                        updateNodeA(IDm, dd)
                    elif (na == "收粉段"):
                        ee = '（收粉段）任务确认'
                        updateNodeA(IDm, ee)
                    elif (na == "醇沉段"):
                        ff = '（醇沉段）任务确认'
                        updateNodeA(IDm, ff)
                    elif (na == "单效浓缩段"):
                        gg = '（单效浓缩段）任务确认'
                        updateNodeA(IDm, gg)
                    elif (na == "收膏段"):
                        hh = '（收膏段）任务确认'
                        updateNodeA(IDm, hh)
                return "OK"
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "任务确认保存设备code报错Error：" + str(e), current_user.Name)
            return "NO"
def updateNodeA(id,name):
    try:
        noclass = db_session.query(Model.node.NodeCollection).filter(Model.node.NodeCollection.name == name,
                                                                     Model.node.NodeCollection.oddNum == id).first()
        noclass.status = Model.node.NodeStatus.PASSED.value
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        print(e)
        logger.error(e)
        insertSyslog("error", "更新NodeCollection报错Error：" + str(e), current_user.Name)

#任务确认查询设备下任务
@app.route('/processMonitorLine/searchTasksByEquipmentID', methods=['POST', 'GET'])
def searchTasksByEquipmentID():
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                EquipmentID = data['EquipmentID']
                taskIDs = db_session.query(ZYTask.TaskID).filter(ZYTask.EquipmentID == EquipmentID).all()
                jsontaskIDs = json.dumps(taskIDs, cls=AlchemyEncoder, ensure_ascii=False)
                return jsontaskIDs
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "任务确认查询设备下任务报错Error：" + str(e), current_user.Name)


# 计划审核页面
@app.route('/ZYPlanGuid/checkplanmanager')
def checkplanmanager():
    return render_template('checkplanmanager.html')

#计划审核查询
@app.route('/allPlanManagers/searchcheckplanmanager', methods=['POST', 'GET'])
def searchcheckplanmanager():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ABatchID = data['BatchID']  # 批次号
                if (ABatchID == None or ABatchID == ""):
                    total = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus.in_((10, 40))).count()
                    planManagers = db_session.query(PlanManager).filter(PlanManager.PlanStatus.in_((10, 40))).order_by(desc("ID")).all()[
                                   inipage:endpage]
                else:
                    total = db_session.query(PlanManager).filter(PlanManager.BatchID == ABatchID,
                                                                 PlanManager.PlanStatus.in_((10, 40))).count()
                    planManagers = db_session.query(PlanManager).filter(PlanManager.BatchID == ABatchID,
                                                                        PlanManager.PlanStatus.in_((10, 40))).order_by(desc("ID")).all()[
                                   inipage:endpage]
                planManagers = json.dumps(planManagers, cls=AlchemyEncoder, ensure_ascii=False)
                jsonPlanManagers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + planManagers + "}"
                return jsonPlanManagers
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划向导生成的计划查询报错Error：" + str(e), current_user.Name)

# 准备工作查询
@app.route('/ZYPlanGuid/ConfirmSearchInfo', methods=['POST', 'GET'])
def ConfirmSearchInfo():
    if request.method == 'GET':
        data = request.values
        try:
            oclass = db_session.query(ReadyWork).filter().all()
            return json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "准备工作查询报错Error：" + str(e), current_user.Name)

# 中控确认保存信息
@app.route('/ZYPlanGuid/controlConfirmSaveInfo', methods=['POST', 'GET'])
def controlConfirmSaveInfo():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                ZYPlanID = int(data["ZYPlanID"])
                oclassR = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ZYPlanID, ReadyWork.ProductionFlag == "0").all()
                for oc in oclassR:
                    oc.IsCheck = "0"
                for i in range(len(jsonnumber)-1):
                    ID = int(jsonnumber[i])
                    oclass = db_session.query(ReadyWork).filter(ReadyWork.ID == ID).first()
                    oclass.IsCheck = "1"
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "中控确认保存信息报错Error：" + str(e), current_user.Name)

#草珊瑚含片
@app.route('/ZYPlanGuid/cshflowtu')
def cshflowtu():
    return render_template('cshflowtu.html')

#健胃消食片
@app.route('/ZYPlanGuid/jwxspflowtu')
def jwxspflowtu():
    return render_template('jwxspflowtu.html')

#生产监控详情页面
@app.route('/ZYPlanGuid/processMonitorLineDetails')
def processMonitorLineDetails():
    return render_template('processMonitorLineDetails.html')

def GetEquipmentData():
    # productUnit = db_session.query(ProductUnit.ID).filter_by(PDUnitName='前处理段')
    # PUID = db_session.query(Equipment.PUID).filter_by(PUID=)
    # ProcessSection = db_session.query(Equipment.Equipment_State).all()
    pass

def Productmonitor():
    t = Timer(2, GetEquipmentData)
    t.start()
app.add_template_global(Productmonitor, 'Productmonitor')

#操作人确认
@app.route('/ZYPlanGuid/operateConfirm', methods=['POST', 'GET'])
def operateConfirm():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data['ID']#计划ID
                PName = data['PName']#计划名称
                PUName = data['PUName']#计划明细名称
                planM = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                BrandName = planM.BrandName
                if(PName == "备料"):
                    PName = '备料段'
                    if(PUName == "生产前的准备"):
                        name = '（备料段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif(PUName == "备料开始"):
                        name = '备料操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif(PUName == "备料结束清场"):
                        name = '（备料段）生产结束清场（操作人）'
                        return operateflow(ID, name, PName)
                elif(PName == "煎煮"):
                    PName = '煎煮段'
                    if(PUName == "生产前的准备"):
                        name = '（煎煮段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif(PUName == "煎煮开始"):
                        name = '煎煮开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif(PUName == "静置开始"):
                        name = '静置开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif(PUName == "煎煮结束清场"):
                        name = '（煎煮段）生产结束清场（操作人）'
                        return operateflow(ID, name, PName)
                elif(PName == "浓缩"):
                    PName = "浓缩段"
                    if (PUName == "生产前的准备"):
                        name = '（浓缩段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "浓缩开始"):
                        name = '浓缩开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "浓缩结束清场"):
                        name = '浓缩结束清场（操作人）'
                        return operateflow(ID, name, PName)
                elif(PName == "喷雾干燥"):
                    PName = "喷雾干燥段"
                    if (PUName == "生产前的准备"):
                        name = '（喷雾干燥段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "喷雾干燥开始"):
                        name = '喷雾干燥开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "喷雾干燥结束清场"):
                        name = '喷雾干燥结束，按SOP清场（操作人）'
                        return operateflow(ID, name, PName)
                elif(PName == "收粉"):
                    PName = '收粉段'
                    if (PUName == "生产前的准备"):
                        name = '（收粉段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "收粉开始"):
                        name = '收粉开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "收粉结束清场"):
                        name = '收粉结束，按SOP清场（操作人）'
                        return operateflow(ID, name, PName)
                elif(PName == "醇沉"):
                    PName = "醇沉段"
                    if (PUName == "生产前的准备"):
                        name = '（醇沉段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "醇沉开始"):
                        name = '醇沉开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "醇沉结束清场"):
                        name = '醇沉结束，按SOP清场（操作人）'
                        return operateflow(ID, name, PName)
                elif(PName == "单效浓缩"):
                    PName = "单效浓缩段"
                    if (PUName == "生产前的准备"):
                        name = '（单效浓缩段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "单效浓缩开始"):
                        name = '单效浓缩开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "单效浓缩结束清场"):
                        name = '单效浓缩结束，按SOP清场（操作人）'
                        return operateflow(ID, name, PName)
                elif(PName == "收膏"):
                    PName = "收膏段"
                    if (PUName == "生产前的准备"):
                        name = '（收膏段）生产前准备（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "收膏开始"):
                        name = '收膏开始，操作按SOP执行（操作人）'
                        return operateflow(ID, name, PName)
                    elif (PUName == "收膏结束清场"):
                        name = '收膏结束，按SOP清场（操作人）'
                        return operateflow(ID, name, PName)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "操作人确认报错Error：" + str(e), current_user.Name)
def operateflow(ID, name, PName):
    flag = 'OK'
    try:
        BatchID = db_session.query(PlanManager.BatchID).filter(PlanManager.ID == ID).first()
        PUID = db_session.query(ProductUnitRoute.PUID).filter(ProductUnitRoute.PDUnitRouteName == PName).first()
        taskStatuss = db_session.query(ZYTask.TaskStatus).filter(ZYTask.PUID == PUID[0], ZYTask.BatchID == BatchID[0]).all()
        for status in taskStatuss:
            if(status[0] != "40"):
                return "请先进行任务确认，再进行操作！"
            else:
                pass
        node = db_session.query(Model.node.NodeCollection).filter(
            Model.node.NodeCollection.oddNum == ID,
            Model.node.NodeCollection.name == name).first()
        node.status = Model.node.NodeStatus.PASSED.value
        node.opertionTime = datetime.datetime.now()
        node.oddUser = current_user.Name
        db_session.commit()
        return flag
    except Exception as e:
        db_session.rollback()
        print(e)
        logger.error(e)
        insertSyslog("error", "复核报错Error：" + str(e), current_user.Name)
        return "复核报错Error：" + str(e), current_user.Name

# 复核人确认
@app.route('/ZYPlanGuid/checkedConfirm', methods=['POST', 'GET'])
def checkedConfirm():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data['ID']  # 计划ID
                PName = data['PName']  # 计划名称
                PUName = data['PUName']  # 计划明细名称
                planM = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                BrandName = planM.BrandName
                if (PName == "备料"):
                    if (PUName == "生产前的准备"):
                        statusName = '（备料段）生产前准备（操作人）'
                        name = '（备料段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "备料开始"):
                        statusName = '备料操作按SOP执行（操作人）'
                        name = '备料操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "备料结束清场"):
                        statusName = '（备料段）生产结束清场（操作人）'
                        name = '（备料段）生产结束清场（复核人）'
                        return checkflow(ID, statusName, name)
                elif (PName == "煎煮"):
                    if (PUName == "生产前的准备"):
                        statusName = '（煎煮段）生产前准备（操作人）'
                        name = '（煎煮段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "煎煮开始"):
                        statusName = '煎煮开始，操作按SOP执行（操作人）'
                        name = '煎煮开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "静置开始"):
                        statusName = '静置开始，操作按SOP执行（操作人）'
                        name = '静置开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "煎煮结束清场"):
                        statusName = '（煎煮段）生产结束清场（操作人）'
                        name = '（煎煮段）生产结束清场（复核人）'
                        return checkflow(ID, statusName, name)
                elif (PName == "浓缩"):
                    if (PUName == "生产前的准备"):
                        statusName = '（浓缩段）生产前准备（操作人）'
                        name = '（浓缩段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "浓缩开始"):
                        statusName = '浓缩开始，操作按SOP执行（操作人）'
                        name = '浓缩开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "浓缩结束清场"):
                        statusName = '浓缩结束清场（操作人）'
                        name = '浓缩结束清场（复核人）'
                        return checkflow(ID, statusName, name)
                elif (PName == "喷雾干燥"):
                    if (PUName == "生产前的准备"):
                        statusName = '（喷雾干燥段）生产前准备（操作人）'
                        name = '（喷雾干燥段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "喷雾干燥开始"):
                        statusName = '喷雾干燥开始，操作按SOP执行（操作人）'
                        name = '喷雾干燥开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "喷雾干燥结束清场"):
                        statusName = '喷雾干燥结束，按SOP清场（操作人）'
                        name = '喷雾干燥结束，按SOP清场（复核人）'
                        return checkflow(ID, statusName, name)
                elif (PName == "收粉"):
                    if (PUName == "生产前的准备"):
                        statusName = '（收粉段）生产前准备（操作人）'
                        name = '（收粉段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "收粉开始"):
                        statusName = '收粉开始，操作按SOP执行（操作人）'
                        name = '收粉开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "收粉结束清场"):
                        statusName = '收粉结束，按SOP清场（操作人）'
                        name = '收粉结束，按SOP清场（复核人）'
                        return checkflow(ID, statusName, name)
                elif (PName == "醇沉"):
                    if (PUName == "生产前的准备"):
                        statusName = '（醇沉段）生产前准备（操作人）'
                        name = '（醇沉段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "醇沉开始"):
                        statusName = '醇沉开始，操作按SOP执行（操作人）'
                        name = '醇沉开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "醇沉结束清场"):
                        statusName = '醇沉结束，按SOP清场（操作人）'
                        name = '醇沉结束，按SOP清场（复核人）'
                        return checkflow(ID, statusName, name)
                elif (PName == "单效浓缩"):
                    if (PUName == "生产前的准备"):
                        statusName = '（单效浓缩段）生产前准备（操作人）'
                        name = '（单效浓缩段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "单效浓缩开始"):
                        statusName = '单效浓缩开始，操作按SOP执行（操作人）'
                        name = '单效浓缩开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "单效浓缩结束清场"):
                        statusName = '单效浓缩结束，按SOP清场（操作人）'
                        name = '单效浓缩结束，按SOP清场（复核人）'
                        return checkflow(ID, statusName, name)
                elif (PName == "收膏"):
                    if (PUName == "生产前的准备"):
                        statusName = '（收膏段）生产前准备（操作人）'
                        name = '（收膏段）生产前准备（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "收膏开始"):
                        statusName = '收膏开始，操作按SOP执行（操作人）'
                        name = '收膏开始，操作按SOP执行（复核人）'
                        return checkflow(ID, statusName, name)
                    elif (PUName == "收膏结束清场"):
                        statusName = '收膏结束，按SOP清场（操作人）'
                        name = '收膏结束，按SOP清场（复核人）'
                        return checkflow(ID,statusName,name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "复核报错Error：" + str(e), current_user.Name)
def checkflow(ID,statusName,name):
    flag = 'OK'
    try:
        status = db_session.query(Model.node.NodeCollection.status).filter(
            Model.node.NodeCollection.oddNum == ID,
            Model.node.NodeCollection.name == statusName).first()
        if (status[0] != 10):
            return "请先操作人进行确认后再进行复核！"
        node = db_session.query(Model.node.NodeCollection).filter(
            Model.node.NodeCollection.oddNum == ID,
            Model.node.NodeCollection.name == name).first()
        node.status = Model.node.NodeStatus.PASSED.value
        node.opertionTime = datetime.datetime.now()
        node.oddUser = current_user.Name
        db_session.commit()
        return flag
    except Exception as e:
        db_session.rollback()
        print(e)
        logger.error(e)
        insertSyslog("error", "复核报错Error：" + str(e), current_user.Name)
        return "复核报错Error：" + str(e), current_user.Name

# QA签名
@app.route('/ZYPlanGuid/QAautograph', methods=['POST', 'GET'])
def QAautograph():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = data['ID']  # 计划ID
                PName = data['PName']  # 计划名称
                PUName = data['PUName']  # 计划明细名称
                planM = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                BrandName = planM.BrandName
                if (PName == "备料"):
                    if (PUName == "生产前的准备"):
                        statusName = '（备料段）生产前准备（复核人）'
                        name = '（备料段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "备料开始"):
                        statusName = '备料操作按SOP执行（复核人）'
                        name = '备料操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "备料结束清场"):
                        statusName = '（备料段）生产结束清场（复核人）'
                        name = '（备料段）生产结束清场（QA签名）'
                        return QAflow(ID, statusName, name)
                elif (PName == "煎煮"):
                    if (PUName == "生产前的准备"):
                        statusName = '（煎煮段）生产前准备（复核人）'
                        name = '（煎煮段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "煎煮开始"):
                        statusName = '煎煮开始，操作按SOP执行（复核人）'
                        name = '煎煮开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "静置开始"):
                        statusName = '静置开始，操作按SOP执行（复核人）'
                        name = '静置开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "煎煮结束清场"):
                        statusName = '（煎煮段）生产结束清场（复核人）'
                        name = '（煎煮段）生产结束清场（QA签名）'
                        return QAflow(ID, statusName, name)
                elif (PName == "浓缩"):
                    if (PUName == "生产前的准备"):
                        statusName = '（浓缩段）生产前准备（复核人）'
                        name = '（浓缩段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "浓缩开始"):
                        statusName = '浓缩开始，操作按SOP执行（复核人）'
                        name = '浓缩开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "浓缩结束清场"):
                        statusName = '浓缩结束清场（复核人）'
                        name = '浓缩结束清场（QA签名）'
                        return QAflow(ID, statusName, name)
                elif (PName == "喷雾干燥"):
                    if (PUName == "生产前的准备"):
                        statusName = '（喷雾干燥段）生产前准备（复核人）'
                        name = '（喷雾干燥段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "喷雾干燥开始"):
                        statusName = '喷雾干燥开始，操作按SOP执行（复核人）'
                        name = '喷雾干燥开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "喷雾干燥结束清场"):
                        statusName = '喷雾干燥结束，按SOP清场（复核人）'
                        name = '喷雾干燥结束，按SOP清场（QA签名）'
                        return QAflow(ID, statusName, name)
                elif (PName == "收粉"):
                    if (PUName == "生产前的准备"):
                        statusName = '（收粉段）生产前准备（复核人）'
                        name = '（收粉段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "收粉开始"):
                        statusName = '收粉开始，操作按SOP执行（复核人）'
                        name = '收粉开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "收粉结束清场"):
                        statusName = '收粉结束，按SOP清场（复核人）'
                        name = '收粉结束，按SOP清场（QA签名）'
                        return QAflow(ID, statusName, name)
                elif (PName == "醇沉"):
                    if (PUName == "生产前的准备"):
                        statusName = '（醇沉段）生产前准备（复核人）'
                        name = '（醇沉段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "醇沉开始"):
                        statusName = '醇沉开始，操作按SOP执行（复核人）'
                        name = '醇沉开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "醇沉结束清场"):
                        statusName = '醇沉结束，按SOP清场（复核人）'
                        name = '醇沉结束，按SOP清场（QA签名）'
                        return QAflow(ID, statusName, name)
                elif (PName == "单效浓缩"):
                    if (PUName == "生产前的准备"):
                        statusName = '（单效浓缩段）生产前准备（复核人）'
                        name = '（单效浓缩段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "单效浓缩开始"):
                        statusName = '单效浓缩开始，操作按SOP执行（复核人）'
                        name = '单效浓缩开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "单效浓缩结束清场"):
                        statusName = '单效浓缩结束，按SOP清场（复核人）'
                        name = '单效浓缩结束，按SOP清场（QA签名）'
                        return QAflow(ID, statusName, name)
                elif (PName == "收膏"):
                    if (PUName == "生产前的准备"):
                        statusName = '（收膏段）生产前准备（复核人）'
                        name = '（收膏段）生产前准备（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "收膏开始"):
                        statusName = '收膏开始，操作按SOP执行（复核人）'
                        name = '收膏开始，操作按SOP执行（QA签名）'
                        return QAflow(ID, statusName, name)
                    elif (PUName == "收膏结束清场"):
                        statusName = '收膏结束，按SOP清场（复核人）'
                        name = '收膏结束，按SOP清场（QA签名）'
                        return QAflow(ID, statusName, name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "复核报错Error：" + str(e), current_user.Name)

def QAflow(ID, statusName, name):
    flag = 'OK'
    try:
        status = db_session.query(Model.node.NodeCollection.status).filter(
            Model.node.NodeCollection.oddNum == ID,
            Model.node.NodeCollection.name == statusName).first()
        if (status[0] != 10):
            return "请先复核人进行复核后再进行QA签名！"
        node = db_session.query(Model.node.NodeCollection).filter(
            Model.node.NodeCollection.oddNum == ID,
            Model.node.NodeCollection.name == name).first()
        node.status = Model.node.NodeStatus.PASSED.value
        node.opertionTime = datetime.datetime.now()
        node.oddUser = current_user.Name
        db_session.commit()
        PStatuss = db_session.query(Model.node.NodeCollection.status).filter(Model.node.NodeCollection.oddNum == ID, Model.node.NodeCollection.name != 'QA放行').all()
        fl = "TRUE"
        for pst in PStatuss:
            if(pst[0] != 10):
                fl = "FALSE"
        if(fl == "TRUE"):
            planaMStatus = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
            planaMStatus.PlanStatus = Model.Global.PlanStatus.FINISH.value
            db_session.commit()
        return flag
    except Exception as e:
        db_session.rollback()
        print(e)
        logger.error(e)
        insertSyslog("error", "QA签名报错Error：" + str(e), current_user.Name)
        return "QA签名报错Error：" + str(e), current_user.Name

# QA放行查询
@app.route('/ZYPlanGuid/QAPassSearch', methods=['POST', 'GET'])
def QAPassSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                ABatchID = data['BatchID']  # 批次号
                if (ABatchID == None or ABatchID == ""):
                    total = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus.in_((60, 70))).count()
                    PlanManagers = db_session.query(PlanManager).filter(PlanManager.PlanStatus.in_((60, 70))).order_by(
                        desc("PlanBeginTime")).all()[inipage:endpage]
                else:
                    total = db_session.query(PlanManager.ID).filter(PlanManager.BatchID == ABatchID,
                                                               PlanManager.PlanStatus.in_((60, 70))).count()
                    PlanManagers = db_session.query(PlanManager).filter(ZYPlan.BatchID == ABatchID,
                                                              PlanManager.PlanStatus.in_((60, 70))).order_by(
                        desc("PlanBeginTime")).all()[inipage:endpage]
                PlanManagers = json.dumps(PlanManagers, cls=AlchemyEncoder, ensure_ascii=False)
                jsonPlanManagers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + PlanManagers + "}"
                return jsonPlanManagers
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "QA放行查询报错Error：" + str(e), current_user.Name)

# QA放行
@app.route('/ZYPlanGuid/QAPass', methods=['POST', 'GET'])
def QAPass():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        nodec = db_session.query(Model.node.NodeCollection).filter(Model.node.NodeCollection.oddNum == id, Model.node.NodeCollection.name == 'QA放行').first()
                        nodec.status = Model.node.NodeStatus.PASSED.value
                        oclass = db_session.query(PlanManager).filter(PlanManager.ID == id).first()
                        oclass.PlanStatus = Model.Global.PlanStatus.QApass.value
                        db_session.commit()
                        return 'OK'
                    except Exception as e:
                        db_session.rollback()
                        print(e)
                        logger.error(e)
                        insertSyslog("error", "QA放行报错Error：" + str(e), current_user.Name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "QA放行报错Error：" + str(e), current_user.Name)

# 计划执行进度
@app.route('/PlanExecutionProgress')
def PlanExecutionProgress():
    return render_template('PlanExecutionProgress.html')

# 计划执行进度查询计划明细
@app.route('/PlanExecutionProgress/zyPlanProgressSearch', methods=['POST', 'GET'])
def zyPlanProgressSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                BatchID = data['BatchID']  # 批次号
                BrandID = data['BrandID']  # 品名ID
                total = db_session.query(ZYPlan.ID).filter(ZYPlan.BatchID == BatchID, ZYPlan.BrandID == BrandID).count()
                zyplans = db_session.query(ZYPlan.ID).filter(ZYPlan.BatchID == BatchID, ZYPlan.BrandID == BrandID).order_by(desc("EnterTime")).all()[inipage:endpage]
                jsonzyplans = json.dumps(zyplans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzyplans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonzyplans + "}"
                return jsonzyplans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划执行进度查询计划明细Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 计划执行进度查询流程图
@app.route('/PlanExecutionProgress/planmanagerProgressTuSearch', methods=['POST', 'GET'])
def planmanagerProgressTuSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                ID = int(data['ID'])
                dic = {}
                planM = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                BrandName = planM.BrandName
                if(BrandName == "健胃消食片浸膏粉"):
                    aa = '（备料段）任务确认'
                    dic['aa'] = queryFlow(ID, aa)
                    a1 = '（备料段）生产前准备（QA签名）'
                    dic['a1'] = queryFlow(ID, a1)
                    a2 = '备料操作按SOP执行（QA签名）'
                    dic['a2'] = queryFlow(ID, a2)
                    a3 = '（备料段）生产结束清场（QA签名）'
                    dic['a3'] = queryFlow(ID, a3)
                    bb = '（煎煮段）任务确认'
                    dic['bb'] = queryFlow(ID, bb)
                    b1 = '（煎煮段）生产前准备（QA签名）'
                    dic['b1'] = queryFlow(ID, b1)
                    b2 = '煎煮开始，操作按SOP执行（QA签名）'
                    dic['b2'] = queryFlow(ID, b2)
                    b3 = '静置开始，操作按SOP执行（QA签名）'
                    dic['b3'] = queryFlow(ID, b3)
                    b4 = '（煎煮段）生产结束清场（QA签名）'
                    dic['b4'] = queryFlow(ID, b4)
                    cc = '（浓缩段）任务确认'
                    dic['cc'] = queryFlow(ID, cc)
                    c1 = '（浓缩段）生产前准备（QA签名）'
                    dic['c1'] = queryFlow(ID, c1)
                    c2 = '浓缩开始，操作按SOP执行（QA签名）'
                    dic['c2'] = queryFlow(ID, c2)
                    c3 = '浓缩结束清场（QA签名）'
                    dic['c3'] = queryFlow(ID, c3)
                    dd = '（喷雾干燥段）任务确认'
                    dic['dd'] = queryFlow(ID, dd)
                    d1 = '（喷雾干燥段）生产前准备（QA签名）'
                    dic['d1'] = queryFlow(ID, d1)
                    d2 = '喷雾干燥开始，操作按SOP执行（QA签名）'
                    dic['d2'] = queryFlow(ID, d2)
                    d3 = '喷雾干燥结束，按SOP清场（QA签名）'
                    dic['d3'] = queryFlow(ID, d3)
                    ee = '（收粉段）任务确认'
                    dic['ee'] = queryFlow(ID, ee)
                    e1 = '（收粉段）生产前准备（QA签名）'
                    dic['e1'] = queryFlow(ID, e1)
                    e2 = '收粉开始，操作按SOP执行（QA签名）'
                    dic['e2'] = queryFlow(ID, e2)
                    e3 = '收粉结束，按SOP清场（QA签名）'
                    dic['e3'] = queryFlow(ID, e3)
                elif(BrandName == "肿节风浸膏"):
                    aa = '（备料段）任务确认'
                    dic['aa'] = queryFlow(ID, aa)
                    a1 = '（备料段）生产前准备（QA签名）'
                    dic['a1'] = queryFlow(ID, a1)
                    a2 = '备料操作按SOP执行（QA签名）'
                    dic['a2'] = queryFlow(ID, a2)
                    a3 = '（备料段）生产结束清场（QA签名）'
                    dic['a3'] = queryFlow(ID, a3)
                    bb = '（煎煮段）任务确认'
                    dic['bb'] = queryFlow(ID, bb)
                    b1 = '（煎煮段）生产前准备（QA签名）'
                    dic['b1'] = queryFlow(ID, b1)
                    b2 = '煎煮开始，操作按SOP执行（QA签名）'
                    dic['b2'] = queryFlow(ID, b2)
                    b3 = '静置开始，操作按SOP执行（QA签名）'
                    dic['b3'] = queryFlow(ID, b3)
                    b4 = '（煎煮段）生产结束清场（QA签名）'
                    dic['b4'] = queryFlow(ID, b4)
                    cc = '（浓缩段）任务确认'
                    dic['cc'] = queryFlow(ID, cc)
                    c1 = '（浓缩段）生产前准备（QA签名）'
                    dic['c1'] = queryFlow(ID, c1)
                    c2 = '浓缩开始，操作按SOP执行（QA签名）'
                    dic['c2'] = queryFlow(ID, c2)
                    c3 = '浓缩结束清场（QA签名）'
                    dic['c3'] = queryFlow(ID, c3)
                    ff = '（醇沉段）任务确认'
                    dic['ff'] = queryFlow(ID, ff)
                    f1 = '（醇沉段）生产前准备（QA签名）'
                    dic['f1'] = queryFlow(ID, f1)
                    f2 = '醇沉开始，操作按SOP执行（QA签名）'
                    dic['f2'] = queryFlow(ID, f2)
                    f3 = '醇沉结束，按SOP清场（QA签名）'
                    dic['f3'] = queryFlow(ID, f3)
                    gg = '（单效浓缩段）任务确认'
                    dic['gg'] = queryFlow(ID, gg)
                    g1 = '（单效浓缩段）生产前准备（QA签名）'
                    dic['g1'] = queryFlow(ID, g1)
                    g2 = '单效浓缩开始，操作按SOP执行（QA签名）'
                    dic['g2'] = queryFlow(ID, g2)
                    g3 = '单效浓缩结束，按SOP清场（QA签名）'
                    dic['g3'] = queryFlow(ID, g3)
                    hh = '（收膏段）任务确认'
                    dic['hh'] = queryFlow(ID, hh)
                    h1 = '（收膏段）生产前准备（QA签名）'
                    dic['h1'] = queryFlow(ID, h1)
                    h2 = '收膏开始，操作按SOP执行（QA签名）'
                    dic['h2'] = queryFlow(ID,h2)
                    h3 = '收膏结束，按SOP清场（QA签名）'
                    dic['h3'] = queryFlow(ID, h3)
                return json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划执行进度查询流程图查询报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
def queryFlow(ID, name):
    status = db_session.query(Model.node.NodeCollection.status).filter(Model.node.NodeCollection.oddNum == ID,
                                                                       Model.node.NodeCollection.name == name).first()
    if(status[0] == 10):
        return 'OK'
    else:
        return 'NO'

# 计划管理
@app.route('/ZYPlanManage')
def zYPlanManage():
    return render_template('ZYPlanManage.html')

# 电子批记录跳转
@app.route('/electronicBatchRecord')
def electronicBatchRecord():
    if request.method == "GET":
        data = request.values
        title = data["title"]
        session['title'] = title
        ID = data["ID"]
        oclass = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
        OperationPeople_a1 = ""
        CheckedPeople_a1 = ""
        QAConfirmPeople_a1 = ""
        OperationPeople_a2 = ""
        CheckedPeople_a2 = ""
        OperationPeople_a3 = ""
        CheckedPeople_a3 = ""
        QAConfirmPeople_a3 = ""
        OperationPeople_a4 = ""
        CheckedPeople_a4 = ""
        QAConfirmPeople_a4 = ""
        OperationPeople_a5 = ""
        CheckedPeople_a5 = ""

        OperationPeople_b1 = ""
        CheckedPeople_b1 = ""
        QAConfirmPeople_b1 = ""
        OperationPeople_b2 = ""
        CheckedPeople_b2 = ""
        QAConfirmPeople_b2 = ""
        OperationPeople_b3 = ""
        CheckedPeople_b3 = ""
        QAConfirmPeople_b3 = ""
        OperationPeople_b4 = ""
        CheckedPeople_b4 = ""
        QAConfirmPeople_b4 = ""
        OperationPeople_b5 = ""
        CheckedPeople_b5 = ""
        QAConfirmPeople_b5 = ""
        OperationPeople_b6 = ""
        CheckedPeople_b6 = ""

        OperationPeople_c1 = ""
        CheckedPeople_c1 = ""
        QAConfirmPeople_c1 = ""
        OperationPeople_c2 = ""
        CheckedPeople_c2 = ""
        QAConfirmPeople_c2 = ""
        OperationPeople_c3 = ""
        CheckedPeople_c3 = ""
        QAConfirmPeople_c3 = ""
        OperationPeople_c4 = ""
        CheckedPeople_c4 = ""
        QAConfirmPeople_c4 = ""
        OperationPeople_c5 = ""
        CheckedPeople_c5 = ""
        QAConfirmPeople_c5 = ""
        OperationPeople_c6 = ""
        CheckedPeople_c6 = ""
        QAConfirmPeople_c6 = ""
        OperationPeople_c7 = ""
        CheckedPeople_c7 = ""

        OperationPeople_d1 = ""
        CheckedPeople_d1 = ""
        QAConfirmPeople_d1 = ""
        OperationPeople_d2 = ""
        CheckedPeople_d2 = ""
        OperationPeople_d3 = ""
        CheckedPeople_d3 = ""
        QAConfirmPeople_d3 = ""
        OperationPeople_d4 = ""
        CheckedPeople_d4 = ""

        OperationPeople_e1 = ""
        CheckedPeople_e1 = ""
        QAConfirmPeople_e1 = ""
        OperationPeople_e2 = ""
        CheckedPeople_e2 = ""
        QAConfirmPeople_e2 = ""
        OperationPeople_e3 = ""
        CheckedPeople_e3 = ""
        QAConfirmPeople_e3 = ""
        QAConfirmPeople_e4 = ""
        OperationPeople_e5 = ""
        CheckedPeople_e5 = ""
        OperationPeople_e6 = ""
        CheckedPeople_e6 = ""
        QAConfirmPeople_e6 = ""
        OperationPeople_e7 = ""
        CheckedPeople_e7 = ""
        OperationPeople_e8 = ""
        CheckedPeople_e8 = ""
        if(title == "备料"):
            re = electronicBatchRecords("备料段", oclass.BrandID, oclass.BatchID, ID)
            Pclass = re[0]
            Zclass = re[1]
            Noclas = re[3]
            for no in Noclas:
                if(no.name == "（备料段）生产前准备（操作人）"):
                    OperationPeople_a1 = no.oddUser
                elif(no.name == "（备料段）生产前准备（复核人）"):
                    CheckedPeople_a1 = no.oddUser
                elif (no.name == "（备料段）生产前准备（QA签名）"):
                    QAConfirmPeople_a1 = no.oddUser
                elif (no.name == "备料操作按SOP执行（操作人）"):
                    OperationPeople_a3 = no.oddUser
                elif (no.name == "备料操作按SOP执行（复核人）"):
                    CheckedPeople_a3 = no.oddUser
                elif (no.name == "备料操作按SOP执行（QA签名）"):
                    QAConfirmPeople_a3 = no.oddUser
                elif (no.name == "（备料段）生产结束清场（操作人）"):
                    OperationPeople_a4 = no.oddUser
                elif (no.name == "（备料段）生产结束清场（复核人）"):
                    CheckedPeople_a4 = no.oddUser
                elif (no.name == "（备料段）生产结束清场（QA签名）"):
                    QAConfirmPeople_a4 = no.oddUser
            Newoclass = db_session.query(NewReadyWork).filter(NewReadyWork.PUID == Pclass.PUID,NewReadyWork.BatchID ==
                                                            oclass.BatchID,NewReadyWork.Type == "32").first()
            if(Newoclass != None):
                OperationPeople_a2 = Newoclass.OperationPeople
                CheckedPeople_a2 = Newoclass.CheckedPeople
            if(re[2] != None):
                OperationPeople_a5 = re[2].OperationPeople
                CheckedPeople_a5 = re[2].CheckedPeople
        elif(title == "煎煮"):
            re = electronicBatchRecords("煎煮段", oclass.BrandID, oclass.BatchID, ID)
            Pclass = re[0]
            Zclass = re[1]
            Noclas = re[3]
            for no in Noclas:
                if(no.name == "（煎煮段）生产前准备（操作人）"):
                    OperationPeople_b1 = no.oddUser
                elif(no.name == "（煎煮段）生产前准备（复核人）"):
                    CheckedPeople_b1 = no.oddUser
                elif (no.name == "（煎煮段）生产前准备（QA签名）"):
                    QAConfirmPeople_b1 = no.oddUser
                elif (no.name == "煎煮开始，操作按SOP执行（操作人）"):
                    OperationPeople_b2 = no.oddUser
                elif (no.name == "煎煮开始，操作按SOP执行（复核人）"):
                    CheckedPeople_b2 = no.oddUser
                elif (no.name == "煎煮开始，操作按SOP执行（QA签名）"):
                    QAConfirmPeople_b2 = no.oddUser
                elif (no.name == "静置开始，操作按SOP执行（操作人）"):
                    OperationPeople_b3 = no.oddUser
                elif (no.name == "静置开始，操作按SOP执行（复核人）"):
                    CheckedPeople_b3 = no.oddUser
                elif (no.name == "静置开始，操作按SOP执行（QA签名）"):
                    QAConfirmPeople_b3 = no.oddUser
                elif (no.name == "（煎煮段）生产结束清场（操作人）"):
                    OperationPeople_b4 = no.oddUser
                elif (no.name == "（煎煮段）生产结束清场（复核人）"):
                    CheckedPeople_b4 = no.oddUser
                elif (no.name == "（煎煮段）生产结束清场（QA签名）"):
                    QAConfirmPeople_b4 = no.oddUser
            Newoclass = db_session.query(NewReadyWork).filter(NewReadyWork.PUID == Pclass.PUID, NewReadyWork.BatchID ==
                                                            oclass.BatchID,NewReadyWork.Type == "42").first()
            if(Newoclass != None):
                OperationPeople_b5 = Newoclass.OperationPeople
                CheckedPeople_b5 = Newoclass.CheckedPeople
                QAConfirmPeople_b5 = Newoclass.QAConfirmPeople
            if (re[2] != None):
                OperationPeople_b6 = re[2].OperationPeople
                CheckedPeople_b6 = re[2].CheckedPeople
        elif (title == "浓缩"):
            re = electronicBatchRecords("浓缩段", oclass.BrandID, oclass.BatchID, ID)
            Pclass = re[0]
            Zclass = re[1]
            Noclas = re[3]
            for no in Noclas:
                if (no.name == "（浓缩段）生产前准备（操作人）"):
                    OperationPeople_c1 = no.oddUser
                elif (no.name == "（浓缩段）生产前准备（复核人）"):
                    CheckedPeople_c1 = no.oddUser
                elif (no.name == "（浓缩段）生产前准备（QA签名）"):
                    QAConfirmPeople_c1 = no.oddUser
                elif (no.name == "浓缩开始，操作按SOP执行（操作人）"):
                    OperationPeople_c2 = no.oddUser
                elif (no.name == "浓缩开始，操作按SOP执行（复核人）"):
                    CheckedPeople_c2 = no.oddUser
                elif (no.name == "浓缩开始，操作按SOP执行（QA签名）"):
                    QAConfirmPeople_c2 = no.oddUser
                elif (no.name == "浓缩结束清场（操作人）"):
                    OperationPeople_c6 = no.oddUser
                elif (no.name == "浓缩结束清场（复核人）"):
                    CheckedPeople_c6 = no.oddUser
                elif (no.name == "浓缩结束清场（QA签名）"):
                    QAConfirmPeople_c6 = no.oddUser
            Newoclass1 = db_session.query(NewReadyWork).filter(NewReadyWork.PUID == Pclass.PUID, NewReadyWork.BatchID ==
                                                              oclass.BatchID, NewReadyWork.Type == "45").first()
            if(Newoclass1 != None):
                OperationPeople_c3 = Newoclass1.OperationPeople
                CheckedPeople_c3 = Newoclass1.CheckedPeople
                QAConfirmPeople_c3 = Newoclass1.QAConfirmPeople
            Newoclass2 = db_session.query(NewReadyWork).filter(NewReadyWork.PUID == Pclass.PUID, NewReadyWork.BatchID ==
                                                               oclass.BatchID, NewReadyWork.Type == "46").first()
            if (Newoclass2 != None):
                OperationPeople_c4 = Newoclass2.OperationPeople
                CheckedPeople_c4 = Newoclass2.CheckedPeople
                QAConfirmPeople_c4 = Newoclass2.QAConfirmPeople
            if (re[2] != None):
                OperationPeople_c7 = re[2].OperationPeople
                CheckedPeople_c7 = re[2].CheckedPeople
        elif (title == "喷雾干燥"):
            re = electronicBatchRecords("喷雾干燥段", oclass.BrandID, oclass.BatchID, ID)
            Pclass = re[0]
            Zclass = re[1]
            if (re[2] != None):
                OperationPeople_d4 = re[2].OperationPeople
                CheckedPeople_d4 = re[2].CheckedPeople
            Noclas = re[3]
            for no in Noclas:
                if (no.name == "（喷雾干燥段）生产前准备（操作人）"):
                    OperationPeople_d1 = no.oddUser
                elif (no.name == "（喷雾干燥段）生产前准备（复核人）"):
                    CheckedPeople_d1 = no.oddUser
                elif (no.name == "（喷雾干燥段）生产前准备（QA签名）"):
                    QAConfirmPeople_d1 = no.oddUser
                elif (no.name == "喷雾干燥开始，操作按SOP执行（操作人）"):
                    OperationPeople_d2 = no.oddUser
                elif (no.name == "喷雾干燥开始，操作按SOP执行（复核人）"):
                    CheckedPeople_d2 = no.oddUser
                elif (no.name == "喷雾干燥开始，操作按SOP执行（QA签名）"):
                    QAConfirmPeople_d2 = no.oddUser
                elif (no.name == "喷雾干燥结束，按SOP清场（操作人）"):
                    OperationPeople_d3 = no.oddUser
                elif (no.name == "喷雾干燥结束，按SOP清场（复核人）"):
                    CheckedPeople_d3 = no.oddUser
                elif (no.name == "喷雾干燥结束，按SOP清场（QA签名）"):
                    QAConfirmPeople_d3 = no.oddUser
        elif (title == "收粉"):
            re = electronicBatchRecords("收粉段", oclass.BrandID, oclass.BatchID, ID)
            Pclass = re[0]
            Zclass = re[1]
            if (re[2] != None):
                OperationPeople_e7 = re[2].OperationPeople
                CheckedPeople_e7 = re[2].CheckedPeople
            Noclas = re[3]
            for no in Noclas:
                if (no.name == "（收粉段）生产前准备（操作人）"):
                    OperationPeople_e1 = no.oddUser
                elif (no.name == "（收粉段）生产前准备（复核人）"):
                    CheckedPeople_e1 = no.oddUser
                elif (no.name == "（收粉段）生产前准备（QA签名）"):
                    QAConfirmPeople_e1 = no.oddUser
                elif (no.name == "收粉开始，操作按SOP执行（操作人）"):
                    OperationPeople_e3 = no.oddUser
                elif (no.name == "收粉开始，操作按SOP执行（复核人）"):
                    CheckedPeople_e3 = no.oddUser
                elif (no.name == "收粉开始，操作按SOP执行（QA签名）"):
                    QAConfirmPeople_e3 = no.oddUser
                elif (no.name == "收粉结束，按SOP清场（操作人）"):
                    OperationPeople_e6 = no.oddUser
                elif (no.name == "收粉结束，按SOP清场（复核人）"):
                    CheckedPeople_e6 = no.oddUser
                elif (no.name == "收粉结束，按SOP清场（QA签名）"):
                    QAConfirmPeople_e6 = no.oddUser
            Newoclasss = db_session.query(NewReadyWork).filter(NewReadyWork.PUID == Pclass.PUID, NewReadyWork.BatchID ==
                                                               oclass.BatchID, NewReadyWork.Type.in_(("48", "50", "51", "52"))).all()
            if(len(Newoclasss) > 0):
                for nc in Newoclasss:
                    if(nc.Type == "48"):
                        OperationPeople_e2 = nc.OperationPeople
                        CheckedPeople_e2 = nc.CheckedPeople
                        QAConfirmPeople_e2 = nc.QAConfirmPeople
                    elif(nc.Type == "50"):
                        OperationPeople_e5 = nc.OperationPeople
                        CheckedPeople_e5 = nc.CheckedPeople
                    elif (nc.Type == "51"):
                        OperationPeople_e8 = nc.OperationPeople
                        CheckedPeople_e8 = nc.CheckedPeople
                    elif (nc.Type == "52"):
                        QAConfirmPeople_e4 = nc.QAConfirmPeople
        elif (title == "醇沉"):
            re = electronicBatchRecords("醇沉段", oclass.BrandID, oclass.BatchID,ID)
            Pclass = re[0]
            Zclass = re[1]
        elif (title == "单效浓缩"):
            re = electronicBatchRecords("单效浓缩段", oclass.BrandID, oclass.BatchID,ID)
            Pclass = re[0]
            Zclass = re[1]
        elif (title == "收膏"):
            re = electronicBatchRecords("收膏段", oclass.BrandID, oclass.BatchID,ID)
            Pclass = re[0]
            Zclass = re[1]
        RoleNames = db_session.query(User.RoleName).filter(User.Name == current_user.Name).all()
        flag = ""
        for rN in RoleNames:
            roleID = db_session.query(Role.ID).filter(Role.RoleName == rN[0]).first()
            menus = db_session.query(Menu.ModuleName).join(Role_Menu, isouter=True).filter_by(Role_ID=roleID).all()
            for menu in menus:
                if (menu[0] == "操作人确认"):
                    flag = "82"
                elif(menu[0] == "复核人确认"):
                    flag = "83"
                elif(menu[0] == "QA确认"):
                    flag = "84"
    return render_template('electronicBatchRecord.html',
                           PName=Pclass.PDUnitRouteName,PUID=Pclass.PUID,BatchID=oclass.BatchID,PlanQuantity=oclass.PlanQuantity,
                           ActBeginTime=Zclass.ActBeginTime,flag=flag,OperationPeople_a1=OperationPeople_a1,CheckedPeople_a1=CheckedPeople_a1,QAConfirmPeople_a1=QAConfirmPeople_a1,
                           OperationPeople_a2=OperationPeople_a2,CheckedPeople_a2=CheckedPeople_a2,OperationPeople_a3=OperationPeople_a3,CheckedPeople_a3=CheckedPeople_a3,
                           QAConfirmPeople_a3=QAConfirmPeople_a3,OperationPeople_a4=OperationPeople_a4,CheckedPeople_a4=CheckedPeople_a4,QAConfirmPeople_a4=QAConfirmPeople_a4,
                           OperationPeople_a5=OperationPeople_a5,CheckedPeople_a5=CheckedPeople_a5,OperationPeople_b1 = OperationPeople_b1,CheckedPeople_b1 = CheckedPeople_b1,
                           QAConfirmPeople_b1 = QAConfirmPeople_b1,OperationPeople_b2 = OperationPeople_b2,CheckedPeople_b2 = CheckedPeople_b2,QAConfirmPeople_b2 = QAConfirmPeople_b2,
                           OperationPeople_b3 = OperationPeople_b3,CheckedPeople_b3 = CheckedPeople_b3,QAConfirmPeople_b3 = QAConfirmPeople_b3,OperationPeople_b4 = OperationPeople_b4,
                           CheckedPeople_b4 = CheckedPeople_b4,QAConfirmPeople_b4 = QAConfirmPeople_b4,OperationPeople_b5 = OperationPeople_b5,CheckedPeople_b5 = CheckedPeople_b5,
                           QAConfirmPeople_b5 = QAConfirmPeople_b5,OperationPeople_b6 = OperationPeople_b6,CheckedPeople_b6 = CheckedPeople_b6,
                           OperationPeople_c1=OperationPeople_c1,CheckedPeople_c1 = CheckedPeople_c1,QAConfirmPeople_c1 = QAConfirmPeople_c1,OperationPeople_c2 = OperationPeople_c2,
                           CheckedPeople_c2 = CheckedPeople_c2,QAConfirmPeople_c2 = QAConfirmPeople_c2,OperationPeople_c3 = OperationPeople_c3,CheckedPeople_c3 = CheckedPeople_c3,
                           QAConfirmPeople_c3 = QAConfirmPeople_c3,OperationPeople_c4 = OperationPeople_c4,CheckedPeople_c4 = CheckedPeople_c4,QAConfirmPeople_c4 = QAConfirmPeople_c4,
                           OperationPeople_c5 = OperationPeople_c5,CheckedPeople_c5 = CheckedPeople_c5,QAConfirmPeople_c5 = QAConfirmPeople_c5,OperationPeople_c6 = OperationPeople_c6,
                           CheckedPeople_c6 = CheckedPeople_c6,QAConfirmPeople_c6 = QAConfirmPeople_c6,OperationPeople_c7 = OperationPeople_c7,CheckedPeople_c7 = CheckedPeople_c7,
                           OperationPeople_d1=OperationPeople_d1,CheckedPeople_d1 = CheckedPeople_d1,QAConfirmPeople_d1 = QAConfirmPeople_d1,OperationPeople_d2 = OperationPeople_d2,
                           CheckedPeople_d2 = CheckedPeople_d2,OperationPeople_d3 = OperationPeople_d3,CheckedPeople_d3 = CheckedPeople_d3,QAConfirmPeople_d3 = QAConfirmPeople_d3,
                           OperationPeople_d4 = OperationPeople_d4,CheckedPeople_d4 = CheckedPeople_d4,
                           OperationPeople_e1 = OperationPeople_e1,CheckedPeople_e1 = CheckedPeople_e1,QAConfirmPeople_e1 = QAConfirmPeople_e1,OperationPeople_e2 = OperationPeople_e2,
                           CheckedPeople_e2 = CheckedPeople_e2,QAConfirmPeople_e2 = QAConfirmPeople_e2,OperationPeople_e3 = OperationPeople_e3,CheckedPeople_e3 = CheckedPeople_e3,
                           QAConfirmPeople_e3 = QAConfirmPeople_e3,QAConfirmPeople_e4 = QAConfirmPeople_e4,OperationPeople_e5 = OperationPeople_e5,CheckedPeople_e5 = CheckedPeople_e5,
                           OperationPeople_e6 = OperationPeople_e6,CheckedPeople_e6 = CheckedPeople_e6,QAConfirmPeople_e6 = QAConfirmPeople_e6,OperationPeople_e7 = OperationPeople_e7,
                           CheckedPeople_e7 = CheckedPeople_e7,OperationPeople_e8 = OperationPeople_e8,CheckedPeople_e8 = CheckedPeople_e8)
def electronicBatchRecords(name,BrandID,BatchID,ID):
    Pclass = db_session.query(ProductUnitRoute).filter(ProductUnitRoute.PDUnitRouteName == name,
                                                       ProductUnitRoute.ProductRuleID == BrandID).first()
    Zclass = db_session.query(ZYPlan).filter(ZYPlan.BatchID == BatchID,ZYPlan.PUID == Pclass.PUID).first()
    Eoclas = db_session.query(EquipmentWork).filter(EquipmentWork.PUID == Pclass.PUID, EquipmentWork.BatchID == BatchID).first()
    Noclas = db_session.query(Model.node.NodeCollection).filter(Model.node.NodeCollection.oddNum == ID,Model.node.NodeCollection.status == "10").all()
    return Pclass,Zclass,Eoclas,Noclas

#设备工作情况确认
@app.route('/addEquipmentWork', methods=['POST', 'GET'])
def addEquipmentWork():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                PUID = data['PUID']
                BatchID = data['BatchID']
                # EQPName = data['EQPName']# 设备名称
                # EQPCode = data['EQPCode']# 设备编码
                # ISNormal = data['ISNormal']# 设备运转情况
                # IsStandard = data['IsStandard']# 生产过程是否符合安全管理规定
                confirm = data['confirm']
                if(confirm == "操作人"):
                    db_session.add(
                        EquipmentWork(
                            BatchID=BatchID,
                            PUID=int(PUID),
                            # EQPName=EQPName,
                            # EQPCode=EQPCode,
                            # ISNormal=ISNormal,
                            OperationPeople=current_user.Name,
                            # CheckedPeople="",
                            # IsStandard=IsStandard,
                            # QAConfirmPeople="",
                            OperationDate=datetime.datetime.now()
                        ))
                else:
                    oclasss = db_session.query(EquipmentWork).filter(EquipmentWork.PUID == PUID,EquipmentWork.BatchID == BatchID).all()
                    for oc in oclasss:
                        oc.CheckedPeople = current_user.Name
                        oc.OperationDate = datetime.datetime.now()
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "设备工作情况确认报错Error：" + str(e), current_user.Name)
            return  "设备工作情况确认报错Error"

# 新加流程确认复核
@app.route('/addNewReadyWork', methods=['POST', 'GET'])
def addNewReadyWork():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                PUID = data['PUID']
                BatchID = data['BatchID']
                # EQPName = data['EQPName']
                # EQPCode = data['EQPCode']
                # ISNormal = data['ISNormal']
                # IsStandard = data['IsStandard']
                confirm = data['confirm']
                if (confirm == "1"):
                    db_session.add(
                        EquipmentWork(
                            BatchID=BatchID,
                            PUID=PUID,
                            # EQPName=EQPName,
                            # EQPCode=EQPCode,
                            # ISNormal=ISNormal,
                            OperationPeople=current_user.Name,
                            # CheckedPeople="",
                            # IsStandard=IsStandard,
                            # QAConfirmPeople="",
                            OperationDate=datetime.datetime.now()
                        ))
                else:
                    oclasss = db_session.query(EquipmentWork.CheckedPeople).filter(EquipmentWork.PUID == PUID,
                                                                                   EquipmentWork.BatchID == BatchID).all()
                    for oc in oclasss:
                        oc.CheckedPeople = current_user.Name
                        oc.OperationDate = datetime.datetime.now()
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "新加流程确认复核报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

# 备料操作按SOP执行物料列表明细
@app.route('/addNewZYPlanMaterial', methods=['POST', 'GET'])
def addNewZYPlanMaterial():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                PUID = data['PUID']
                BatchID = data['BatchID']
                MaterialName = data['MaterialName']# 物料名称
                MaterialCode = data['MaterialCode']# 物料号
                CheckedCode = data['CheckedCode']# 检验单号
                Count = data['Count']# 数量
                TankNum = data['TankNum']  # 罐号
                Unit = data['Unit']  # 单位
                db_session.add(
                    NewZYPlanMaterial(
                        MaterialName=MaterialName,
                        MaterialCode=MaterialCode,
                        BatchID=BatchID,
                        CheckedCode=CheckedCode,
                        PUID=PUID,
                        Count=Count,
                        TankNum=TankNum,
                        Unit=Unit,
                        EnterTime=datetime.datetime.now()
                    ))
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "备料操作按SOP执行物料列表明细保存报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

# 收粉结束，包装材料统计
@app.route('/addPackMaterial', methods=['POST', 'GET'])
def addPackMaterial():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                PUID = data['PUID']
                BatchID = data['BatchID']
                MaterialName = data['MaterialName']
                MaterialCode = data['MaterialCode']
                ReadyUnit = data['ReadyUnit']
                UserUnit = data['UserUnit']
                SurplusUnit = data['SurplusUnit']
                DefectiveUnit = data['DefectiveUnit']
                AttritionUnit = data['AttritionUnit']
                CancelStocksUnit = data['CancelStocksUnit']
                OperationPeople = data['OperationPeople']
                CheckedPeople = data['CheckedPeople']
                QAConfirmPeople = data['QAConfirmPeople']
                confirm = data['confirm']
                if (confirm == "1"):
                    db_session.add(
                        PackMaterial(
                            MaterialName=MaterialName,
                            MaterialCode=MaterialCode,
                            BatchID=BatchID,
                            ReadyUnit=ReadyUnit,
                            UserUnit=UserUnit,
                            SurplusUnit=SurplusUnit,
                            DefectiveUnit=DefectiveUnit,
                            AttritionUnit=AttritionUnit,
                            CancelStocksUnit=CancelStocksUnit,
                            OperationPeople=OperationPeople,
                            CheckedPeople=CheckedPeople,
                            QAConfirmPeople=QAConfirmPeople,
                            PUID=PUID,
                            OperationDate=datetime.datetime.now()
                        ))
                else:
                    oclasss = db_session.query(PackMaterial.CheckedPeople).filter(PackMaterial.PUID == PUID,
                                                                                  PackMaterial.BatchID == BatchID).all()
                    for oc in oclasss:
                        oc.CheckedPeople = current_user.Name
                        oc.OperationDate = datetime.datetime.now()
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "收粉结束，包装材料统计报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

# 煎煮段数据提取
@app.route('/electionBatchSearch')
def electionBatchSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                PName = data['PName']
                BatchID = data['BatchID']
                Pclass = db_session.query(ProductUnitRoute).filter(ProductUnitRoute.PDUnitRouteName == PName).first()
                if(Pclass.PDUnitRouteName == "煎煮段"):
                    EQPCodes = db_session.query(ElectronicBatch.EQPCode).distinct().filter(ElectronicBatch.BatchID == BatchID,
                                                                                  ElectronicBatch.PDUnitRouteCode == "提取").all()
                    EQPNames = {}#提取罐号
                    starttimes = {}#开始时间
                    endtimes = {}#结束时间
                    firstaddwaters = {}#第一次加入药材量6倍水
                    time1s = {}#一次煎煮
                    value1s = {}  # 一次煎煮
                    time2s = {}  # 二次煎煮
                    value2s = {}  # 二次煎煮
                    jstarttimes = {}  # 开始时间
                    jendtimes = {}  # 结束时间
                    for i in range(len(EQPCodes)):
                        EQPName = db_session.query(Equipment.EQPName).filter(Equipment.EQPCode == EQPCodes[i]).first()
                        EQPNames["EQPName"+str(i)] = EQPName[0]
                        Eos = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                       ElectronicBatch.EQPCode ==
                                                                       EQPCodes[i],
                                                                       ElectronicBatch.PDUnitRouteCode == "提取").order_by(
                            desc("SampleDate")).all()
                        for j in range(len(Eos)):
                            if (j == 0):
                                starttimes["starttime"+str(j)] = str(Eos[j].SampleDate)[0:-7]
                            if (j == len(Eos)-1):
                                endtimes["endtime" + str(j)] = str(Eos[j].SampleDate)[0:-7]
                        ss = "PV_"+str(EQPCodes[i])[2:-3]+"_Accumlation"
                        occs = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                       ElectronicBatch.EQPCode ==
                                                                       EQPCodes[i],
                                                                       ElectronicBatch.PDUnitRouteCode == "提取",ElectronicBatch.OpcTagID == ss).first()
                        if(occs != None):
                            firstaddwaters["firstaddwater"+str(i)] = occs.SampleValue + occs.Unit
                        else:
                            firstaddwaters["firstaddwater" + str(i)] = ""
                        esss = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                        ElectronicBatch.EQPCode ==
                                                                        EQPCodes[i],
                                                                        ElectronicBatch.PDUnitRouteCode == "提取",
                                                                        ElectronicBatch.RepeatCount == 1).all()
                        for i in range(len(esss)):
                            time1s["time1s"+str(i)] = str(esss[i].SampleDate)[10:-10]
                            value1s["value1s"+str(i)] = esss[i].SampleValue
                        esssa = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                        ElectronicBatch.EQPCode ==
                                                                        EQPCodes[i],
                                                                        ElectronicBatch.PDUnitRouteCode == "提取",
                                                                        ElectronicBatch.RepeatCount == 2).all()
                        for i in range(len(esssa)):
                            time2s["time2s" + str(i)] = str(esssa[i].SampleDate)[10:-10]
                            value2s["value2s" + str(i)] = esssa[i].SampleValue
                        Eos = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                       ElectronicBatch.EQPCode ==
                                                                       EQPCodes[i],
                                                                       ElectronicBatch.PDUnitRouteCode == "静置").order_by(
                            desc("SampleDate")).all()
                        for j in range(len(Eos)):
                            if (j == 0):
                                jstarttimes["jstarttime" + str(j)] = str(Eos[j].SampleDate)[10:-10]
                            if (j == len(Eos)-1):
                                jendtimes["jendtime" + str(j)] = str(Eos[j].SampleDate)[10:-10]
                    dic = {}
                    dic["EQPNames"] = EQPNames
                    dic["starttimes"] = starttimes
                    dic["endtimes"] = endtimes
                    dic["firstaddwaters"] = firstaddwaters
                    dic["time1s"] = time1s
                    dic["value1s"] = value1s
                    dic["time2s"] = time2s
                    dic["value2s"] = value2s
                    dic["jstarttimes"] = jstarttimes
                    dic["jendtimes"] = jendtimes
                    print(dic)
                    return json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
                elif (Pclass.PDUnitRouteName == "浓缩段"):
                    EQPCodes = db_session.query(ElectronicBatch.EQPCode).distinct().filter(
                        ElectronicBatch.BatchID == BatchID,
                        ElectronicBatch.PDUnitRouteCode == "MVR").all()
                    EQPNames = {}  # 提取罐号
                    starttimes = {}  # 开始时间
                    endtimes = {}  # 结束时间
                    zkds = {}#真空度
                    zkdtimes = {}#真空度时间
                    wds = {}  # 温度
                    wdstimes = {}#温度时间
                    for i in range(len(EQPCodes)):
                        EQPName = db_session.query(Equipment.EQPName).filter(Equipment.EQPCode == EQPCodes[i]).first()
                        EQPNames["EQPName" + str(i)] = EQPName[0]
                        Eos = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                       ElectronicBatch.EQPCode ==
                                                                       EQPCodes[i],
                                                                       ElectronicBatch.PDUnitRouteCode == "MVR").order_by(
                            desc("SampleDate")).all()
                        for j in range(len(Eos)):
                            if (j == 0):
                                starttimes["starttime" + str(j)] = str(Eos[j].SampleDate)[0:-7]
                            if (j == len(Eos) - 1):
                                endtimes["endtime" + str(j)] = str(Eos[j].SampleDate)[0:-7]
                        Num = str(EQPCodes[i])[5:-3]
                        zk = "B24_" + Num
                        wd = "TT002_" + Num

                        occs = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                        ElectronicBatch.EQPCode ==
                                                                        EQPCodes[i],
                                                                        ElectronicBatch.PDUnitRouteCode == "MVR",
                                                                        ElectronicBatch.OpcTagID == zk).all()
                        if (occs != None):
                            for j in range(len(occs)):
                                zkds["zkd" + str(j)] = occs[j].SampleValue + occs.Unit
                                zkdtimes["zkd" + str(j)] = str(occs[j].SampleDate)[10:-10]
                        else:
                            zkds["zkd" + str(i)] = ""
                            zkdtimes["zkd" + str(j)] = ""
                        esss = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                        ElectronicBatch.EQPCode ==
                                                                        EQPCodes[i],
                                                                        ElectronicBatch.PDUnitRouteCode == "MVR",
                                                                        ElectronicBatch.OpcTagID == wd).all()
                        for i in range(len(esss)):
                            zkds["time1s" + str(i)] = str(esss[i].SampleDate)[10:-10]
                            zkds["value1s" + str(i)] = esss[i].SampleValue
                        occs = db_session.query(ElectronicBatch).filter(ElectronicBatch.BatchID == BatchID,
                                                                        ElectronicBatch.EQPCode ==
                                                                        EQPCodes[i],
                                                                        ElectronicBatch.PDUnitRouteCode == "MVR",
                                                                        ElectronicBatch.OpcTagID == zk).all()
                        if (occs != None):
                            for j in range(len(occs)):
                                zkds["zkd" + str(j)] = occs[j].SampleValue + occs.Unit
                                zkdtimes["zkd" + str(j)] = str(occs[j].SampleDate)[10:-10]
                        else:
                            zkds["zkd" + str(i)] = ""
                            zkdtimes["zkd" + str(j)] = ""
                    dic = {}
                    dic["EQPNames"] = EQPNames
                    dic["starttimes"] = starttimes
                    dic["endtimes"] = endtimes
                    dic["zkds"] = zkds
                    dic["wds"] = wds
                    # dic["time2s"] = time2s
                    # dic["value2s"] = value2s
                    print(dic)
                    return json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "收粉结束，包装材料统计报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

# QA放行
@app.route('/QAauthPass')
def QApass():
    return render_template('QAPassAuth.html')

#批物料平衡审核人确认
@app.route('/CheckedBatchMaterielBalance', methods=['POST', 'GET'])
def CheckedBatchMaterielBalance():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                ID = data['ID']  # 计划ID
                PName = data['PName']  # 工艺段名称
                CheckedSuggestion = data['CheckedSuggestion']  # 审核意见
                DeviationDescription = data['DeviationDescription']  # 偏差说明
                PMClass = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                PUID = db_session.query(ProductUnitRoute.PUID).filter(ProductUnitRoute.PDUnitRouteName == PName, ProductUnitRoute.ProductRuleID == PMClass.BrandID).first()
                db_session.add(
                    BatchMaterielBalance(
                        PlanManagerID=PMClass.ID,
                        PUID=PUID,
                        DeviationDescription=DeviationDescription,
                        CheckedSuggestion=CheckedSuggestion,
                        CheckedPerson=current_user.Name,
                        OperationDate=datetime.datetime.now()
                    ))
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "批物料平衡审核人确认报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 查询批物料平衡审核人确认信息
@app.route('/MaterielBalanceCheckedInfoSearch')
def MaterielBalanceCheckedInfoSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                ID = data['ID']  # 计划ID
                PName = data['PName']  # 工艺段名称
                PMClass = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                PUID = db_session.query(ProductUnitRoute.PUID).filter(ProductUnitRoute.PDUnitRouteName == PName,
                                                                      ProductUnitRoute.ProductRuleID == PMClass.BrandID).first()
                oclass = db_session.query(BatchMaterielBalance).filter(BatchMaterielBalance.PlanManagerID == ID, BatchMaterielBalance.PUID == PUID).first()
                return json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询批物料平衡审核人确认信息报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

#批物料平衡工序负责人确认
@app.route('/PUIDChargeBatchMaterielBalance', methods=['POST', 'GET'])
def PUIDChargeBatchMaterielBalance():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                ID = data['ID']  # 计划ID
                PName = data['PName']  # 工艺段名称
                OperationSpaceNum = data['OperationSpaceNum']  # 操作间编号
                PMClass = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                PUID = db_session.query(ProductUnitRoute.PUID).filter(ProductUnitRoute.PDUnitRouteName == PName, ProductUnitRoute.ProductRuleID == PMClass.BrandID).first()
                oclass = db_session.query(BatchMaterielBalance).filter(BatchMaterielBalance.PlanManagerID == PMClass.ID, BatchMaterielBalance.PUID == PUID)
                if(oclass == None):
                    return "请先进行批物料平衡审核人确认！"
                oclass.PUIDChargePerson = current_user.Name
                oclass.OperationSpaceNum = OperationSpaceNum
                oclass.OperationDate = datetime.datetime.now()
                db_session.commit()
                return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "批物料平衡工序负责人确认报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#查询批物料平衡
@app.route('/MaterielBalanceSearch')
def MaterielBalanceSearch():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                pages = int(data['page'])  # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                Name = current_user.Name
                BatchID = data['BatchID']
                BrandName = data['name']
                if BatchID == None or BatchID == "":
                    total = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus.in_((20, 40, 50, 60, 70)), PlanManager.BrandName == BrandName).count()
                    oclass = db_session.query(PlanManager).filter(PlanManager.PlanStatus.in_((20, 40, 50, 60, 70)), PlanManager.BrandName == BrandName).order_by(desc("PlanBeginTime")).all()[inipage:endpage]
                else:
                    total = db_session.query(PlanManager.ID).filter(PlanManager.BatchID == BatchID, PlanManager.BrandName == BrandName,
                        PlanManager.PlanStatus.in_((20, 40, 50, 60, 70))).count()
                    oclass = db_session.query(PlanManager).filter(PlanManager.BatchID == BatchID, PlanManager.BrandName == BrandName,
                        PlanManager.PlanStatus.in_((20, 40, 50, 60, 70))).order_by(desc("PlanBeginTime")).all()[
                             inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询批物料平衡报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 查询待办
@app.route('/maindaiban')
def maindaiban():
    if request.method == 'GET':
        data = request.values
        try:
            # pages = int(data['offset'])  # 页数
            # rowsnumber = int(data['limit'])  # 行数
            # inipage = pages * rowsnumber + 0  # 起始页
            # endpage = pages * rowsnumber + rowsnumber  # 截止页
            # Name = current_user.Name
            oclass = db_session.query(PlanManager).filter(PlanManager.PlanStatus != "70").order_by(
                desc("PlanBeginTime")).all()
            return json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
            # roleclass = db_session.query(Role).join(User, Role.RoleName == User.RoleName).filter(User.Name == Name).all()
            # for rol in roleclass:
            #     Role_Menuclass = db_session.query(Role_Menu).filter(Role_Menu.Role_ID == rol.ID).all()
            #     for men in Role_Menuclass:
            #         db_session.query(Menu).filter()
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "查询待办报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)

#首页查询
@app.route('/souyesearch')
def souyesearch():
    if request.method == 'GET':
        data = request.values
        try:
            A = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus == "10").count()
            B = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus == "11").count()
            C = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus == "60").count()
            D = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus.in_((20, 40, 50, 60, 70))).count()
            return '{"A"' + ":" + str(A) + ',"B"' + ":" + str(B) + ',"C"' + ":" + str(C) +',"D"' + ":" + str(D)+ "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "首页查询报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 批记录查询
@app.route('/batchjiluSearch')
def batchjiluSearch():
    if request.method == 'GET':
        data = request.values
        try:
            PUID = data["PUID"]
            BatchID = data["BatchID"]
            oclasss = db_session.query(NewReadyWork).filter(NewReadyWork.PUID == PUID, NewReadyWork.BatchID == BatchID).all()
            dic = {}
            for oclass in oclasss:
                if(oclass.Type=="1"):
                    dic["s1"] = oclass.ISConfirm
                    dic["StartTime1"] = str(oclass.StartTime)
                    dic["EndTime1"] = str(oclass.EndTime)
                elif (oclass.Type == "2"):
                    dic["s2"] = oclass.ISConfirm
                elif (oclass.Type == "3"):
                    dic["s3"] = oclass.ISConfirm
                elif (oclass.Type == "4"):
                    dic["s4"] = oclass.ISConfirm
                elif (oclass.Type == "5"):
                    dic["s5"] = oclass.ISConfirm
                elif (oclass.Type == "6"):
                    dic["s6"] = oclass.ISConfirm
                elif (oclass.Type == "7"):
                    dic["s7"] = oclass.ISConfirm
                elif (oclass.Type == "8"):
                    dic["s8"] = oclass.ISConfirm
                    dic["StartTime2"] = str(oclass.StartTime)
                    dic["EndTime2"] = str(oclass.EndTime)
                    dic["OperationPeople2"] = oclass.OperationPeople
                    dic["CheckedPeople2"] = oclass.CheckedPeople
                    dic["QAConfirmPeople2"] = oclass.QAConfirmPeople
                elif (oclass.Type == "9"):
                    dic["s9"] = oclass.ISConfirm
                elif (oclass.Type == "10"):
                    dic["s10"] = oclass.ISConfirm
                elif (oclass.Type == "11"):
                    dic["s11"] = oclass.ISConfirm
                elif (oclass.Type == "12"):
                    dic["s12"] = oclass.ISConfirm
                elif (oclass.Type == "13"):
                    dic["s13"] = oclass.ISConfirm
                elif (oclass.Type == "14"):
                    dic["s14"] = oclass.ISConfirm
            print(dic)
            return json.dumps(dic, cls=AlchemyEncoder, ensure_ascii=False)
            A = db_session.query(OperationProcedure.OperationpValue).filter(OperationProcedure.EQPCode == "10").count()
            B = db_session.query(ElectronicBatch.SampleValue).filter(PlanManager.PlanStatus == "11").count()
            C = db_session.query(QualityControl.Temperature).filter(PlanManager.PlanStatus == "60").count()
            return '{"A"' + ":" + str(A) + ',"B"' + ":" + str(B) + ',"C"' + ":" + str(C) + ',"D"' + ":" + str(C) + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "首页查询报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)


# 操作手册
@app.route('/CreateOperationManual', methods=['POST', 'GET'])
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

# 收粉监控画面
@app.route('/processMonitorLineCollect')
def processMonitorLineCollect():
    return render_template('processMonitorLineCollect.html')

def getExcel(file, method='r'):
    '''
    改变数据结构 -- 方便前端显示
    :param filename:  文件名
    :param method:  按照 列或者 行 返回数据
    '''
    data = xlrd.open_workbook(file)
    table = data.sheets()[0]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    if method == 'r':
        row_list = [table.row_values(i) for i in range(0, nrows)]  # 所有行的数据
        return row_list
    elif method == 'c':
        col_list = [table.col_values(i) for i in range(0, ncols)]  # 所有列的数据
        return col_list

# NodeID注释配置
@app.route('/NodeIdNote/config', methods=['POST', 'GET'])
def nodeIdNote():
    if request.method == 'GET':
        return render_template('nodeIDNote.html')
    if request.method == 'POST':
        try:
            nodes = [] # 收集为匹配的变量
            x = 0 # Excel横坐标
            y = 0 # Excel纵坐标
            file = request.files.get('note')
            if file is None or file == '':
                return
            file.save(os.path.join(os.getcwd(), file.filename))
            new_file = '%s%s%s'%(os.getcwd(), "\\", file.filename)
            data = getExcel(new_file)
            for index in data:
                if index[1].lower() == 'note': #去表头
                    continue
                elements = ('ns=1;s=t|', 'ns=1;s=f|')
                for element in elements:  #将注释Note插入OpcTag中
                    nodeId = element + index[0]
                    opcTag = db_session.query(OpcTag.NodeID).filter_by(NodeID=nodeId).first()
                    if opcTag is None:
                        nodes.append(index[0])
                        continue
                    opcTag.Note = index[1]
                    db_session.add(opcTag)
                    db_session.commit()
                    # 读取excel数据录入NodeIdNote数据表
                    oclass = db_session.query(NodeIdNote).filter_by(NodeID=nodeId).first()
                    if oclass is not None:
                        db_session.delete(oclass)
                        db_session.commit()
                    if len(index) == 2:
                        db_session.add(NodeIdNote(
                                NodeID=nodeId,
                                Note=index[1]))
                        try:
                            db_session.commit()
                        except:
                            db_session.rollback()
            # 将未匹配注释的变量生成一个新的Excel
            workbook = xlwt.Workbook(encoding='utf-8', style_compression=0)
            sheet = workbook.add_sheet('note', cell_overwrite_ok=True)
            sheet.write(x, y, 'NodeID')
            for node in set(nodes):
                x += 1
                sheet.write(x, y, node)
            path = r'C:\Users\maomao\Desktop\{}{}{}'.format('nodeId', datetime.datetime.now(), '.xlsx')
            workbook.save(path)
            return redirect(url_for('nodeIdNote'))
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Excel数据读取失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/NodeIdNote/Find')
def NodeIdNoteFind():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = db_session.query(NodeIdNote.ID).count()
                if total > 0:
                    qDatas = db_session.query(NodeIdNote).all()[inipage:endpage]
                    # ORM模型转换json格式
                    jsonNodeIdNote = json.dumps(qDatas, cls=Model.BSFramwork.AlchemyEncoder,
                                                 ensure_ascii=False)
                    jsonNodeIdNote = '{"total"' + ":" + str(
                        total) + ',"rows"' + ":\n" + jsonNodeIdNote + "}"
                    return jsonNodeIdNote
                else:
                    return ""
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "NodeIdNote数据加载失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


@app.route('/NodeIdNote/Create', methods=['POST', 'GET'])
def NodeIdNoteCreate():
    if request.method == 'POST':
        try:
            data = request.values
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                db_session.add(
                    NodeIdNote(
                        NodeID=data['NodeID'],
                        Note=data['Note']
                    ))
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "NodeIdNote数据创建失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


@app.route('/NodeIdNote/Delete', methods=['POST', 'GET'])
def NodeIdNoteDelete():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    NodeIdNoteID = int(key)
                    try:
                        oclass = db_session.query(NodeIdNote).filter_by(ID=NodeIdNoteID).first()
                        db_session.delete(oclass)
                        db_session.commit()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "NodeIdNote数据删除失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


@app.route('/NodeIdNote/Update', methods=['POST', 'GET'])
def NodeIdNoteUpdate():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                NodeIdNoteID = int(data['ID'])
                oclass = db_session.query(NodeIdNote).filter_by(ID=NodeIdNoteID).first()
                oclass.NodeID = data['NodeID']
                oclass.Note = data['Note']
                db_session.add(oclass)
                db_session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "NodeIdNote数据更新失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@app.route('/NodeIdNote/Search', methods=['POST', 'GET'])
def NodeIdNoteSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                NodeID = "%" + data['NodeID'] + "%"
                count = db_session.query(NodeIdNote).filter(
                    NodeIdNote.NodeID.like(NodeID)).all()
                total = Counter(count)
                jsonNotes = json.dumps(count, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                jsonNotes = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonNotes + "}"
                return jsonNotes
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "NodeIdNote数据查询失败报错Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 质量管理
# 过程连续数据
@app.route('/ProcessContinuousData')
def processContinuousData():
    return render_template('BatchData_Process.html')

# 过程连续数据——Data
@app.route('/ProcessContinuousData/DataPart')
def DataPart():
    return render_template('BatchData_Process_Data.html')

# 过程连续数据——彩虹图
@app.route('/ProcessContinuousData/Rainbow')
def Rainbow():
    return render_template('BatchData_Process_Trend.html')

# 过程连续数据——CPK
@app.route('/ProcessContinuousData/CPK')
def CPK():
    return render_template('BatchData_Process_CPK.html')

# 过程连续数据—— 直方图
@app.route('/ProcessContinuousData/Histogram')
def histogram():
    return render_template('BatchData_Process_Histogram.html')

#离散数据录入
@app.route('/DiscreteDataEntry')
def discreteDataEntry():
    return render_template('DataEntry_Discrete.html')

# 统计-数据点
@app.route('/StatisticDataSpot')
def statisticDataSpot():
    return render_template('DataSpot_Statistic.html')

# 统计-数据点-批次数据列表
@app.route('/StatisticDataSpot/BatchDataList')
def BatchDataList():
    return render_template('BatchStatistics_Point_Data.html')

# 统计-数据点-批次数据趋势
@app.route('/StatisticDataSpot/BatchDataTrend')
def BatchDataTrend():
    return render_template('BatchStatistics_Point_Trend.html')

# 统计-数据点-批次数据CPK
@app.route('/StatisticDataSpot/BatchDataCPK')
def BatchDataCPK():
    return render_template('BatchStatistics_Point_CPK.html')

# 统计-数据点-批次数据直方图
@app.route('/StatisticDataSpot/BatchDataHistogram')
def BatchDataHistogram():
    return render_template('BatchStatistics_Point_Histogram.html')

# 质量标准管理
@app.route('/QualityStandardManagement')
def qualityStandardManagement():
    return render_template('QualityStandard_Management.html')

# 生产数据管理-电子批记录
@app.route('/ElectronicBatchRecord')
def ElectronicBatchRecord():
    return render_template('ElectronicBatchRecordParent.html')

# 生产数据管理-批物料平衡统计
@app.route('/BatchMaterielBalanceStatistic')
def BatchMaterielBalanceStatistic():
    return render_template('BatchMaterielBalanceStatistic.html')

if __name__ == '__main__':
    app.run(debug=True)