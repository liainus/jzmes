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
import Model.node
from tools.MESLogger import MESLogger
from Model.system import User,Role,Menu

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
        bReturn = True
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
                    EnterTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    PlanBeginTime=APlanBeginTime,
                    # PlanEndTime=APlanEndTime,
                    # ActBeginTime="",
                    # ActEndTime="",
                    ZYPlanStatus=Model.Global.ZYPlanStatus.NEW.value,
                    LockStatus=Model.Global.TASKLOCKSTATUS.UNLOCK.value,
                    INFStatus=Model.Global.TASKSTATUS.NEW.value,
                    WMSStatus=Model.Global.TASKSTATUS.NEW.value))
            session.commit()
            ZYPlanID = session.query(Model.core.ZYPlan.ID).filter(Model.core.ZYPlan.BatchID == ABatchID,Model.core.ZYPlan.PUID==APUID).first()
            ZYPlanID = ZYPlanID[0]
            PlanManageID = session.query(Model.core.PlanManager.ID).filter_by(BatchID=ABatchID).first()
            PlanManageID = PlanManageID[0]
            AuditStatus = Model.Global.AuditStatus.Realse.value
            DescF = "计划向导生成计划zyplan"
            bReturn = self.createWorkFlowStatus(PlanManageID, ZYPlanID, None, AuditStatus, DescF)
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            bReturn = False
            print(e)
            logger.error(e)
            return bReturn


    def createPUTask(self, APUID, ABatchID, ABrandID, ABrandName, APlanWeight,ATaskNO,ASeq, APlanDate, AUnit,ASetRepeatCount):
        bReturn = True;
        try:
            session.add(
                Model.core.ZYTask(
                    PlanDate=APlanDate,
                    TaskID=ATaskNO,
                    BatchID=ABatchID,
                    PlanSeq=ASeq,
                    PUID=APUID,
                    # PDUnitRouteName=iPDUnitRouteName,
                    PlanType=Model.Global.PLANTYPE.SCHEDULE.value,
                    BrandID=ABrandID,
                    BrandName=ABrandName,
                    PlanQuantity=APlanWeight,
                    # ActQuantity="",
                    Unit=AUnit,
                    EnterTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    # ActBeginTime="",
                    # ActEndTime="",
                    SetRepeatCount=ASetRepeatCount,
                    # CurretnRepeatCount=odata['CurretnRepeatCount'],
                    # ActTank=odata['ActTank'],
                    TaskStatus=Model.Global.TASKSTATUS.NEW.value,
                    LockStatus=Model.Global.TASKLOCKSTATUS.UNLOCK.value))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn

    def getPUPara(self,APUID,ABrandID):#, APUPara
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductParameter).filter(
                Model.core.ProductParameter.ProductRuleID == ABrandID).filter(
                Model.core.ProductParameter.PUID == APUID).first() #.filter(Model.core.ProductParameter.PDParaCode ==APUPara)
            if oclass is None:
                bReturn = True
                paraValue = 1
            else:
                paraValue = int(oclass.Value)
            return bReturn, paraValue
        except Exception as e:
            bReturn = False
            print(e)
            logger.error(e)
            return  bReturn,paraValue

    def getLineInfo(self,ABrandName):
        bReturn = True
        try:
            oclass = session.query(Model.core.ProductLine).filter(
                Model.core.ProductLine.PLineName == ABrandName).first() #"江中罗亭生产线1"
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

    def createPlanManager(self, APlanDate, ABatchID,ABrandID,ABrandName,ASeq,AType,APlanQuantity,AUnit):
        bReturn = True;
        try:
            session.add(
                Model.core.PlanManager(
                    SchedulePlanCode=APlanDate,
                    BatchID = ABatchID,
                    BrandID = ABrandID,
                    BrandName = ABrandName,
                    # Seq = ASeq,
                    PlanBeginTime = APlanDate + " " + Model.Global.GLOBAL_PLANSTARTTIME,
                    Type = AType,
                    PlanQuantity = APlanQuantity,
                    Unit = AUnit,
                    PlanStatus = Model.Global.PlanStatus.NEW.value))
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

    def createLinePlanManager(self, AProductRuleID, APlanWeight,APlanDate,ABatchID,ABrandID,ABrandName,PLineName,AUnit,userName):
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

            bReturn, iPLineID, sPLineName = self.getLineInfo(PLineName)
            if bReturn == False:
                return False
            bReturn, strTaskNo = self.getTaskNo()
            bReturn = self.createPlanManager(APlanDate, ABatchID, ABrandID, ABrandName, iPlanManageSeq, "", APlanWeight,
                                             AUnit)
            if bReturn == False:
                return False

            PlanManageID = session.query(Model.core.PlanManager.ID).filter_by(BatchID=ABatchID, BrandID=ABrandID).first()
            PlanManageID = PlanManageID[0]
            if (ABrandName == "健胃消食片浸膏粉"):
                bReturn = self.createOdd(PlanManageID)
                if bReturn == False:
                    return False
                flowPathNames = session.query(Model.node.Odd.flowPathName).filter(Model.node.Odd.oddNum==PlanManageID).all()
                for name in flowPathNames:
                    names = session.query(Model.node.Procedure.nodeName).filter(Model.node.Procedure.flowPathName == name).all()
                    for na in names:
                        bReturn = self.createNodeCollection(PlanManageID, na, userName)
                        if bReturn == False:
                            return False
            if (ABrandName == "肿节风浸膏"):
                bReturn = self.createOddC(PlanManageID)
                if bReturn == False:
                    return False
                flowPathNames = session.query(Model.node.Odd.flowPathName).filter(
                    Model.node.Odd.oddNum == PlanManageID).all()
                for name in flowPathNames:
                    names = session.query(Model.node.Procedure.nodeName).filter(
                        Model.node.Procedure.flowPathName == name).all()
                    for na in names:
                        bReturn = self.createNodeCollection(PlanManageID, na, userName)
                        if bReturn == False:
                            return False
            # Desc = "计划向导生成计划planmanager"
            # Type = Model.Global.AuditStatus.Unaudited.value
            # bReturn = self.createWorkFlowEventPlan(PlanManageID,userID,Desc,Type)
            # if bReturn == False:
            #     return False
            #
            # PlanManageID = PlanManageID
            # AuditStatus = Model.Global.AuditStatus.Unaudited.value
            # DescF = "计划向导生成计划planmanager"
            # bReturn = self.createWorkFlowStatus(PlanManageID, None, None, AuditStatus, DescF)
            # if bReturn == False:
            #     return False
            return True
        except Exception as e:
            session.rollback()
            print(e)
            logger.error(e)
            return bReturn
    def createNodeCollection(self,APlanManageID,name,userName):
        bReturn = True
        try:
            session.add(Model.node.NodeCollection(
                name=name,
                oddNum=APlanManageID,
                oddUser=""))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            print(e)
            logger.error(e)
            return False

    def createZYPlanZYTask(self, ID):
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
            oclassplan = session.query(Model.core.PlanManager).filter_by(ID=ID).first()
            PlanStatus = oclassplan.PlanStatus
            ABrandID = oclassplan.BrandID
            ABrandName = oclassplan.BrandName
            APlanWeight = oclassplan.PlanQuantity
            APlanDate = oclassplan.SchedulePlanCode
            AUnit = oclassplan.Unit
            ABatchID = oclassplan.BatchID
            strPlanStarTime = str(APlanDate) + " " + Model.Global.GLOBAL_PLANSTARTTIME
            bReturn, oRoutes = self.getProductUnitRoute(ABrandID)
            if bReturn == False:
                return False
            else:
                for obj in oRoutes:
                    iPUID = int(obj.PUID)
                    iProductRuleID = int(obj.ProductRuleID)
                    bReturn, strTaskNo = self.getTaskNo()
                    if (bReturn == True):
                        try:
                            bReturn, iPlanSeq = self.getPlanSeq(iPUID, APlanDate)
                            if bReturn == False:
                                return False

                            bReturn, iSetReatCount = self.getPUPara(iPUID, ABrandID)
                            if bReturn == False:
                                return False

                            bReturn, iTaskCount = self.queryProductContrlTask(ABrandID, iPUID, APlanWeight)
                            if bReturn == False:
                                return False

                            # bReturn, iPlanManageSeq = self.getPlanManagerSeq(iPLineID, APlanDate)
                            # if bReturn == False:
                            #     return False
                            iReturn, iIsExist, sErr = self.IsExistBatchID(ABatchID)
                            if iReturn == -1:
                                return False
                            elif iIsExist == 0:
                                pass
                            else:
                                pass

                            bReturn = self.createPUPlan(iPUID, ABatchID, ABrandID, ABrandName, APlanWeight, strTaskNo,
                                                        iPlanSeq, APlanDate, AUnit, strPlanStarTime,
                                                        Model.Global.GLOBAL_PLANENDTIME)
                            if bReturn == False:
                                return False

                            if iTaskCount >= 1:
                                iTaskSeq = 0
                                for num in range(0, iTaskCount):
                                    iTaskSeq = iTaskSeq + 1
                                    bReturn, strTaskNo = self.getTaskNo()
                                    if bReturn == False:
                                        return False
                                    bReturn = self.createPUTask(iPUID, ABatchID, ABrandID, ABrandName, APlanWeight,
                                                                strTaskNo, iTaskSeq, APlanDate, AUnit, iSetReatCount)
                                    if bReturn == False:
                                        return False
                        except Exception as e:
                            session.rollback()
                            print(e)
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

    def createWorkFlowEventPlan(self,APlanManageID,userName,Desc,Type):
        bReturn = True
        try:
            session.add(Model.core.WorkFlowEventPlan(
                PlanManageID=APlanManageID,
                userName=userName,
                Desc=Desc,
                Type=Type,
                EventTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            print(e)
            logger.error(e)
            return False

    def createWorkFlowEventZYPlan(self,AZYPlanID,userName,Desc,Type):
        bReturn = True
        try:
            session.add(Model.core.WorkFlowEventZYPlan(
                ZYPlanID=AZYPlanID,
                userName=userName,
                Desc=Desc,
                Type=Type,
                EventTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            print(e)
            logger.error(e)
            return False

    def createWorkFlowStatus(self,APlanManageID, AZYPlanID, AZYTaskID, AuditStatus, Desc):
        bReturn = True
        try:
            session.add(Model.core.WorkFlowStatus(
                PlanManageID=APlanManageID,
                ZYPlanID=AZYPlanID,
                ZYTaskID=AZYTaskID,
                AuditStatus=AuditStatus,
                Desc=Desc))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            print(e)
            logger.error(e)
            return False

    def createWorkFlowEven(self, PlanManageID, ID, param, userName, Desc, Type, EventTime):
        pass

    def sessionadd(self,APlanManageID,flowPathName):
        bReturn = True
        try:
            session.add(Model.node.Odd(
                oddNum=APlanManageID,
                flowPathName=flowPathName))
            session.commit()
            return bReturn
        except Exception as e:
            session.rollback()
            print(e)
            logger.error(e)
            return False
    def createOdd(self,APlanManageID):
        A = Model.node.flowPathNameJWXSP.A.value
        re = self.sessionadd(APlanManageID, A)
        B = Model.node.flowPathNameJWXSP.B.value
        re = self.sessionadd(APlanManageID, B)
        C = Model.node.flowPathNameJWXSP.C.value
        re = self.sessionadd(APlanManageID, C)
        D = Model.node.flowPathNameJWXSP.D.value
        re = self.sessionadd(APlanManageID, D)
        E = Model.node.flowPathNameJWXSP.E.value
        re = self.sessionadd(APlanManageID, E)
        F = Model.node.flowPathNameJWXSP.F.value
        re = self.sessionadd(APlanManageID, F)
        G = Model.node.flowPathNameJWXSP.G.value
        re = self.sessionadd(APlanManageID, G)
        H = Model.node.flowPathNameJWXSP.H.value
        re = self.sessionadd(APlanManageID, H)
        I = Model.node.flowPathNameJWXSP.I.value
        re = self.sessionadd(APlanManageID, I)
        J = Model.node.flowPathNameJWXSP.J.value
        re = self.sessionadd(APlanManageID, J)
        K = Model.node.flowPathNameJWXSP.K.value
        re = self.sessionadd(APlanManageID, K)
        L = Model.node.flowPathNameJWXSP.L.value
        re = self.sessionadd(APlanManageID, L)
        M = Model.node.flowPathNameJWXSP.M.value
        re = self.sessionadd(APlanManageID, M)
        N = Model.node.flowPathNameJWXSP.N.value
        re = self.sessionadd(APlanManageID, N)
        O = Model.node.flowPathNameJWXSP.O.value
        re = self.sessionadd(APlanManageID, O)
        P = Model.node.flowPathNameJWXSP.P.value
        re = self.sessionadd(APlanManageID, P)
        Q = Model.node.flowPathNameJWXSP.Q.value
        re = self.sessionadd(APlanManageID, Q)
        R = Model.node.flowPathNameJWXSP.R.value
        re = self.sessionadd(APlanManageID, R)
        S = Model.node.flowPathNameJWXSP.S.value
        re = self.sessionadd(APlanManageID, S)
        aa = Model.node.flowPathNameJWXSP.aa.value
        re = self.sessionadd(APlanManageID, aa)
        bb = Model.node.flowPathNameJWXSP.bb.value
        re = self.sessionadd(APlanManageID, bb)
        cc = Model.node.flowPathNameJWXSP.cc.value
        re = self.sessionadd(APlanManageID, cc)
        dd = Model.node.flowPathNameJWXSP.dd.value
        re = self.sessionadd(APlanManageID, dd)
        ee = Model.node.flowPathNameJWXSP.ee.value
        re = self.sessionadd(APlanManageID, ee)
        return re
    def createOddC(self,APlanManageID):
        A = Model.node.flowPathNameCSHHP.A.value
        re = self.sessionadd(APlanManageID, A)
        B = Model.node.flowPathNameCSHHP.B.value
        re = self.sessionadd(APlanManageID, B)
        C = Model.node.flowPathNameCSHHP.C.value
        re = self.sessionadd(APlanManageID, C)
        D = Model.node.flowPathNameCSHHP.D.value
        re = self.sessionadd(APlanManageID, D)
        E = Model.node.flowPathNameCSHHP.E.value
        re = self.sessionadd(APlanManageID, E)
        F = Model.node.flowPathNameCSHHP.F.value
        re = self.sessionadd(APlanManageID, F)
        G = Model.node.flowPathNameCSHHP.G.value
        re = self.sessionadd(APlanManageID, G)
        H = Model.node.flowPathNameCSHHP.H.value
        re = self.sessionadd(APlanManageID, H)
        I = Model.node.flowPathNameCSHHP.I.value
        re = self.sessionadd(APlanManageID, I)
        J = Model.node.flowPathNameCSHHP.J.value
        re = self.sessionadd(APlanManageID, J)
        K = Model.node.flowPathNameCSHHP.K.value
        re = self.sessionadd(APlanManageID, K)
        L = Model.node.flowPathNameCSHHP.L.value
        re = self.sessionadd(APlanManageID, L)
        M = Model.node.flowPathNameCSHHP.M.value
        re = self.sessionadd(APlanManageID, M)
        N = Model.node.flowPathNameCSHHP.N.value
        re = self.sessionadd(APlanManageID, N)
        O = Model.node.flowPathNameCSHHP.O.value
        re = self.sessionadd(APlanManageID, O)
        P = Model.node.flowPathNameCSHHP.P.value
        re = self.sessionadd(APlanManageID, P)
        Q = Model.node.flowPathNameCSHHP.Q.value
        re = self.sessionadd(APlanManageID, Q)
        R = Model.node.flowPathNameCSHHP.R.value
        re = self.sessionadd(APlanManageID, R)
        S = Model.node.flowPathNameCSHHP.S.value
        re = self.sessionadd(APlanManageID, S)
        T = Model.node.flowPathNameCSHHP.T.value
        re = self.sessionadd(APlanManageID, T)
        U = Model.node.flowPathNameCSHHP.U.value
        re = self.sessionadd(APlanManageID, U)
        V = Model.node.flowPathNameCSHHP.V.value
        re = self.sessionadd(APlanManageID, V)
        aa = Model.node.flowPathNameCSHHP.aa.value
        re = self.sessionadd(APlanManageID, aa)
        bb = Model.node.flowPathNameCSHHP.bb.value
        re = self.sessionadd(APlanManageID, bb)
        cc = Model.node.flowPathNameCSHHP.cc.value
        re = self.sessionadd(APlanManageID, cc)
        dd = Model.node.flowPathNameCSHHP.dd.value
        re = self.sessionadd(APlanManageID, dd)
        ee = Model.node.flowPathNameCSHHP.ee.value
        re = self.sessionadd(APlanManageID, ee)
        ff = Model.node.flowPathNameCSHHP.ff.value
        re = self.sessionadd(APlanManageID, ff)
        return re


# class SystemCtrol:
#     def __init__(self,name):
#         try:
#             self.name = name
#         except Exception as e:
#             print(e)
#             logger.error(e)
#
#     # 将password字段定义为User类的一个属性，其中设置该属性不可读，若读取抛出AttributeError。
#     @property
#     def password(self):
#         raise AttributeError('password cannot be read')
#
#     # 定义password字段的写方法，我们调用generate_password_hash将明文密码password转成密文Shadow
#     @password.setter
#     def password(self, password):
#         self.Shadow = generate_password_hash(password)
#
#     # 定义验证密码的函数confirm_password
#     def confirm_password(self, password):
#         return check_password_hash(self.Shadow, password)

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