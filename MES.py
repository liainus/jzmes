import datetime
import decimal
import json
import os
import re
import string
import time
from collections import Counter
from flask import Flask, jsonify, redirect, url_for, flash
import xlrd
from flask import Flask, jsonify, redirect, url_for
from flask import render_template, request
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
    CollectTaskCollection, ReadyWork, NodeIdNote
from Model.system import Role, Organization, User, Menu, Role_Menu
from tools.MESLogger import MESLogger
from Model.core import SysLog
from sqlalchemy import func
import string
import re
from collections import Counter
from Model.system import User
from Model.Global import WeightUnit
from Model.control import ctrlPlan
from flask_login import LoginManager, current_user
from flask.ext.login import login_required, logout_user, login_user
import socket
from opcua import Client
from Model.dynamic_model import make_dynamic_classes
import Model.node

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


# 加载工作台
# 左右滑动添加
@app.route('/batchmanager')  # 批次管理
def batchmanager():
    productUnit_ID = db_session.query(ProcessUnit.ID, ProcessUnit.PUName).all()
    data = []
    for tu in productUnit_ID:
        li = list(tu)
        id = li[0]
        name = li[1]
        pro_unit_id = {'ID': id, 'text': name}
        data.append(pro_unit_id)
    return render_template('batch_manager.html',Product_unit_ID=data)

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
                planMa = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                total = db_session.query(ZYPlan.ID).filter(ZYPlan.BatchID == planMa.BatchID).count()
                zYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == planMa.BatchID).order_by(desc("EnterTime")).all()[
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
                plan = db_session.query(ZYPlan).filter(ZYPlan.ID == ID)
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
                    total = db_session.query(Pequipment).count()
                    pequipments = db_session.query(Pequipment).all()[inipage:endpage]
                else:
                    total = db_session.query(Pequipment).filter(Pequipment.EQPName.like("%" + EQPName + "%")).count()
                    pequipments = db_session.query(Pequipment).filter(Pequipment.EQPName.like("%" + EQPName + "%")).all()[inipage:endpage]
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
                session.commit()
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
                oclass = session.query(Pequipment).filter_by(ID=id).first()
                oclass.EQPCode=data['EQPCode']
                oclass.EQPName=data['EQPName']
                oclass.PUID=data['PUID']
                oclass.Desc=data['Desc']
                session.commit()
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
                        oclass = session.query(Pequipment).filter_by(ID=id).first()
                        session.delete(oclass)
                        session.commit()
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

            # 查询Opc服务


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

def getOpcTagList(id, ParentID=None):
    sz = []
    try:
        opcTags = db_session.query(OpcTag).all()
        for obj in opcTags:
            if obj.ParentID == ParentID:
                sz.append({"id": obj.ID,
                           "NodeId": obj.NodeID,
                           "Desc": obj.Note,
                           "children": getOpcTagList(obj.ID, obj.NodeID)})
        return sz
    except Exception as e:
        print(e)
        logger.error(e)
        insertSyslog("error", "getOpcTagList加载父级菜单列表报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/CollectParams/OpcTagLoad', methods=['POST', 'GET'])
def OpcTagLoad():
    if request.method == 'POST':
        try:
            data = getOpcTagList(id=0)
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
            json_str = json.dumps(data.to_dict())
            CollectParamsTemplateID = data['CollectParamsTemplateID']
            nodeIds = data['OpcTags'] # [{"nodeId":"i=2259"},{"nodeId":"i=2258"}]
            nodeIds = re.findall(r"i=\d+", nodeIds)
            if CollectParamsTemplateID is None or nodeIds is None:
                return
            if len(json_str) > 10:
                for nodeId in nodeIds:
                    OpcTagID = db_session.query(OpcTag.ID).filter_by(NodeID=nodeId).first()[0]
                    # 判断当前模板是否存在
                    object = db_session.query(CollectParams).filter(and_(CollectParams.OpcTagID==OpcTagID,CollectParams.CollectParamsTemplateID==CollectParamsTemplateID)).first()
                    if object is not None:
                        db_session.delete(object)
                        db_session.commit()
                        db_session.add(
                            CollectParams(
                                CollectParamsTemplateID=CollectParamsTemplateID,
                                OpcTagID=OpcTagID))
                        db_session.commit()
                    else:
                        db_session.add(CollectParams(CollectParamsTemplateID=CollectParamsTemplateID,
                                                     OpcTagID=OpcTagID))
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
                NodeID = data['NodeID']
                nodeIds = re.findall(r"i=\d+", NodeID)
                if nodeIds is None:
                    return
                for nodeId in nodeIds:
                    OpcTagID = db_session.query(OpcTag.ID).filter_by(NodeID=nodeId).first()[0]
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

            # 查询Opc服务


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

            # 查询Opc服务


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
    for name in TempNames:
        li = list(name)
        name = li[0]
        temp_name = {'tempName': name}
        TemplateNames.append(temp_name)
    StrategyNames = []
    straNames = db_session.query(Collectionstrategy.StrategyName).all()
    for name in straNames:
        li = list(name)
        name = li[0]
        stra_name = {'straName': name}
        StrategyNames.append(stra_name)
    CollectTaskNames = []
    TaskNames = db_session.query(CollectTask.CollectTaskName).all()
    for name in TaskNames:
        li = list(name)
        name = li[0]
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

            # 查询Opc服务


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

            # 查询Opc服务


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

#任务确认
@app.route('/taskConfirm')
def taskConfirm():
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

#任务确认查询任务
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
                APUID = data['PUID']  # 工艺段编码
                TaskStatus = data['TaskStatus']  # 任务的执行状态
                BatchID = data['BatchID']#批次号
                if(APUID == "" and TaskStatus == ""):
                    total = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32,40,50))).count()
                    ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32,40,50))).order_by(desc("EnterTime")).all()[inipage:endpage]
                elif(APUID != "" and TaskStatus == "" and BatchID == ""):
                    total = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32, 40, 50)),
                                                            ZYTask.PUID == APUID).count()
                    ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus.in_((32, 40, 50)),
                                                              ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
                elif(APUID != "" and TaskStatus == "" and BatchID != ""):
                    total = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
                                                            ZYTask.TaskStatus.in_((32, 40, 50)),
                                                            ZYTask.PUID == APUID).count()
                    ZYTasks = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
                                                              ZYTask.TaskStatus.in_((32, 40, 50)),
                                                              ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
                elif (APUID == "" and TaskStatus != ""):
                    total = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus).count()
                    ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus).order_by(desc("EnterTime")).all()[inipage:endpage]
                elif (APUID != "" and TaskStatus != "" and BatchID == ""):
                    total = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus,
                                                            ZYTask.PUID == APUID).count()
                    ZYTasks = db_session.query(ZYTask).filter(ZYTask.TaskStatus == TaskStatus,
                                                              ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
                elif (APUID != "" and TaskStatus != "" and BatchID != ""):
                    total = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
                                                            ZYTask.TaskStatus == TaskStatus,
                                                            ZYTask.PUID == APUID).count()
                    ZYTasks = db_session.query(ZYTask).filter(ZYTask.BatchID == BatchID,
                                                              ZYTask.TaskStatus == TaskStatus,
                                                              ZYTask.PUID == APUID).order_by(desc("EnterTime")).all()[inipage:endpage]
                jsonZYTasks = json.dumps(ZYTasks, cls=AlchemyEncoder, ensure_ascii=False)
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
                equipmentNames = db_session.query(Pequipment.EQPCode,Pequipment.EQPName).filter(Pequipment.PUID == 1)
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
                oclass.EquipmentID = EQPCode
                oclass.TaskStatus = Model.Global.TASKSTATUS.COMFIRM.value
                db_session.commit()
                oclassplan = db_session.query(ZYPlan).filter(ZYPlan.PUID == oclass.PUID, ZYPlan.BatchID == oclass.BatchID).first()
                oclasstasks = db_session.query(ZYTask).filter(ZYTask.PUID == oclass.PUID,
                                                             ZYTask.BatchID == oclass.BatchID).all()
                flag = "TRUE"
                for task in oclasstasks:
                    if(task.TaskStatus != Model.Global.TASKSTATUS.COMFIRM.value):
                        flag = "FALSE"
                if(flag == "TRUE"):
                    oclassplan.ZYPlanStatus = Model.Global.ZYPlanStatus.COMFIRM.value
                    db_session.commit()
                return "OK"
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "任务确认保存设备code报错Error：" + str(e), current_user.Name)
            return "NO"

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


