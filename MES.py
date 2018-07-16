import datetime
import decimal
import json
import re
import string
import time
from collections import Counter
from flask import Flask, jsonify, redirect, url_for
from flask import render_template, request
from sqlalchemy import create_engine, Column, ForeignKey, Table, DateTime, Integer, String, and_, or_
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import Model.Global
from Model.BSFramwork import AlchemyEncoder
from Model.core import Enterprise, Area, Factory, ProductLine, ProcessUnit, Equipment
from Model.system import Role, Organization,User,Menu, User_Role
from tools.MESLogger import MESLogger
from Model.core import SysLog
from sqlalchemy import create_engine, Column, ForeignKey, Table, DateTime, Integer, String
from sqlalchemy import func
from sqlalchemy.ext.declarative import DeclarativeMeta
import string
import re
from collections import Counter
from Model.account import login_security
from flask import session as cli_session
from Model.system import User

# from flask_cache import Cache
#
# # redis配置
# cache = Cache()
# config = {
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_HPST': 'localhost',
#     'CAHCE_REDIS_DB': '',
#     'CACHE_REDIS_PASSWORD': ''
# }
# 获取本文件名实例化一个flask对象
app = Flask(__name__)
# app.config['SECRET_KEY'] = 'AHAHAAHAHAHA'


engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
session = Session()

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'Get':
        return render_template('login.html')

    if request.method == 'POST':
        job_number = request.form['job_number']
        password = request.form['password']
        security_status = request.form['security_status']  # 获取ajax传的验证码状态码

        # 判断验证码是否正确
        result = login_security.security(security_status)
        if result['status'] is False:
            return json.dumps({'status': False})

        # 验证账户与密码
        result = login_security.login_handler(job_number, password)
        if result['status'] is True:
            cli_session['username'] = User.job_number
            return render_template('main.html')
        return json.dumps({'status': 400, 'msg': result['msg']})


# 退出
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    cli_session.pop('job_number', None)
    return render_template('login.html')


'''注册'''


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        render_template('register.html')

    if request.method == 'POST':
        user_name = request.form['user_name']
        job_number = request.form['job_number']
        password1 = request.form['password1']
        password2 = request.form['password2']
        email = request.form['email']
        tel = request.form['tel']
        security_status = request.form['security_status']  # 获取ajax传的验证码状态码

        # 判断验证码是否正确
        result = login_security.security(security_status)
        if result['status'] is False:
            return json.dumps({'status': False})

        # 用户注册
        result = login_security.register_handler(user_name, job_number, password1, password2, email, tel)
        if result['status'] is True:
            return render_template('login.html')
        return render_template('register.html', message=result['msg'])


# 系统日志
@app.route('/syslogs')
def syslogs():
    return render_template('syslogs.html')


