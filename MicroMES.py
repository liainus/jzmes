from flask import Flask
from flask import render_template,request
from flask import Flask, jsonify
from system.system import *
from system.BSFramwork import *
import json
import sqlalchemy
import time,datetime,decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Column,ForeignKey, Table, DateTime, Integer, String
from sqlalchemy import func
import string
import re
from collections import Counter


app = Flask(__name__)

engine = create_engine("mssql+pymssql://sa:Qcsw@123@127.0.0.1:1433/MES?charset=utf8", deprecate_large_types=True)
Session = sessionmaker(bind=engine)
session = Session()

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data,ensure_ascii=False)     # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:    # 添加了对datetime的处理
                    # print(type(data),data)
                    if isinstance(data, datetime.datetime):
                        # fields[field] = data.strftime("%Y-%m-%d %H:%M:%S.%f")[:-2] #SQLserver数据库中毫秒是3位，日期格式;2015-05-12 11:13:58.543
                        fields[field] = data.strftime("%Y-%m-%d %H:%M:%S")  # SQLserver数据库中毫秒是3位，日期格式;2015-05-12 11:13:58.543
                    elif isinstance(data, datetime.date):
                        fields[field] = data.strftime("%Y-%m-%d")
                    elif isinstance(data, decimal.Decimal):
                        fields[field]= float(data)
                    else:
                        fields[field] = AlchemyEncoder.default(self, data) #如果是自定义类，递归调用解析JSON，这个是对象映射关系表 也加入到JSON
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)
# 建立会话
#主页面路由
@app.route('/')
def hello_world():
    return render_template('main.html')

#加载工作台
@app.route('/workbench')
def workbenck():
    return render_template('workbench.html')

#工作台菜单role
@app.route('/sysrole')
def sysrole():
    return render_template('sysRole.html')

#role更新数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allroles/Update',methods=['POST','GET'])
def allrolesUpdate():
    if request.method == 'POST':
        data = request.values
        str = request.get_json()
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 10:
                Roleid = int(data['ID'] )
                role= session.query(Role).filter_by(ID=Roleid).first()
                role.RoleCode = data['RoleCode']
                role.RoleName =  data['RoleName']
                role.RoleSeq =  data['RoleSeq']
                role.Description =  data['Description']
                role.CreatePerson =  data['CreatePerson']
                role.CreateDate =  data['CreateDate']
                session.commit()
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)

#role删除数据，通过传入的json数据，json数据只包含主键，解析之后进行相应更新
#解析方法：主键为数字，通过正则表达式把数字筛选出来，进行相应操作
@app.route('/allroles/Delete',methods=['POST','GET'])
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
                        return json.dumps([{"status": "error:"+string(ee)}], cls=AlchemyEncoder, ensure_ascii=False)
                return json.dumps([{"status": "OK"}], cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)

#role创建数据，通过传入的json数据，解析之后进行相应更新
@app.route('/allroles/Create',methods=['POST','GET'])
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
            return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)


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
                endpage = (pages-1) * rowsnumber + rowsnumber
                total = session.query(func.count(Role.ID)).scalar()
                roles = session.query(Role).all()[inipage:endpage]
                #ORM模型转换json格式
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"'+":"+str(total)+',"rows"' +":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            return json.dumps([{"status": "Error："+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)

@app.route('/allroles/Search',methods=['POST','GET'])
def allrolesSearch():
    if request.method == 'POST':
        data = request.values
        try:
            json_str = json.dumps(data.to_dict())
            if len(json_str) > 2:
                strconditon = "%"+data['condition']+"%"
                roles = session.query(Role).filter(Role.RoleName.like(strconditon)).all()
                total = Counter(roles)
                jsonroles = json.dumps(roles, cls=AlchemyEncoder, ensure_ascii=False)
                jsonroles = '{"total"'+":"+str(total.__len__())+',"rows"' +":\n" + jsonroles + "}"
                return jsonroles
        except Exception as e:
            print(e)
            return json.dumps([{"status": "Error："+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)

if __name__ == '__main__':
    app.run()




