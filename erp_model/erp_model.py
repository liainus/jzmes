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
    EquipmentTimeStatisticTree, SystemEQPCode, EquipmentManagementManua, EquipmentMaintenanceStandard, product_info, \
    product_plan, product_infoERP, YieldMaintain, plantCalendarScheduling, Scheduling, SchedulingStandard, \
    SchedulingMaterial, StapleProducts
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
                product_type = data.get("product_type")
                product_code = data.get("product_code")
                if product_type == None or product_type =="":
                    total = db_session.query(product_infoERP).filter(product_infoERP.product_code.like("%"+product_code+"%")).count()
                    oclass = db_session.query(product_infoERP).filter(product_infoERP.product_code.like("%"+product_code+"%")).all()[inipage:endpage]
                    jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                else:
                    total = db_session.query(product_infoERP).filter(product_infoERP.product_type == product_type, product_infoERP.product_code.like("%"+product_code+"%")).count()
                    oclass = db_session.query(product_infoERP).filter(product_infoERP.product_type == product_type, product_infoERP.product_code.like("%"+product_code+"%")).all()[inipage:endpage]
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
                oclass = ERP_session.query(product_plan).order_by(desc("plan_period")).all()[inipage:endpage]
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
            # plans = ERP_session.query(product_plan).filter(product_plan.product_code == plan.product_code).all()
            # for pla in plans:
            #     pla.transform_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #     pla.transform_flag = '0'
            # ERP_session.commit()
            count = ERP_session.query(product_plan.bill_code).distinct().filter(product_plan.product_code == plan.product_code, product_plan.transform_flag == '0').count()
            if plan.transform_flag == "1":
                return "此单据号的数据已经同步过，请选择没有同步过的数据！"
            e = product_plan()
            e.plan_period = plan.plan_period
            e.product_code = plan.product_code
            e.product_name = plan.product_name
            e.plan_quantity = str(count)
            e.product_unit = plan.product_unit
            e.meter_type = plan.meter_type
            e.bill_code = plan.bill_code
            e.plan_type = plan.plan_type
            e.create_time = plan.create_time
            e.transform_time = plan.transform_time
            e.transform_flag = plan.transform_flag
            db_session.add(e)
            db_session.commit()
            plans = ERP_session.query(product_plan).filter(product_plan.product_code == plan.product_code, product_plan.transform_flag == '0').all()
            for pla in plans:
                pla.transform_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pla.transform_flag = '1'
            ERP_session.commit()
            PRName = db_session.query(ERPproductcode_prname.PRName).filter(ERPproductcode_prname.product_code == plan.product_code).first()[0]
            ProductRuleID = db_session.query(ProductRule.ID).filter(ProductRule.PRName == PRName).first()[0]
            # ss = db_session.query(SchedulingStock).filter(SchedulingStock.product_code == plan.product_code).all()
            # if ss != None:
            #     for s in ss:
            #         db_session.delete(s)
            #     db_session.commit()
            MATIDs = db_session.query(MaterialBOM.MATID).filter(MaterialBOM.ProductRuleID == ProductRuleID).all()
            for MATID in MATIDs:
                MATName = db_session.query(Material.MATName).filter(Material.ID == MATID).first()[0]
                ss = db_session.query(SchedulingStock).filter(SchedulingStock.MATName == MATName, SchedulingStock.product_code == plan.product_code).first()
                if ss == None:
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