# 中控确认
@app.route('/MiddleControl/PlanConfirm')
def PlanConfirm():
    return render_template('MiddleControlPlanConfirm.html')

# 中控确认查询
@app.route('/ZYPlanGuid/controlConfirmSearch', methods=['POST', 'GET'])
def controlConfirmSearch():
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
                    total = db_session.query(ZYPlan.ID).filter(ZYPlan.ZYPlanStatus.in_((20, 60))).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.ZYPlanStatus.in_((20, 60))).order_by(desc("EnterTime")).all()[
                              inipage:endpage]
                else:
                    total = db_session.query(ZYPlan).filter(ZYPlan.BatchID == ABatchID,
                                                            ZYPlan.ZYPlanStatus.in_((20, 60))).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == ABatchID,
                                                              ZYPlan.ZYPlanStatus.in_((20, 60))).order_by(desc("EnterTime")).all()[
                              inipage:endpage]
                ZYPlans = json.dumps(ZYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonZYPlans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + ZYPlans + "}"
                return jsonZYPlans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "中控确认查询报错Error：" + str(e), current_user.Name)

# 中控确认保存信息查询
@app.route('/ZYPlanGuid/ConfirmSearchInfo', methods=['POST', 'GET'])
def ConfirmSearchInfo():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ZYPlanID = int(data["ZYPlanID"])
                oclass = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ZYPlanID, ReadyWork.ProductionFlag == "0").all()
                return json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "中控确认保存信息报错Error：" + str(e), current_user.Name)

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

