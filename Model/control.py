import datetime
import json
import json
# 引入mssql数据库引擎
import pymssql
import re
import sys
from collections import Counter
from datetime import datetime, date, timedelta
from enum import Enum
from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode, BigInteger
from sqlalchemy import create_engine, Column, ForeignKey, Table, DateTime, Integer, String
from sqlalchemy import func
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import Model.Global
import Model.core
from tools.MESLogger import MESLogger
from Model.system import User,Role,Permission,Menu

# 创建对象的基类
engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
# Session = sessionmaker(bind=engine)
# session = Session()
# Base = declarative_base(engine)

Base = declarative_base(engine)
session = sessionmaker(engine)()
logger = MESLogger('../logs','log')

class ctrlPlan:
    def __init__(self,name):
        try:
            self.name = name
            # self.productrule = Model.core.ProductRule("1")
            # self.productunit = Model.core.ProductUnit("2")
            # self.productcontrltask = Model.core.ProductContrlTask("3")
            # self.productparameter = Model.core.ProductParameter("4")
            # self.materialbom = Model.core.MaterialBOM("5")
            # self.productunitroute = Model.core.ProductUnitRoute("6")
            # self.scheduleplan = Model.core.SchedulePlan("7")
            # self.planmanager = Model.core.PlanManager("8")
            # self.unit = Model.core.Unit("9")
        except Exception as e:
            print(e)
            logger.error(e)

    def getjsondata(self):
        f = open("Plan.json", encoding='utf-8')
        setting = json.load(f)
        productdate = setting['productdate']
        brand = setting['brand']
        planweight = setting['planweight']
        unit = setting['unit']
        unitcode = setting['unitcode']

    def queryPlanDate(self,AProductDate):
        bReturn = True
        try:
            oclass = session.query(Model.core.SchedulePlan).filter_by(SchedulePlanCode=AProductDate).first()
            if oclass is None:
                bReturn = False
            else:
                session.add(Model.core.SchedulePlan(SchedulePlanCode=AProductDate, Desc="", PlanBeginTime="2018-05-04 08:00:00",
                                                             PlanEndTime="2018-05-05 07:59:59", Type="天"))
                session.commit()
            return (bReturn,oclass)
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return (bReturn, oclass)

    def queryProductRule(self,AID):
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductRule).filter_by(ID=AID).first()
            if oclass is None:
                bReturn = False
            else:
                bReturn = True
            return (bReturn,oclass)
        except Exception as e:
            print(e)
            logger.error(e)
            return (bReturn, oclass)

    def queryProductUnit(self,AID):
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductUnit).filter_by(ProductRuleID=AID).all()
            if oclass is None:
                bReturn = False
            else:
                bReturn = True
            return (bReturn,oclass)
        except Exception as e:
            print(e)
            logger.error(e)
            return (bReturn, oclass)

    def queryProductUnitRoute(self,AID):
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductUnitRoute).filter_by(ProductRuleID=AID).all()
            if oclass is None:
                bReturn = False
            else:
                bReturn = True
            return (bReturn,oclass)
        except Exception as e:
            print(e)
            logger.error(e)
            return (bReturn, oclass)

    def queryProductContrlTask(self, AID,APUID, AWeight):
        bReturn = True
        iTaskCount = 0
        try:
            oclass = session.query(Model.core.ProductControlTask)\
                .filter(Model.core.ProductControlTask.ProductRuleID==AID) \
                .filter(Model.core.ProductControlTask.PUID == APUID) \
                .filter(Model.core.ProductControlTask.LowLimit<=AWeight)\
                .filter(Model.core.ProductControlTask.HighLimit > AWeight).first()
            if oclass is None:
                bReturn = False
            else:
                bReturn = True
                iTaskCount = int(oclass.RelateTaskCount)
            return (bReturn,iTaskCount)
        except Exception as e:
            print(e)
            logger.error(e)
            return (bReturn, iTaskCount)

    def createPUPlan(self,APUID,ABatchID, ABrandID, ABrandName, APlanWeight,ATaskNO,ASeq, APlanDate, AUnit,APlanBeginTime,APlanEndTime):
        bReturn = True;
        try:
            session.add(
                Model.core.ZYPlan(
                    PlanDate=APlanDate,
                    PlanNo=ATaskNO,
                    BatchID=ABatchID,
                    PlanSeq=ASeq,
                    PUID=APUID,
                    PlanType=Model.Global.PLANTYPE.SCHEDULE.value,
                    BrandID=ABrandID,
                    BrandName=ABrandName,
                    ERPOrderNo="",
                    PlanQuantity=APlanWeight,
                    # ActQuantity=0,
                    Unit=AUnit,
                    EnterTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    PlanBeginTime=APlanBeginTime,
                    PlanEndTime=APlanEndTime,
                    ActBeginTime="",
                    ActEndTime="",
                    TaskStatus=Model.Global.TASKSTATUS.COMPILE.value,
                    LockStatus=Model.Global.TASKLOCKSTATUS.LOCKED.value,
                    INFStatus=Model.Global.TASKSTATUS.COMPILE.value,
                    WMSStatus=Model.Global.TASKSTATUS.COMPILE.value))
            session.commit()
        except Exception as e:
            session.rollback()
            bReturn = False
            print(e)
            logger.error(e)
            return bReturn


    def createPUTask(self,APUID,ABatchID, ABrandID, ABrandName, APlanWeight,ATaskNO,ASeq, APlanDate, AUnit,ASetRepeatCount):
        bReturn = True;
        try:
            session.add(
                Model.core.ZYTask(
                    PlanDate=APlanDate,
                    TaskID=ATaskNO,
                    BatchID=ABatchID,
                    PlanSeq=ASeq,
                    PUID=APUID,
                    PlanType=Model.Global.PLANTYPE.SCHEDULE.value,
                    BrandID=ABrandID,
                    BrandName=ABrandName,
                    PlanQuantity=APlanWeight,
                    # ActQuantity="",
                    Unit=AUnit,
                    EnterTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    ActBeginTime="",
                    ActEndTime="",
                    SetRepeatCount=ASetRepeatCount,
                    # CurretnRepeatCount=odata['CurretnRepeatCount'],
                    # ActTank=odata['ActTank'],
                    TaskStatus=Model.Global.TASKSTATUS.COMPILE.value,
                    LockStatus=Model.Global.TASKLOCKSTATUS.LOCKED.value))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn

    def getPUPara(self,APUID,ABrandID, APUPara):
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductParameter).filter(
                Model.core.ProductParameter.ProductRuleID == ABrandID).filter(
                Model.core.ProductParameter.PUID == APUID).filter(
                Model.core.ProductParameter.PDParaCode ==APUPara).first()
            if oclass is None:
                bReturn = True
                paraValue = 0
            else:
                paraValue = int(oclass.Value)
            return bReturn, paraValue
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,paraValue

    def getLineInfo(self):
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductLine).filter(
                Model.core.ProductLine.PLineName == "江中罗亭生产线1").first()
            if oclass is None:
                bReturn = False
                return bReturn, "", ""
            else:
                return bReturn, str(oclass.ID),str(oclass.PLineName)
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,"",""

    def getPlanSeq(self,APUID,APlanDate):
        bReturn = True
        iSeq = 0
        try:
            oclass = session.query(func.max(Model.core.ZYPlan.PlanSeq)).filter(
                Model.core.ZYPlan.PlanDate == APlanDate).filter(
                Model.core.ZYPlan.PUID == APUID).all()
            if oclass[0][0] is None:
                bReturn = True
                iSeq = 1
            else:
                iSeq = int(oclass[0][0]) + 1
            return bReturn, iSeq
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,iSeq

    def getProductUnitRoute(self,AProductRuleID):
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductUnitRoute).filter(
                Model.core.ProductUnitRoute.ProductRuleID == AProductRuleID).all()
            if oclass is None:
                bReturn = False
            else:
                bReturn = True
            return bReturn, oclass
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,oclass

    def getTaskSeq(self,APUID,ABatchID):
        bReturn = True
        iSeq = 0
        try:
            oclass = session.query(Model.core.ZYTask).filter(
                Model.core.ZYTask.BatchID == ABatchID).filter(
                Model.core.ZYTask.PUID == APUID).last()
            if oclass is None:
                bReturn = True
                iSeq = 1
            else:
                iSeq = int(oclass["PlanSeq"])
            return bReturn, iSeq + 1
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,iSeq

    def getPlanManagerSeq(self,APLineID,APlanDate):
        bReturn = True
        iSeq = 0
        try:
            oclass = session.query(func.max(Model.core.PlanManager.Seq)).filter(
                Model.core.PlanManager.SchedulePlanCode == APlanDate).filter(
                Model.core.PlanManager.PLineID == APLineID).all()
            if oclass[0][0] is None:
                bReturn = True
                iSeq = 1
            else:
                iSeq = int(oclass[0][0]) + 1
            return bReturn, iSeq
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,iSeq

    def IsExistBatchID(self,ABatchID):
        iReturn = 0
        iIsExist = 0
        try:
            oclass = session.query(Model.core.PlanManager).filter(
                Model.core.PlanManager.BatchID == ABatchID).first()
            if oclass is None:
                iReturn = 0
                iIsExist = 0
            else:
                iReturn = 0
                iIsExist = 1
            return iReturn, iIsExist,Model.Global.GLOBAL_NULL_STRING
        except Exception as e:
            iReturn = -1
            print(e)
            logger.error(e)
            return iReturn, iIsExist,str(e)

    def createPlanManager(self, APlanDate, ABatchID,ABrandID,ABrandName,ASeq,AType,APlanQuantity,AUnit,APLineID,APlineName):
        bReturn = True;
        try:
            session.add(
                Model.core.PlanManager(
                    SchedulePlanCode=APlanDate,
                    BatchID = ABatchID,
                    BrandID = ABrandID,
                    BrandName = ABrandName,
                    Seq = ASeq,
                    PlanBeginTime = APlanDate + " " + Model.Global.GLOBAL_PLANSTARTTIME,
                    Type = AType,
                    PlanQuantity = APlanQuantity,
                    Unit = AUnit,
                    PLineID = APLineID,
                    PLineName = APlineName))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            bReturn = False
            print(e)
            logger.error(e)
            return bReturn

    def IsExistSchedulePlanDate(self,APlanDate):
        bReturn = False
        IsExist = False
        oclass = None
        try:
            oclass = session.query(Model.core.SchedulePlan).filter(
                Model.core.SchedulePlan.SchedulePlanCode == APlanDate).first()
            if oclass is None:
                bReturn = True
                IsExist = False
            else:
                bReturn = True
                IsExist = True
            return bReturn, IsExist
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return bReturn, IsExist

    def createSchedulePlan(self,APlanDate,ADesc,AType,APlanBeginTime,APlanEndTime):
        bReturn = True
        try:
            session.add(
                Model.core.SchedulePlan(
                    SchedulePlanCode=APlanDate,
                    Desc=ADesc,
                    PlanBeginTime=APlanBeginTime,
                    PlanEndTime=APlanEndTime,
                    Type=AType))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn

    def createLinePUPlan(self, AProductRuleID, APlanWeight,APlanDate,ABatchID,ABrandID,ABrandName,AUnit):
        bReturn = True
        bIsExist = True
        iPlanSeq = 0
        iTaskCount = 0
        iTaskSeq = 0
        iPlanManageSeq = 0
        iPLineID = 0
        sPLineName = ""
        iReturn = 0
        iIsExist = 0
        try:
            strPlanStarTime = str(APlanDate) + " " + Model.Global.GLOBAL_PLANSTARTTIME
            dEndTime = datetime.strptime(APlanDate, '%Y-%m-%d') + timedelta(days=1)
            strPlanEndTime = dEndTime.strftime('%Y-%m-%d') + " " + Model.Global.GLOBAL_PLANENDTIME
            bReturn,bIsExist = self.IsExistSchedulePlanDate(APlanDate)
            if (bReturn == True) and (bIsExist == False):
                bReturn = self.createSchedulePlan(APlanDate, Model.Global.SCHEDULETYPE.DAY.value,
                                                  Model.Global.SCHEDULETYPE.DAY.value, strPlanStarTime,strPlanEndTime)
                if bReturn == False:
                    return False

            bReturn, iPLineID, sPLineName = self.getLineInfo()
            if bReturn == False:
                return False
            bReturn,oRoutes = self.getProductUnitRoute(AProductRuleID)
            if bReturn == False:
                return False
            else:
                for obj in oRoutes:
                    iPUID = int(obj.PUID)
                    iProductRuleID = int(obj.ProductRuleID)
                    bReturn, strTaskNo = self.getTaskNo()
                    if (bReturn == True):
                        try:
                            bReturn,iPlanSeq = self.getPlanSeq(iPUID, APlanDate)
                            if bReturn == False:
                                return False

                            bReturn, iSetReatCount = self.getPUPara(iPUID, ABrandID, "SetReatCount")
                            if bReturn == False:
                                return False

                            bReturn, iTaskCount = self.queryProductContrlTask(ABrandID, iPUID, APlanWeight)
                            if bReturn == False:
                                return False

                            bReturn,iPlanManageSeq = self.getPlanManagerSeq(iPLineID,APlanDate)
                            if bReturn == False:
                                return False
                            iReturn,iIsExist,sErr = self.IsExistBatchID(ABatchID)
                            if iReturn == -1:
                                return False
                            elif iIsExist == 0:
                                bReturn = self.createPlanManager(APlanDate,ABatchID,ABrandID,ABrandName,iPlanManageSeq,"",APlanWeight,AUnit,iPLineID,sPLineName)
                                if bReturn == False:
                                    print("haha ")
                            else:
                                pass

                            bReturn = self.createPUPlan(iPUID, ABatchID, ABrandID, ABrandName, APlanWeight, strTaskNo,
                                                        iPlanSeq, APlanDate, AUnit, strPlanStarTime, Model.Global.GLOBAL_PLANENDTIME)
                            if bReturn == False:
                                return False

                            if iTaskCount >= 1:
                                iTaskSeq = 0
                                for num in range(0,iTaskCount):
                                    iTaskSeq = iTaskSeq + 1
                                    bReturn, strTaskNo = self.getTaskNo()
                                    if bReturn == False:
                                        return False
                                    bReturn = self.createPUTask(iPUID, ABatchID, ABrandID, ABrandName, APlanWeight,
                                                                strTaskNo, iTaskSeq, APlanDate, AUnit,iSetReatCount)
                                    if bReturn == False:
                                        return False
                        except Exception as e:
                            session.rollback()
                            print (e)
                            logger.error(e)
                            return False
            return True
        except Exception as e:
            print(e)
            logger.error(e)
            return bReturn

    def getTaskNo(self):
        bReturn = True
        qry = session.query(func.max(Model.core.TaskNoGenerator.TaskNoInt)).all();
        intTaskNo = int(qry[0][0])
        varTaskNo = str(intTaskNo + 1)
        if len(varTaskNo) == 1:
            varTaskNo = "00000" + varTaskNo
        elif len(varTaskNo) == 2:
            varTaskNo = "0000" + varTaskNo
        if len(varTaskNo) == 3:
            varTaskNo = "000" + varTaskNo
        if len(varTaskNo) == 4:
            varTaskNo = "00" + varTaskNo
        if len(varTaskNo) == 5:
            varTaskNo = "0" + varTaskNo
        else:
            varTaskNo = varTaskNo
        try:
            session.add(
                Model.core.TaskNoGenerator(
                    TaskNoInt=intTaskNo + 1,
                    TaskNoVar=varTaskNo,
                    Desc=""))
            session.commit()
            return bReturn,varTaskNo
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,varTaskNo

class SystemCtrol:
    def __init__(self,name):
        try:
            self.name = name
        except Exception as e:
            print(e)
            logger.error(e)

    # 将password字段定义为User类的一个属性，其中设置该属性不可读，若读取抛出AttributeError。
    @property
    def password(self):
        raise AttributeError('password cannot be read')

    # 定义password字段的写方法，我们调用generate_password_hash将明文密码password转成密文Shadow
    @password.setter
    def password(self, password):
        self.Shadow = generate_password_hash(password)

    # 定义验证密码的函数confirm_password
    def confirm_password(self, password):
        return check_password_hash(self.Shadow, password)

if __name__ == "__main__":
    mytest = ctrlPlan("a")
    mytest.getjsondata()
    mytest.queryPlanDate("2018-05-04")
    # mytest.queryproductrule(1)
    # mytest.queryproductunit(1)
    # mytest.queryProductunitroute(1)
    # mytest.queryProductContrlTask(1,4500)
    # mytest.createPUPlan(1,4500.0,"2018-05-04","201805040001",1,"健胃消食片",1,1)
    mytest.createLinePUPlan(1,4500.0,"2018-05-05","201805050001",1,"健胃消食片","h")
    print(mytest.getjsondata())