@ERP.route('/YieldMaintainUpdateCreate', methods=['POST', 'GET'])
def YieldMaintainUpdateCreate():
    '''
    YieldMaintain的更新添加
    :return:
    '''
    if request.method == 'POST':
        try:
            data = request.values
            PRName = data["PRName"]
            Yield = data["Yield"]
            FinishProduct = data["FinishProduct"]
            SamplingQuantity = data["SamplingQuantity"]
            TotalQuantity = data["TotalQuantity"]
            cp = float(FinishProduct) + float(SamplingQuantity)
            TotalQuantity = str((cp / float(Yield)))
            oclass = db_session.query(YieldMaintain).filter(YieldMaintain.PRName == PRName).first()
            if oclass == None or oclass == '':
                db_session.add(YieldMaintain(PRName=PRName, Yield=Yield, FinishProduct=FinishProduct,
                                             SamplingQuantity=SamplingQuantity, TotalQuantity=TotalQuantity))
            else:
                oclass.Yield = Yield
                oclass.FinishProduct = FinishProduct
                oclass.SamplingQuantity = SamplingQuantity
                oclass.TotalQuantity = TotalQuantity
            db_session.commit()
            return 'OK'
        except Exception as e:
            db_session.rollback()
            print(e)
            logger.error(e)
            insertSyslog("error", "YieldMaintain的更新添加报错：" + str(e), current_user.Name)
            return json.dumps("YieldMaintain的更新添加报错", cls=Model.BSFramwork.AlchemyEncoder,
                              ensure_ascii=False)


@ERP.route('/YieldMaintainSearch', methods=['POST', 'GET'])
def YieldMaintainSearch():
    '''
    YieldMaintain查询
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                PRName = data["PRName"]
                oclass = db_session.query(YieldMaintain).filter(YieldMaintain.PRName == PRName).first()
                dir = {}
                if oclass != None:
                    dir["ID"] = oclass.ID
                    dir["PRName"] = oclass.PRName
                    dir["Yield"] = oclass.Yield
                    dir["FinishProduct"] = oclass.FinishProduct
                    dir["SamplingQuantity"] = oclass.SamplingQuantity
                    dir["TotalQuantity"] = oclass.TotalQuantity
                    return json.dumps(dir, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
                else:
                    return ''
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SchedulingMaterial查询报错Error：" + str(e), current_user.Name)

@ERP.route('/plantCalendarYield')
def plantCalendarYield():
    '''
    :return: 得率页面跳转
    '''
    data = []
    # codenames = {"太子参粉","无糖山药粉","肿节风浸膏","山药粉"}
    codenames = db_session.query(ERPproductcode_prname).filter().all()
    for i in codenames:
        dir = {"id": i.PRName, "text": i.PRName}
        data.append(dir)
    return render_template('plantCalendarYield.html',data = data)

@ERP.route('/plantCalendar')
def plantCalendar():
    '''
    :return: 工厂日历页面跳转
    '''
    data = []
    codenames = db_session.query(ProductRule.PRCode, ProductRule.PRName).all()
    for i in codenames:
        dir = {"id": i[0], "text": i[1]}
        data.append(dir)
    return render_template('plantCalendar.html',data = data)



@ERP.route('/systemManager_model/plantCalendarSchedulingCreate', methods=['GET', 'POST'])
def plantCalendarSchedulingCreate():
    '''
    工厂日历
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        return insert(plantCalendarScheduling, data)


@ERP.route('/systemManager_model/plantCalendarSchedulingUpdate', methods=['GET', 'POST'])
def plantCalendarSchedulingUpdate():
    '''
    工厂日历
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        return update(plantCalendarScheduling, data)


@ERP.route('/systemManager_model/plantCalendarSchedulingDelete', methods=['GET', 'POST'])
def plantCalendarSchedulingDelete():
    '''
    工厂日历
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        return delete(plantCalendarScheduling, data)