# 中控计划确认
@app.route('/ZYPlanGuid/controlConfirm', methods=['POST', 'GET'])
def controlConfirm():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
            ID = int(jsonnumber[0])
            roclass = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ID, ReadyWork.ProductionFlag == "0").all()
            for ro in roclass:
                if(ro.IsCheck=="0"):
                    return "还有准备工作未确认，请确认再提交！"
                else:
                    pass
            zyp = db_session.query(ZYPlan).filter(ZYPlan.ID == ID).first()
            zyp.ZYPlanStatus = Model.Global.ZYPlanStatus.Control.value
            # flag = "TRUE"
            # zyplans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == zyp.BatchID).all()
            db_session.commit()
            # for z in zyplans:
            #     if(z.ZYPlanStatus != Model.Global.ZYPlanStatus.Control.value):
            #         flag = "FALSE"
            userName = current_user.Name
            # if(flag == "TRUE"):
            #     oclass = db_session.query(PlanManager).filter(PlanManager.BatchID == zyp.BatchID).first()
            #     oclassW = db_session.query(WorkFlowStatus).filter(WorkFlowStatus.PlanManageID==oclass.ID).all()
            #     for oc in oclassW:
            #         oc.AuditStatus = Model.Global.AuditStatus.ClearField.value
            #         oc.DescF = "中控确认清场"
            #     db_session.commit()
            Desc = "中控确认清场"
            Type = Model.Global.TypeZY.Control.value
            PlanCreate = ctrlPlan('PlanCreate')
            wReturn = PlanCreate.createWorkFlowEventZYPlan(ID, userName, Desc, Type)
            if(wReturn == False):
                return '添加工作流表报错'
            return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "中控确认清场报错Error：" + str(e), current_user.Name)