@app.route('/syslogs/findByDate')
def syslogsFindByDate():
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
                startTime = data['startTime']  # 开始时间
                endTime = data['endTime']  # 结束时间
                # startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                # endTime = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")


                if startTime == "" and endTime == "":
                    total = session.query(SysLog).count()
                    syslogs = session.query(SysLog).all()[inipage:endpage]
                elif startTime != "" and endTime == "":
                    nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    total = session.query(SysLog).filter(SysLog.OperationDate.between(startTime, nowTime)).count()
                    syslogs = session.query(SysLog).filter(SysLog.OperationDate.between(startTime, nowTime))[
                              inipage:endpage]
                else:
                    total = session.query(SysLog).filter(SysLog.OperationDate.between(startTime, endTime)).count()
                    syslogs = session.query(SysLog).filter(SysLog.OperationDate.between(startTime, endTime))[
                              inipage:endpage]
                    # sql = 'select *  from SysLog where Syslog.OperationDate BETWEEN '+"'"+ startTime +"'"+ ' AND '+"'" + endTime +"'"

                # ORM模型转换json格式
                jsonsyslogs = json.dumps(syslogs, cls=AlchemyEncoder, ensure_ascii=False)
                jsonsyslogs = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonsyslogs + "}"

                return jsonsyslogs
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 用户管理
@app.route('/userManager')
def userManager():
    departments = session.query(Organization.ID, Organization.OrganizationName).all()
    print(departments)
    # departments = json.dumps(departments, cls=AlchemyEncoder, ensure_ascii=False)
    data = []
    for tu in departments:
        li = list(tu)
        id = li[0]
        name = li[1]
        department = {'ID':id,'OrganizationName':name}
        data.append(department)
    return render_template('userManager.html',departments=data)


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
                ID = odata['id']
                Name = odata['Name']
                if ID != '':
                    OrganizationCodeData = session.query(Organization).filter_by(ID=ID).first()
                    if OrganizationCodeData != None:
                        OrganizationName = str(OrganizationCodeData.OrganizationName)
                        total = session.query(User).filter(and_(User.OrganizationName.like("%" + OrganizationName + "%") if OrganizationName is not None else "",
                                                           User.Name.like("%" + Name + "%") if Name is not None else "")).count()
                        oclass = session.query(User).filter(and_(User.OrganizationName.like("%" + OrganizationName + "%") if OrganizationName is not None else "",
                                                           User.Name.like("%" + Name + "%") if Name is not None else ""))[inipage:endpage]
                    else:
                        total = session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").count()
                        oclass = session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "")[inipage:endpage]
                else:
                    total = session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").count()
                    oclass = session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "")[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
            return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# @app.route('/queryUserByName')#通过用户名Name进行全表查询
# def queryUserByName():
#     if request.method == 'GET':
#         data = request.values  # 返回请求中的参数和form
#         try:
#             json_str = json.dumps(data.to_dict())
#             print(json_str)
#             if len(json_str) > 10:
#                 pages = int(data['page'])  # 页数
#                 rowsnumber = int(data['rows'])  # 行数
#                 inipage = (pages - 1) * rowsnumber + 0  # 起始页
#                 endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
#                 Name = data['Name']
#                 if Name == '':
#                     total = session.query(User).count()
#                     oclass = session.query(User).all()[inipage:endpage]
#                 else:
#                     total = session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "").count()
#                     oclass = session.query(User).filter(User.Name.like("%" + Name + "%") if Name is not None else "")[inipage:endpage]
#                 # ORM模型转换json格式
#                 jsonuser = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
#                 jsonjsonusers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonuser + "}"
#                 return jsonjsonusers
#         except Exception as e:
#             print(e)
#             logger.error(e)
#             return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/user/addUser', methods=['POST', 'GET'])
def addUser():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                session.add(
                    User(Name=data['Name'],
                         Password=data['Password'], LoginName=data['LoginName'],
                         Status="1", #登录状态先设置一个默认值1：已登录，0：未登录
                         Creater=data['Creater'],
                         CreateTime=data['CreateTime'],
                         LastLoginTime=datetime.datetime.now(),
                         IsLock='false',#data['IsLock'],
                         OrganizationName=data['OrganizationName']))
                session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/user/updateUser', methods=['POST', 'GET'])
def UpdateUser():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                ID = int(data['ID'])
                user = session.query(User).filter_by(ID=ID).first()
                user.Name = data['Name']
                user.Password = data['Password']
                user.LoginName = data['LoginName']
                # user.Status = data['Status']
                user.Creater = data['Creater']
                # user.CreateTime = data['CreateTime']
                # user.LastLoginTime = data['LastLoginTime']
                # user.IsLock = data['IsLock']
                user.OrganizationName = data['OrganizationName']
                session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
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
                    ID = int(key)
                    try:
                        organization = session.query(User).filter_by(ID=ID).delete()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 权限分配
@app.route('/roleright')
def roleright():
    return render_template('roleRight.html')

# 角色列表树形图
def getRoleList(id=0):
    sz = []
    try:
        roles = session.query(Role).filter().all()
        for obj in roles:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "text": obj.RoleName, "children": getRoleList(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'
        # data = string(sz)
        # data.replace(srep, '')

        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 权限分配下的角色列表
@app.route('/Permission/SelectRoles')
def SelectRoles():
    if request.method == 'GET':
        try:
            # data = load()
            data = getRoleList(id=0)
            # organizations = session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 权限分配下的用户列表
@app.route('/permission/userlist')
def userList():
    # 获取用户列表
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        # 默认返回所有用户
        first_ID = data['id']
        if first_ID == '':
            try:
                json_str = json.dumps(data.to_dict())
                print(json_str)
                if len(json_str) > 10:
                    pages = int(data['page'])  # 页数
                    rowsnumber = int(data['rows'])  # 行数
                    inipage = (pages - 1) * rowsnumber + 0  # 起始页
                    endpage = (pages - 1) * rowsnumber + rowsnumber  # 截止页
                    total = session.query(User).count()
                    users_data = session.query(User)[inipage:endpage]
                    # ORM模型转换json格式
                    jsonusers = json.dumps(users_data, cls=AlchemyEncoder, ensure_ascii=False)
                    jsonusers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonusers + "}"
                    return jsonusers.encode("utf8")
            except Exception as e:
                print(e)
                logger.error(e)
                return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 通过点击角色查询用户
@app.route('/permission/RoleFindUser')
def roleFindUser():
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
                # 通过角色ID获取当前角色对应的用户
                role_id = data['id']
                role = session.query(Role).filter_by(ID=role_id).first()
                print(role)
                if role is None:  # 判断当前角色是否存在
                    return
                total = session.query(User).join(User_Role, isouter=True).filter_by(Role_ID=role_id).count()
                users_data = session.query(User).join(User_Role, isouter=True).filter_by(Role_ID=role_id).all()[inipage:endpage]
                print(users_data)
                # ORM模型转换json格式
                jsonusers = json.dumps(users_data, cls=AlchemyEncoder, ensure_ascii=False)
                jsonusers = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonusers + "}"
                return jsonusers
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 权限分配下的功能模块列表
def getMenuList(id=0):
    sz = []
    try:
        menus = session.query(Menu).filter().all()
        for obj in menus:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "text": obj.ModuleName, "children": getMenuList(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'
        # data = string(sz)
        # data.replace(srep, '')

        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
# 加载菜单列表
@app.route('/permission/menulist')
def menulist():
    if request.method == 'GET':
        try:
            data = getMenuList(id=0)
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
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
            menu_id = data['menu_id'] # 获取菜单ID
            if menu_id:
                menu_id = re.findall(r'\d+\.?\d*', menu_id)
            if menu_id is None:
                return
            for r in menu_id:
                role = session.query(Role).filter_by(ID=role_id).first()
                menu = session.query(Menu).filter_by(ID=r).first()
                # 将菜单ID和角色ID存入User_Role
                menu.roles.append(role)
                session.add(menu)
                session.commit()
            # 存入数据库后跳转到权限分配页面
            return redirect(url_for("roleright"))
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载工作台
# 左右滑动添加
@app.route('/batchmanager')  # 批次管理
def batchmanager():
    return render_template('batch_manager.html')


# 加载工作台
@app.route('/organizationMap')
def organizationMap():
    return render_template('index_organization.html')


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
            print(json_str)
            if len(json_str) > 10:
                pages = int(data['page']) # 页数
                rowsnumber = int(data['rows'])  # 行数
                inipage = (pages - 1) * rowsnumber + 0  # 起始页
                endpage = (pages-1) * rowsnumber + rowsnumber #截止页
                total = session.query(func.count(Organization.ID)).scalar()
                organiztions = session.query(Organization).all()[inipage:endpage]
                #ORM模型转换json格式
                jsonorganzitions = json.dumps(organiztions, cls=AlchemyEncoder, ensure_ascii=False)
                jsonorganzitions = '{"total"'+":"+str(total)+',"rows"' +":\n" + jsonorganzitions + "}"
                return jsonorganzitions
        except Exception as e:
            print(e)
            logger.error(e)
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
                organization = session.query(Organization).filter_by(ID=organizationid).first()
                organization.OrganizationCode = data['OrganizationCode']
                organization.OrganizationName = data['OrganizationName']
                organization.ParentCode = data['ParentNode']
                organization.OrganizationSeq = data['OrganizationSeq']
                organization.Description = data['Description']
                organization.CreatePerson = data['CreatePerson']
                organization.CreateDate = data['CreateDate']
                organization.Img = data['Img']
                organization.Color = data['Color']
                session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
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
                        organization = session.query(Organization).filter_by(ID=Organizationid).delete()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder,
                                          ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder,
                                  ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
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
                session.add(
                    Organization(OrganizationCode=data['OrganizationCode'], OrganizationName=data['OrganizationName'],ParentNode=data['ParentNode'], OrganizationSeq=data['OrganizationSeq'],
                                     Description=data['Description'], CreatePerson=data['CreatePerson'],
                                     CreateDate=datetime.datetime.now(),Img = DspImg,Color = DspColor))
                session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allOrganizations/Search', methods=['POST', 'GET'])
def allOrganizationsSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                strconditon = "%" + data['condition'] + "%"
                organizations = session.query(Organization).filter(Organization.OrganizationName.like(strconditon)).all()
                total = Counter(organizations)
                jsonorganizations = json.dumps(organizations, cls=AlchemyEncoder, ensure_ascii=False)
                jsonorganizations = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonorganizations + "}"
                return jsonorganizations
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)

# 生产建模
# 加载工作台
@app.route('/Enterprise')
def Enterprise():
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
# 权限分配下的功能模块列表
def getOrganizationList(id=0):
    sz = []
    try:
        organizations = session.query(Organization).filter().all()
        for obj in organizations:
            if obj.ParentNode == id:
                sz.append({"id": obj.ID, "text": obj.ModuleName, "children": getOrganizationList(obj.ID)})
        srep = ',' + 'items' + ':' + '[]'
        # data = string(sz)
        # data.replace(srep, '')

        return sz
    except Exception as e:
        print(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)
# 加载菜单列表
@app.route('/Enterprize/parentNode')
def parentNode():
    if request.method == 'GET':
        try:
            data = getOrganizationList(id=0)
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
            return jsondata.encode("utf8")
        except Exception as e:
            print(e)
            logger.error(e)
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
def Factory():
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
        print(re)
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


# 加载工作台
@app.route('/ProductLine')
def ProductLine():
    return render_template('sysProductLine.html')


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
def ProcessUnit():
    return render_template('sysProcessUnit.html')


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


# 加载工作台
@app.route('/Equipment')
def Equipment():
    return render_template('sysEquipment.html')


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
def ProductRule():
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
def ZYPlan():
    return render_template('sysZYPlan.html')


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
def ZYTask():
    return render_template('sysZYTask.html')


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
def ProductControlTask():
    return render_template('sysProductControlTask.html')


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
def ProductParameter():
    return render_template('sysProductParameter.html')


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
def MaterialType():
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
def Material():
    return render_template('sysMaterial.html')


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
        re = MaterialBOMIFS.MaterialPlanBOMsFind(data)
        print(re)
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
def MaterialBOM():
    return render_template('sysMaterialBOM.html')


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
def ZYPlanMaterial():
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
def ProductUnit():
    return render_template('sysProductUnit.html')


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
def ProductUnitRoute():
    return render_template('sysProductUnitRoute.html')


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
def SchedulePlan():
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
@app.route('/PlanManager')
def PlanManager():
    return render_template('sysPlanManager.html')


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
def Unit():
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
        orgs = session.query(Organization).filter().all()
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
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/Organization/Find')
def OrganizationFind():
    if request.method == 'GET':
        try:
            # data = load()
            data = getOrganizationChildren(id=0)
            # organizations = session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 建立会话
# 主页面路由
@app.route('/')
def hello_world():
    return render_template('main.html')


# 加载工作台
@app.route('/workbench')
def workbenck():
    return render_template('workbench.html')


# 工作台菜单role
@app.route('/sysrole')
def sysrole():
    return render_template('sysRole.html')


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
                role = session.query(Role).filter_by(ID=Roleid).first()
                role.RoleCode = data['RoleCode']
                role.RoleName = data['RoleName']
                role.RoleSeq = data['RoleSeq']
                role.Description = data['Description']
                role.CreatePerson = data['CreatePerson']
                role.CreateDate = data['CreateDate']
                session.commit()
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
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
                        role = session.query(Role).filter_by(ID=Roleid).delete()
                    except Exception as ee:
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "error:" + string(ee)}], cls=AlchemyEncoder, ensure_ascii=False)
                return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
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
                session.add(Role(RoleCode = data['RoleCode'],RoleName=data['RoleName'],RoleSeq=data['RoleSeq'],Description=data['Description'],CreatePerson=data['CreatePerson'],CreateDate= datetime.datetime.now()))
                session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
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
            print(json_str)
            if len(json_str) > 10:
                pages = int(data['page'])
                rowsnumber = int(data['rows'])
                inipage = (pages - 1) * rowsnumber + 0
                endpage = (pages - 1) * rowsnumber + rowsnumber
                total = session.query(func.count(Role.ID)).scalar()
                roles = session.query(Role).all()[inipage:endpage]
                # ORM模型转换json格式
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/allroles/Search', methods=['POST', 'GET'])
def allrolesSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                strconditon = "%" + data['condition'] + "%"
                roles = session.query(Role).filter(Role.RoleName.like(strconditon)).all()
                total = Counter(roles)
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载工作台
@app.route('/Myorganization')
def Myorganization():
    return render_template('Myorganization.html')