@ERP.route('/systemManager_model/plantCalendarSchedulingSelect', methods=['GET', 'POST'])
def plantCalendarSchedulingSelect():
    '''
    工厂日历
    :return:
    '''
    if request.method == 'GET':
        data = request.values
        try:
            re = []
            oclass = db_session.query(Scheduling).all()
            for oc in oclass:
                dir = {}
                dir['ID'] = oc.ID
                dir['start'] = oc.SchedulingTime
                dir['title'] = oc.PRName + ": 第" + oc.SchedulingNum[6:] + "批"
                dir['color'] = "#9FDABF"
                re.append(dir)
            ocl = db_session.query(plantCalendarScheduling).all()
            for o in ocl:
                dic = {}
                dic['ID'] = str(o.ID)
                dic['start'] = str(o.start)
                dic['title'] = o.title.split(":")[0]
                dic['color'] = o.color
                re.append(dic)
            return json.dumps(re, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(e)
            insertSyslog("error", "工厂日历查询报错Error：" + str(e), current_user.Name)
            return json.dumps("工厂日历查询报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@ERP.route('/systemManager_model/planScheduling', methods=['GET', 'POST'])
def planScheduling():
    '''
    计划排产
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        try:
            plan_id = data['plan_id']
            oc = db_session.query(product_plan).filter(product_plan.plan_id == plan_id).first()
            month = data['month']
            count = db_session.query(plantCalendarScheduling).filter(plantCalendarScheduling.start.like("%" + month + "%"),
                ~plantCalendarScheduling.title.like("%安全库存%")).count()
            mou = month.split("-")
            monthRange = calendar.monthrange(int(mou[0]), int(mou[1]))
            monthRangeNext = calendar.monthrange(int(mou[0]), int(mou[1])+1)
            SchedulDates = monthRange[1] - count #排产月份有多少天
            PRName = db_session.query(ERPproductcode_prname.PRName).filter(ERPproductcode_prname.product_code == oc.product_code).first()[0]
            sch = db_session.query(SchedulingStandard).filter(SchedulingStandard.PRName == PRName).first()

            #这批计划要做多少天
            # batchnums = ""
            # if oc.meter_type == "W":
            #     yc = db_session.query(YieldMaintain).filter(YieldMaintain.PRName == PRName).first()
            #     #计划做多少批
            #     batchnums = float(oc.plan_quantity)/float(yc.FinishProduct)
            #     #计划要用到多少原材料
            #     total = float(yc.TotalQuantity)*batchnums
            #     # 计划有多少批
            #     batchnums = total/float(sch.Batch_quantity)
            # elif oc.meter_type == "B":
            #     batchnums = int(oc.plan_quantity)
            batchnums = int(oc.plan_quantity)
            days = batchnums/int(sch.DayBatchNumS) #这批计划要做多少天
            re = timeChange(mou[0], mou[1], monthRange[1])

            #不能排产的时间
            if int(mou[1])<10:
                mou = mou[0]+"-0"+mou[1]
            else:
                mou = mou[0] + "-" + mou[1]
            schdays = db_session.query(plantCalendarScheduling.start).filter(plantCalendarScheduling.start.like("%" + mou + "%"),
                                    ~plantCalendarScheduling.title.like("%安全库存%")).all()
            undays = []
            if schdays != None:
                for i in schdays:
                    undays.append(i[0])

            # 删除上一次排产同品名的数据
            solds = db_session.query(Scheduling).filter(Scheduling.PRName == PRName, Scheduling.SchedulingTime.like("%"+mou+"%")).all()
            for old in solds:
                sql = "DELETE FROM Scheduling WHERE ID = "+str(old.ID)
                db_session.execute(sql)#删除同意品名下的旧的排产计划
            plans = db_session.query(plantCalendarScheduling).filter(plantCalendarScheduling.title.like(PRName), plantCalendarScheduling.start.like("%"+mou+"%")).all()
            for pl in plans:
                sql = sql1 = "DELETE FROM plantCalendarScheduling WHERE ID = " + str(pl.ID)
                db_session.execute(sql)#删除同意品名下的安全库存信息
            db_session.commit()

            # 去掉不能排产的时间，只剩可以排产的时间
            daySchedulings = list(set(re).difference(set(undays)))
            daySchedulings = list(daySchedulings)
            daySchedulings.sort()

            # 排产数据写入数据库
            dayBatchNum = db_session.query(SchedulingStandard.DayBatchNumS).filter(SchedulingStandard.PRName == PRName).first()[0]
            j = 1
            k = 1
            for day in daySchedulings:
                if k > days:#当这个计划所有的批次做完跳出循环
                    break
                for r in range(0, int(dayBatchNum)):
                    s = Scheduling()
                    s.SchedulingTime = day
                    s.PRName = PRName
                    s.BatchNumS = sch.DayBatchNumS
                    if j < 10:
                        s.SchedulingNum = day.replace("-", "")[2:6] + "600" + str(j)
                    else:
                        s.SchedulingNum = day.replace("-", "")[2:6] + "60" + str(j)
                    db_session.add(s)
                    j = j+1
                k = k + 1
            db_session.commit()

            #工厂日历安全库存提醒
            sches = db_session.query(Scheduling).filter(Scheduling.PRName == PRName).order_by(("SchedulingTime")).all()
            stan = db_session.query(SchedulingStandard).filter(SchedulingStandard.PRName == PRName).first()
            stocks = db_session.query(SchedulingStock).filter(SchedulingStock.product_code == oc.product_code).all()
            for st in stocks:
                sto = int(st.StockHouse) - int(st.SafetyStock)#库存-安全库存 库存情况
                mid = db_session.query(Material.ID).filter(Material.MATName == st.MATName).first()[0]
                BatchPercentage = db_session.query(MaterialBOM.BatchPercentage).filter(MaterialBOM.MATID == mid).first()#此物料的百分比
                cals = db_session.query(plantCalendarScheduling).filter(
                    plantCalendarScheduling.title.like("%" + st.MATName + "%")).all()
                if cals != None:
                    for c in cals:
                        db_session.delete(c)
                        db_session.commit()
                #物料N每天做多少公斤
                steverydayKG = (int(stan.DayBatchNumS)*float(stan.Batch_quantity))*float(BatchPercentage[0])
                #库存可以做多少天
                stockdays = sto/steverydayKG
                if "." in str(stockdays):
                    stockdays = int(str(stockdays).split(".")[0])
                for i in range(0,len(sches)):
                    if i == stockdays-1:
                        ca = plantCalendarScheduling()
                        ca.start = sches[i].SchedulingTime
                        ca.title = st.MATName + "已到安全库存" + ":"+ PRName#PRName + "中的物料" +
                        ca.color = "#e67d7d"
                        db_session.add(ca)
                        break
                # # 存库存消耗表
                # sms = db_session.query(SchedulingMaterial).filter(SchedulingMaterial.MaterialName == st.MATName).all()
                # for s in sms:
                #     db_session.delete(s)
                # db_session.commit()
                # for n in range(1,len(daySchedulings)):
                #     schm = SchedulingMaterial()
                #     schm.SchedulingTime = daySchedulings[n-1]
                #     schm.MaterialName = st.MATName
                #     schm.Surplus_quantity = float(st.StockHouse) - float(steverydayKG*n)
                #     db_session.add(schm)
            db_session.commit()
            return 'OK'
        except Exception as e:
            print(e)
            db_session.rollback()
            logger.error(e)
            insertSyslog("error", "计划排产报错Error：" + str(e), current_user.Name)
            return json.dumps("计划排产报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
def timeChange(year,month,days):
    i = 0
    da = []
    while i < days:
        if i < 9:
            i = i + 1
            date = str(year) + "-" + str(mon(month)) + "-" + str(0) + str(i)
            da.append(date)
        else:
            i = i + 1
            date = str(year)  + "-" + str(mon(month))  + "-" +  str(i)
            da.append(date)
    return da
def mon(month):
    if int(month)<10:
        return "0"+month
    else:
        return month
@ERP.route('/systemManager_model/plantSchedulingAddBatch', methods=['GET', 'POST'])
def plantSchedulingAddBatch():
    '''
    计划排产增加批次
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        try:
            PRName = data['title']
            code = db_session.query(ERPproductcode_prname.product_code).filter(ERPproductcode_prname.PRName ==
                                                                               PRName).first()[0]
            plan_id = db_session.query(product_plan.plan_id).filter(product_plan.product_code == code).order_by(
                desc("plan_id")).first()
            if plan_id != None:
                plan_id = plan_id[0]
            else:
                return "请先同步ERP计划！"
            date = data['start']
            #添加排产数据
            sch = db_session.query(Scheduling).filter(Scheduling.PRName == PRName).order_by(desc("SchedulingNum")).first()
            if sch == None:
                return "请先进行排产！"
            count = db_session.query(Scheduling).filter(Scheduling.SchedulingTime == sch.SchedulingTime).count()
            SchedulingTime = sch.SchedulingTime
            if int(sch.BatchNumS) == count or sch.BatchNumS == "1":
                spls = str(sch.SchedulingTime)[8:10]
                spls = str(int(spls) + 1)
                SchedulingTime = str(sch.SchedulingTime)[0:8] + spls
                ishas = db_session.query(plantCalendarScheduling).filter(plantCalendarScheduling.start == SchedulingTime).first()
                while ishas != None:
                    i = 1
                    spls = str(int(spls) + i)
                    SchedulingTime = str(sch.SchedulingTime)[0:8] + spls
                    ishas = db_session.query(plantCalendarScheduling).filter(plantCalendarScheduling.start == SchedulingTime).first()
                    i = i + 1
            sc = Scheduling()
            sc.PRName = sch.PRName
            sc.SchedulingStatus = Model.Global.SchedulingStatus.Unlock.value
            sc.SchedulingTime = SchedulingTime
            sc.BatchNumS = sch.BatchNumS
            sc.SchedulingNum = str(int(sch.SchedulingNum) + 1)
            sc.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_session.add(sc)
            db_session.commit()
            return 'OK'
        except Exception as e:
            logger.error(e)
            insertSyslog("error", "计划排产增加批次报错Error：" + str(e), current_user.Name)
            return json.dumps("计划排产增加批次报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

@ERP.route('/planSchedulingTu', methods=['GET', 'POST'])
def planSchedulingTu():
    '''
    计划排产库存与安全库存柱状图
    :return:
    '''
    if request.method == 'GET':
        data = request.values
        try:
            dir = []
            PRName = data['PRName']
            product_code = db_session.query(ERPproductcode_prname.product_code).filter(ERPproductcode_prname.PRName
                                                                                       == PRName).first()[0]
            MATNames = db_session.query(Material.MATName).join(MaterialBOM, MaterialBOM.MATID == Material.ID).join(
                ProductRule, ProductRule.ID == MaterialBOM.ProductRuleID).filter(ProductRule.PRName == PRName).all()
            for na in MATNames:
                dir.append(yselect(na[0], product_code))
            return json.dumps(dir, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            logger.error(e)
            insertSyslog("error", "计划排产柱状图报错Error：" + str(e), current_user.Name)
            return json.dumps("计划排产柱状图报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
def yselect(name, product_code):
    '''
    配置每个物料名下的柱状图
    :param name:
    :param product_code:
    :return:
    '''
    yc = {}
    y = db_session.query(SchedulingStock).filter(SchedulingStock.MATName == name, SchedulingStock.product_code == product_code).first()
    if y == None:
        yc["ID"] = "y"
        yc["name"] = name
        yc["total"] = ""
        yc["safe"] = ""
    else:
        yc["ID"] = "y" + str(y.ID)
        yc["name"] = name
        yc["total"] = y.StockHouse
        yc["safe"] = y.SafetyStock
    return yc

@ERP.route('/SchedulingStockUpdateCreate', methods=['POST', 'GET'])
def SchedulingStockUpdateCreate():
    '''
    SchedulingStock的更新添加
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        ID = data["ID"]
        if(ID == "" or ID == None):
            return "请先同步ERP计划信息再进行设置！"
        else:
            StockHouse = data["StockHouse"]
            SafetyStock = data["SafetyStock"]
            if StockHouse != None and StockHouse != '':
                ss = db_session.query(SchedulingStock).filter(SchedulingStock.ID == ID).first()
                ssms = db_session.query(SchedulingStock).filter(SchedulingStock.MATName == ss.MATName).all()
                for i in ssms:
                    i.StockHouse = StockHouse
                db_session.commit()
                return 'OK'
            elif SafetyStock != None and SafetyStock != '':
                ss = db_session.query(SchedulingStock).filter(SchedulingStock.ID == ID).first()
                ss.SafetyStock = SafetyStock
                db_session.commit()
                return 'OK'

# 设置安全库存
@ERP.route('/plantCalendarSafeStock')
def plantCalendarSafeStock():
    data = []
    codenames = db_session.query(ProductRule.PRCode, ProductRule.PRName).all()
    for i in codenames:
        dir = {"id":i[0],"text":i[1]}
        data.append(dir)
    return render_template('plantCalendarSafeStock.html', data=data)

# 设置每日批数
@ERP.route('/plantCalendarbatchNumber')
def plantCalendarbatchNumber():
    data = []
    codenames = db_session.query(ProductRule.PRCode, ProductRule.PRName).all()
    for i in codenames:
        dir = {"id": i[0], "text": i[1]}
        data.append(dir)
    return render_template('plantCalendarbatchNumber.html', data=data)

# 日历排产
@ERP.route('/calendarScheduling')
def calendarScheduling():
    return render_template('plantCalendarScheduling.html')

@ERP.route('/SchedulingStandardCreate', methods=['POST', 'GET'])
def SchedulingStandardCreate():
    '''
    SchedulingStandardCreate添加
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        try:
            PRName = data['PRName']
            oclass = db_session.query(SchedulingStandard).filter(SchedulingStandard.PRName == PRName).first()
            if oclass != None:
                db_session.delete(oclass)
                db_session.commit()
            return insert(SchedulingStandard,data)
        except Exception as e:
            db_session.rollback()
            logger.error(e)
            insertSyslog("error", "SchedulingStandardCreate添加报错Error：" + str(e), current_user.Name)
            return json.dumps("SchedulingStandardCreate添加报错", cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
@ERP.route('/SchedulingStandardUpdate', methods=['POST', 'GET'])
def SchedulingStandardUpdate():
    '''
    修改
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        return update(SchedulingStandard, data)
@ERP.route('/SchedulingStandardDelete', methods=['POST', 'GET'])
def SchedulingStandardDelete():
    '''
    删除
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        return update(SchedulingStandard, data)
@ERP.route('/SchedulingStandardSearch', methods=['POST', 'GET'])
def SchedulingStandardSearch():
    '''
    SchedulingStandard查询
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                offset = int(data['offset'])  # 页数
                limit = int(data['limit'])  # 行数
                total = db_session.query(SchedulingStandard).count()
                oclass = db_session.query(SchedulingStandard).all()[offset:limit]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                return '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SchedulingStandard查询报错Error：" + str(e), current_user.Name)

@ERP.route('/SchedulingSearchNew', methods=['POST', 'GET'])
def SchedulingSearchNew():
    '''
    Scheduling查询
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
                SchedulingTime = data["SchedulingTime"]
                if (SchedulingTime == ""):
                    total = db_session.query(Scheduling).count()
                    oclass = db_session.query(Scheduling).order_by("SchedulingTime").all()[inipage:endpage]
                else:
                    total = db_session.query(Scheduling).filter(Scheduling.SchedulingTime == SchedulingTime).count()
                    oclass = db_session.query(Scheduling).filter(Scheduling.SchedulingTime == SchedulingTime).order_by("SchedulingTime").all()[inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonoclass = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonoclass
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Scheduling查询报错Error：" + str(e), current_user.Name)

@ERP.route('/SchedulingSearch', methods=['POST', 'GET'])
def SchedulingSearch():
    '''
    Scheduling查询
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                re = []
                oclass = db_session.query(Scheduling).all()
                for oc in oclass:
                    dir = {}
                    dir['start'] = str(oc.SchedulingTime)[0:-9]
                    dir['title'] = oc.PRName +":"+ oc.BatchNumS+"批"
                    re.append(dir)
                return json.dumps(re, cls=AlchemyEncoder, ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "Scheduling查询报错Error：" + str(e), current_user.Name)
# 排产结果
@ERP.route('/plantCalendarResult')
def plantCalendarResult():
    return render_template('plantCalendarResult.html')

@ERP.route('/SchedulingUpdate', methods=['POST', 'GET'])
def SchedulingUpdate():
    '''
    修改
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        return update(Scheduling, data)
@ERP.route('/SchedulingDelete', methods=['POST', 'GET'])
def SchedulingDelete():
    '''
    删除
    :return:
    '''
    if request.method == 'POST':
        data = request.values
        return delete(Scheduling, data)

@ERP.route('/SchedulingMaterialSearch', methods=['POST', 'GET'])
def SchedulingMaterialSearch():
    '''
    SchedulingMaterial查询
    :return:
    '''
    if request.method == 'POST':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                SchedulingTime = data["SchedulingTime"]
                oclass = db_session.query(SchedulingMaterial).filter(SchedulingMaterial.SchedulingTime == SchedulingTime).all()
                str = ""
                for oc in oclass:
                    str = str + "<p>" + oc.MaterialName + "剩余物料：" + oc.Surplus_quantity + "kg</p>"
                return str
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "SchedulingMaterial查询报错Error：" + str(e), current_user.Name)

@ERP.route('/erp_model/StapleProductsSearch', methods=['POST', 'GET'])
def StapleProductsSearch():
    '''
    原料单检验查询
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
                IsRelevance = data.get("IsRelevance")
                BillNo = data.get("BillNo")
                total = db_session.query(StapleProducts).filter(StapleProducts.IsRelevance == IsRelevance, StapleProducts.BillNo == BillNo).count()
                oclass = db_session.query(StapleProducts).filter(StapleProducts.IsRelevance == IsRelevance, StapleProducts.BillNo == BillNo).all()[
                         inipage:endpage]
                jsonoclass = json.dumps(oclass, cls=AlchemyEncoder, ensure_ascii=False)
                jsonpequipments = '{"total"' + ":" + str(total) + ',"rows"' + ":\n" + jsonoclass + "}"
                return jsonpequipments
        except Exception as e:
            print(e)
            logger.error(e)
            insertSyslog("error", "原料单检验查询查询报错Error：" + str(e), current_user.Name)

@ERP.route('/StapleProductsChecked', methods=['POST', 'GET'])
def StapleProductsChecked():
    '''
    原料复核
    :return:
    '''
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
                        oclass = db_session.query(StapleProducts).filter_by(ID=id).first()
                        oclass.CheckedPeople = current_user.Name
                        oclass.CheckedStatus = ""
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

@ERP.route('/StapleProductsUpdate', methods=['POST', 'GET'])
def StapleProductsUpdate():
    '''
    WMS原料单关联SAP采购单
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                BillNo = data.get("BillNo")
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(StapleProducts).filter_by(ID=id).first()
                        oclass.BillNo = BillNo
                        oclass.IsRelevance = "1"
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
            insertSyslog("error", "WMS原料单关联SAP采购单报错Error：" + str(e), current_user.Name)

@ERP.route('/cancelStapleProductsUpdate', methods=['POST', 'GET'])
def cancelStapleProductsUpdate():
    '''
    WMS原料单取消关联SAP采购单
    :return:
    '''
    if request.method == 'GET':
        data = request.values  # 返回请求中的参数和form
        try:
            jsonstr = json.dumps(data.to_dict())
            if len(jsonstr) > 10:
                jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
                for key in jsonnumber:
                    id = int(key)
                    try:
                        oclass = db_session.query(StapleProducts).filter_by(ID=id).first()
                        oclass.BillNo = ""
                        oclass.IsRelevance = "0"
                        db_session.commit()
                    except Exception as ee:
                        db_session.rollback()
                        print(ee)
                        logger.error(ee)
                        return json.dumps([{"status": "WMS原料单取消关联SAP采购单报错:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
                                          ensure_ascii=False)
        except Exception as e:
            print(e)
            logger.error(e)
            return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
            insertSyslog("error", "WMS原料单取消关联SAP采购单报错：" + str(e), current_user.Name)