# 中控计划复核
@app.route('/MiddleControl/PlanConfirmChecked')
def PlanConfirmChecked():
    return render_template('PlanConfirmChecked.html')

# 中控计划复核查询
@app.route('/ZYPlanGuid/controlConfirmReCheckSearch', methods=['POST', 'GET'])
def controlConfirmReCheckSearch():
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
                    total = db_session.query(ZYPlan.ID).filter(ZYPlan.ZYPlanStatus.in_((30, 61))).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.ZYPlanStatus.in_((30, 61))).order_by(desc("EnterTime")).all()[
                              inipage:endpage]
                else:
                    total = db_session.query(ZYPlan).filter(ZYPlan.BatchID == ABatchID,
                                                            ZYPlan.ZYPlanStatus.in_((30, 61))).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == ABatchID,
                                                              ZYPlan.ZYPlanStatus.in_((30, 61))).order_by(desc("EnterTime")).all()[
                              inipage:endpage]
                ZYPlans = json.dumps(ZYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonZYPlans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + ZYPlans + "}"
                return jsonZYPlans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "中控计划复核查询报错Error：" + str(e), current_user.Name)

# 中控操作复核
@app.route('/ZYPlanGuid/controlConfirmReCheck', methods=['POST', 'GET'])
def controlConfirmReCheck():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
            for key in jsonnumber:
                try:
                    ID = int(key)
                    userN = db_session.query(WorkFlowEventZYPlan.userName).filter(WorkFlowEventZYPlan.ZYPlanID == ID).first()
                    if(userN[0] == current_user.Name):
                        return "中控确认清场与中控操作复核不能是同一人操作！"
                    roclass = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ID, ReadyWork.ProductionFlag == "0").all()
                    for ro in roclass:
                        if (ro.IsCheck == "0"):
                            return "还有准备工作未确认，请确认再提交！"
                        else:
                            pass
                    zypla = db_session.query(ZYPlan).filter(ZYPlan.ID == ID).first()
                    zypla.ZYPlanStatus = Model.Global.ZYPlanStatus.ControlChecked.value
                    db_session.commit()
                    # zyplans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == zypla.BatchID).all()
                    # flag = "TRUE"
                    # for zy in zyplans:
                    #     if(zy.ZYPlanStatus != Model.Global.ZYPlanStatus.ControlChecked.value):
                    #         flag = "FALSE"
                    # oclass = db_session.query(PlanManager).filter(PlanManager.BatchID == zypla.BatchID).first()
                    userName = current_user.Name
                    # if(flag == "TRUE"):
                    #     oclassW = db_session.query(WorkFlowStatus).filter_by(PlanManageID=oclass.ID).all()
                    #     for oc in oclassW:
                    #         oc.AuditStatus = Model.Global.AuditStatus.Recheck.value
                    #         oc.DescF = "中控清场复核"
                    #     db_session.commit()
                    Desc = "中控操作复核"
                    Type = Model.Global.TypeZY.ControlChecked.value
                    PlanCreate = ctrlPlan('PlanCreate')
                    wReturn = PlanCreate.createWorkFlowEventZYPlan(ID, userName, Desc, Type)
                    if (wReturn == False):
                        return '添加工作流表报错'
                    return 'OK'
                except Exception as e:
                    db_session.rollback()
                    logger.error(e)
                    insertSyslog("error", "中控操作复核报错Error：" + str(e), current_user.Name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "中控操作复核报错Error：" + str(e), current_user.Name)

# QA复核
@app.route('/QAPlanConfirm')
def QAPlanConfirm():
    return render_template('QAPlanConfirm.html')