def getMyOrganizationChildren(id=0):
    sz = []
    try:
        orgs = session.query(Organization).filter().all()
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
        orgs = session.query(Organization).filter().all()
        for obj in orgs:
            sz.append({"id": obj.ID, "text": obj.OrganizationName, "group": obj.ParentNode})
        # data = string(sz)"'"
        # data.replace(srep, '')
        return sz
    except Exception as e:
        print(e)
        logger.error(e)
        return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/MyOp')
def MyOpFind():
    if request.method == 'GET':
        try:
            # data = load()
            data = getMyOrganizationChildren(id=0)
            # organizations = session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


@app.route('/Myenterprise')
def Myenterprise():
    if request.method == 'GET':
        try:
            # data = load()
            data = getMyEnterprise(id=0)
            # organizations = session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
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
                oclass = session.query(Model.system.Organization).filter_by(ID=objid).first()
                jsondata = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


# 加载工作台
@app.route('/createPlanWizard')
def createPlanWizard():
    return render_template('createPlanWizard.html')


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
        objs = session.query(Model.core.ProductRule).filter().all()
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
            # organizations = session.query(Organization).filter().all()
            jsondata = json.dumps(data, cls=AlchemyEncoder, ensure_ascii=False)
            print(jsondata)
            return jsondata
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error：" + str(e)}], cls=AlchemyEncoder, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)