# QA复核查询
@app.route('/ZYPlanGuid/QAConfirmSearch', methods=['POST', 'GET'])
def QAConfirmSearch():
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
                    total = db_session.query(ZYPlan.ID).filter(ZYPlan.ZYPlanStatus.in_((31, 62))).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.ZYPlanStatus.in_((31, 62))).order_by(desc("EnterTime")).all()[inipage:endpage]
                else:
                    total = db_session.query(ZYPlan.ID).filter(ZYPlan.BatchID == ABatchID,ZYPlan.ZYPlanStatus.in_((31, 62))).count()
                    ZYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == ABatchID,ZYPlan.ZYPlanStatus.in_((31, 62))).order_by(desc("EnterTime")).all()[inipage:endpage]
                ZYPlans = json.dumps(ZYPlans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonZYPlans = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + ZYPlans + "}"
                return jsonZYPlans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "QA复核查询报错Error：" + str(e), current_user.Name)

# QA复核
@app.route('/ZYPlanGuid/QAConfirm', methods=['POST', 'GET'])
def QAConfirm():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(ZYPlan).filter(ZYPlan.ID == id).first()
                        oclassZYTasks = db_session.query(ZYTask).filter(ZYTask.BatchID == oclass.BatchID).all()
                        for Task in oclassZYTasks:
                            if(Task.TaskStatus != Model.Global.TASKSTATUS.COMFIRM.value):
                                return "请先进行任务确认，选择设备！"
                        oclass.ZYPlanStatus = Model.Global.ZYPlanStatus.QAChecked.value
                        # planmID = db_session.query(PlanManager.ID).filter(PlanManager.BatchID == oclass.BatchID).first()
                        # oclassW = db_session.query(WorkFlowStatus).filter_by(PlanManageID=planmID[0]).all()
                        # for oc in oclassW:
                        #     oc.AuditStatus = Model.Global.AuditStatus.ReviewPass.value
                        #     oc.DescF = "QA复核"
                        db_session.add(Model.core.ReadyWork(ZYPlanID=id, IsCheck="0", ReadyName="ClearFieldCard",
                                                 Describe="设备、衡器是否按照清洁SOP要求完成", ProductionFlag="1"))
                        db_session.add(Model.core.ReadyWork(ZYPlanID=id, IsCheck="0", ReadyName="ClearLastMateriel",
                                                 Describe="是否已经清除生产现场本批次药材及废弃物", ProductionFlag="1"))
                        db_session.add(Model.core.ReadyWork(ZYPlanID=id, IsCheck="0", ReadyName="ClearLastMaterielStatus",
                                                 Describe="是否已经清除本批次生产有关的状态标志或文件", ProductionFlag="1"))
                        db_session.add(Model.core.ReadyWork(ZYPlanID=id, IsCheck="0", ReadyName="ClaernEquipLocal",
                                                 Describe="工作区域、工器具、洁具是否清洁并按定置摆放", ProductionFlag="1"))
                        db_session.add(Model.core.ReadyWork(ZYPlanID=id, IsCheck="0", ReadyName="ClarnFile",
                                                 Describe="是否按《清场管理规程》进行清场", ProductionFlag="1"))
                        db_session.add(Model.core.ReadyWork(ZYPlanID=id, IsCheck="0", ReadyName="SafetyStatus",
                                                 Describe="QA对现场清场进行检查，合格后发放《清场合格证》", ProductionFlag="1"))
                        db_session.commit()
                        userName = current_user.Name
                        Desc = "QA复核"
                        Type = Model.Global.TypeZY.QAChecked.value
                        PlanCreate = ctrlPlan('PlanCreate')
                        wReturn = PlanCreate.createWorkFlowEventZYPlan(id, userName, Desc, Type)
                        if(wReturn == False):
                            return 'NO'
                        return 'OK'
                    except Exception as e:
                        db_session.rollback()
                        print(e)
                        logger.error(e)
                        insertSyslog("error", "QA复核报错Error：" + str(e), current_user.Name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "QA复核报错Error：" + str(e), current_user.Name)

# 中控再次确认保存信息查询
@app.route('/ZYPlanGuid/ConfirmSearchInfoAgain', methods=['POST', 'GET'])
def ConfirmSearchInfoAgain():
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ZYPlanID = int(data["ZYPlanID"])
                oclass = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ZYPlanID, ReadyWork.ProductionFlag == "1").all()
                return json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "中控确认保存信息报错Error：" + str(e), current_user.Name)

# 中控确认保存信息
@app.route('/ZYPlanGuid/controlConfirmSaveInfoAgain', methods=['POST', 'GET'])
def controlConfirmSaveInfoAgain():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                ZYPlanID = int(data["ZYPlanID"])
                oclassR = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ZYPlanID, ReadyWork.ProductionFlag == "1").all()
                for oc in oclassR:
                    oc.IsCheck = "0"
                for i in range(len(jsonnumber) - 1):
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

# 中控再次确认
@app.route('/ZYPlanGuid/controlConfirmAgain', methods=['POST', 'GET'])
def controlConfirmAgain():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
            ID = int(jsonnumber[0])
            roclass = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ID, ReadyWork.ProductionFlag == "1").all()
            for ro in roclass:
                if (ro.IsCheck == "0"):
                    return "还有准备工作未确认，请确认再提交！"
                else:
                    pass
            zyp = db_session.query(ZYPlan).filter(ZYPlan.ID == ID).first()
            zyp.ZYPlanStatus = Model.Global.ZYPlanStatus.AgainControl.value
            db_session.commit()
            # flag = "TRUE"
            # zyplans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == zyp.BatchID).all()
            # for z in zyplans:
            #     if (z.ZYPlanStatus != Model.Global.ZYPlanStatus.Control.value):
            #         flag = "FALSE"
            userName = current_user.Name
            # if (flag == "TRUE"):
            #     oclass = db_session.query(PlanManager).filter(PlanManager.BatchID == zyp.BatchID).first()
            #     oclassW = db_session.query(WorkFlowStatus).filter(
            #         WorkFlowStatus.PlanManageID == oclass.ID).all()
            #     for oc in oclassW:
            #         oc.AuditStatus = Model.Global.AuditStatus.ClearField.value
            #         oc.DescF = "中控确认清场"
            Desc = "中控确认清场"
            Type = Model.Global.TypeZY.AgainControl.value
            PlanCreate = ctrlPlan('PlanCreate')
            wReturn = PlanCreate.createWorkFlowEventZYPlan(ID, userName, Desc, Type)
            if (wReturn == False):
                return '添加工作流表报错'
            return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "中控确认清场报错Error：" + str(e), current_user.Name)

# 中控再次复核
@app.route('/ZYPlanGuid/controlConfirmReCheckAgain', methods=['POST', 'GET'])
def controlConfirmReCheckAgain():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
            for key in jsonnumber:
                try:
                    ID = int(key)
                    userN = db_session.query(WorkFlowEventZYPlan.userName).filter(
                        WorkFlowEventZYPlan.ZYPlanID == ID).order_by(desc("EventTime")).first()
                    if (userN[0] == current_user.Name):
                        return "中控确认清场与中控清场复核不能是同一人操作！"
                    roclass = db_session.query(ReadyWork).filter(ReadyWork.ZYPlanID == ID, ReadyWork.ProductionFlag == "1").all()
                    for ro in roclass:
                        if (ro.IsCheck == "0"):
                            return "还有准备工作未确认，请确认再提交！"
                        else:
                            pass
                    zypla = db_session.query(ZYPlan).filter(ZYPlan.ID == ID).first()
                    zypla.ZYPlanStatus = Model.Global.ZYPlanStatus.AgainControlChecked.value
                    db_session.commit()
                    # zyplans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == zypla.BatchID).all()
                    # flag = "TRUE"
                    # for zy in zyplans:
                    #     if (zy.ZYPlanStatus != Model.Global.ZYPlanStatus.ControlChecked.value):
                    #         flag = "FALSE"
                    # oclass = db_session.query(PlanManager).filter(PlanManager.BatchID == zypla.BatchID).first()
                    userName = current_user.Name
                    # if (flag == "TRUE"):
                    #     oclassW = db_session.query(WorkFlowStatus).filter_by(PlanManageID=oclass.ID).all()
                    #     for oc in oclassW:
                    #         oclassW.AuditStatus = Model.Global.AuditStatus.Recheck.value
                    #         oclassW.DescF = "中控清场复核"
                    Desc = "中控清场复核"
                    Type = Model.Global.TypeZY.AgainControlChecked.value
                    PlanCreate = ctrlPlan('PlanCreate')
                    wReturn = PlanCreate.createWorkFlowEventZYPlan(ID, userName, Desc, Type)
                    if (wReturn == False):
                        return '添加工作流表报错'
                    return 'OK'
                except Exception as e:
                    db_session.rollback()
                    logger.error(e)
                    insertSyslog("error", "中控清场复核报错Error：" + str(e), current_user.Name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "中控清场复核报错Error：" + str(e), current_user.Name)

# QA再次复核
@app.route('/ZYPlanGuid/QAConfirmAgain', methods=['POST', 'GET'])
def QAConfirmAgain():
    if request.method == 'POST':
        data = request.values
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(ZYPlan).filter(ZYPlan.ID == id).first()
                        oclass.ZYPlanStatus = Model.Global.ZYPlanStatus.AgainQAChecked.value
                        zyplans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == oclass.BatchID).all()
                        flag = "TRUE"
                        for zy in zyplans:
                            if (zy.ZYPlanStatus != Model.Global.ZYPlanStatus.AgainQAChecked.value):
                                flag = "FALSE"
                        userName = current_user.Name
                        if (flag == "TRUE"):
                            oclassPlanManager = db_session.query(PlanManager).filter(PlanManager.BatchID == oclass.BatchID).first()
                            oclassPlanManager.PlanStatus = Model.Global.PlanStatus.AgainQAChecked.value
                            oclassW = db_session.query(WorkFlowStatus).filter_by(PlanManageID=oclass.ID).all()
                            for oc in oclassW:
                                oclassW.AuditStatus = Model.Global.AuditStatus.Recheck.value
                                oclassW.DescF = "QA清场复核"
                        db_session.commit()
                        Desc = "QA清场复核"
                        Type = Model.Global.TypeZY.AgainQAChecked.value
                        PlanCreate = ctrlPlan('PlanCreate')
                        wReturn = PlanCreate.createWorkFlowEventZYPlan(id, userName, Desc, Type)
                        if(wReturn == False):
                            return 'NO'
                        return 'OK'
                    except Exception as e:
                        db_session.rollback()
                        print(e)
                        logger.error(e)
                        insertSyslog("error", "QA清场复核报错Error：" + str(e), current_user.Name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "QA清场复核报错Error：" + str(e), current_user.Name)

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
                    total = db_session.query(PlanManager.ID).filter(PlanManager.PlanStatus == Model.Global.PlanStatus.AgainQAChecked.value).count()
                    PlanManagers = db_session.query(PlanManager).filter(PlanManager.PlanStatus == Model.Global.PlanStatus.AgainQAChecked.value).order_by(
                        desc("EnterTime")).all()[inipage:endpage]
                else:
                    total = db_session.query(PlanManager.ID).filter(PlanManager.BatchID == ABatchID,
                                                               PlanManager.PlanStatus == Model.Global.PlanStatus.AgainQAChecked.value).count()
                    PlanManagers = db_session.query(PlanManager).filter(ZYPlan.BatchID == ABatchID,
                                                              PlanManager.PlanStatus == Model.Global.PlanStatus.AgainQAChecked.value).order_by(
                        desc("EnterTime")).all()[inipage:endpage]
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
                        oclass = db_session.query(PlanManager).filter(PlanManager.ID == id).first()
                        oclassZYPlans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == oclass.BatchID).all()
                        for plan in oclassZYPlans:
                            if(plan.ZYPlanStatus != Model.Global.ZYPlanStatus.AgainQAChecked.value):
                                return "请先确认此批次下的计划都已QA清场复核，QA清场复核后再进行放行！"
                            else:
                                pass
                        oclass.PlanStatus = Model.Global.PlanStatus.QApass.value
                        oclassW = db_session.query(WorkFlowStatus).filter(WorkFlowStatus.PlanManageID == id).all()
                        for oc in oclassW:
                            oc.AuditStatus = Model.Global.AuditStatus.BatchEndPass.value
                            oc.DescF = "QA放行"
                        db_session.commit()
                        userName = current_user.Name
                        Desc = "QA放行"
                        Type = Model.Global.Type.QApass.value
                        PlanCreate = ctrlPlan('PlanCreate')
                        wReturn = PlanCreate.createWorkFlowEventPlan(id, userName, Desc, Type)
                        if(wReturn == False):
                            return 'NO'
                        return 'OK'
                    except Exception as e:
                        db_session.rollback()
                        print(e)
                        logger.error(e)
                        insertSyslog("error", "QA复核报错Error：" + str(e), current_user.Name)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "QA复核报错Error：" + str(e), current_user.Name)

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
    if request.method == 'GET':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                jsonstr = json.dumps(data.to_dict())
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                ID = int(jsonnumber[0])
                plan = db_session.query(PlanManager).filter(PlanManager.ID == ID).first()
                zyplans = db_session.query(ZYPlan).filter(ZYPlan.BatchID == plan.BatchID).all()
                for zy in zyplans:
                    zy.ZYPlanStatus = ""
                jsonzyplans = json.dumps(zyplans, cls=AlchemyEncoder, ensure_ascii=False)
                jsonzyplans = '{"total"' + ":" + str() + ',"rows"' + ":\n" + jsonzyplans + "}"
                return jsonzyplans
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "计划执行进度查询计划明细Error：" + str(e), current_user.Name)
            return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

# 计划管理
@app.route('/ZYPlanManage')
def zYPlanManage(): # 1           2           3               4            5            6          7
    # rights = ['制药计划向导','生产计划审核','生产计划下发', '中控计划确认', '中控计划复核', '任务确认', 'QA计划确认']
    # rolename = db_session.query(User.RoleName).filter_by(Name=current_user.Name).first()
    # role_id = db_session.query(Role.ID).filter_by(RoleName=rolename).first()
    # notVip = []
    # for right in rights:
    #     menu_id = db_session.query(Menu.ID).filter_by(ModuleName=right).first()[0]
    #     # db_session.query(Menu).join(Role_Menu, isouter=True).filter_by(Role_ID=id).all()
    #     menu = db_session.query(Menu).join(Role_Menu, isouter=True).filter(and_(Role_Menu.Role_ID==role_id, Role_Menu.Menu_ID==menu_id)).first()
    #     if menu:
    #         continue
    #     notVip.append(rights.index(right)+1)
    return render_template('ZYPlanManage.html')

# QA放行
@app.route('/QAauthPass')
def QApass():
    return render_template('QAPassAuth.html')


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
            file = request.files.get('note')
            if file is None or file == '':
                return
            file.save(os.path.join(os.getcwd(), file.filename))
            new_file = '%s%s%s'%(os.getcwd(), "\\", file.filename)
            data = getExcel(new_file) # [['i=1100', '温度'], ['i=1112', '气压'], ['i=1123', '湿度']]
            for index in data:
                if index[1].lower() == 'note': #去表头
                    continue
                elements = ('ns=1;s=t|', 'ns=1;s=h|')
                for element in elements:  #将注释Note插入OpcTag中
                    nodeId = element + index[0]
                    opcTag = db_session.query(OpcTag.NodeID).filter_by(NodeID=nodeId).first()
                    if opcTag is None:
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


if __name__ == '__main__':
    app.run(debug=True)