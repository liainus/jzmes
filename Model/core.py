
#/******************************************************************************************
# ************* STK make model usage:
# ************* version: print python3.6.3  version
# ************* make: make Python file
# ************* STK makemodel.py 1.0.0
# ************* @author Xujin
# ************* @date 2018-03-23 14:11:58
# ************* @Model 
# ******************************************************************************************/

import json
# 引入mssql数据库引擎
import re
import datetime
import sys
import pymssql
from collections import Counter
# -coding:utf-8--
# 引入必要的类库
from imp import reload

from flask_login import current_user
from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode, BigInteger,Boolean
from sqlalchemy import create_engine, Column, ForeignKey, Table, DateTime, Integer, String, desc
from sqlalchemy import func
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import Model.Global
from tools.MESLogger import MESLogger

# 创建对象的基类
engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base(engine)
logger = MESLogger('../logs','log')

#Data_RealTime:
class Data_RealTime(Base):
	__tablename__ = "Data_RealTime" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False)
	
	#Tag名称:
	TagID = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#更新时间:
	UpdateTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#值:
	Value = Column(Unicode(10), primary_key = False, autoincrement = False, nullable = True)
	
	#状态:
	Stauts = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#错误信息:
	ErrMessage = Column(Unicode(200), primary_key = False, autoincrement = False, nullable = True)
	
#Data_History:
class Data_History(Base):
	__tablename__ = "Data_History" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False)
	
	#Tag名称:
	TagID = Column(Unicode(100), primary_key = False, autoincrement = False, nullable = True)
	
	#采样时间:
	SampleTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#值:
	Value = Column(Unicode(100), primary_key = False, autoincrement = False, nullable = True)
	
#ServerStatus:
class ServerStatus(Base):
	__tablename__ = "ServerStatus" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False)
	
	#Server名称:
	ServerName = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#运行次数:
	ExecCount = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#成功次数:
	SuccessCount = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#失败次数:
	ErrCount = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#更新时间:
	UpdateTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#开始运行时间:
	BeginRunTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
#ZYPlan:
class ZYPlan(Base):
	__tablename__ = "ZYPlan" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False)
	
	#计划日期:
	PlanDate = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#制药计划单号:
	PlanNo = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#批次号:
	BatchID = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#顺序号:
	PlanSeq = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#工艺段:
	PUID = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#计划类型:
	PlanType = Column(Unicode(16), primary_key = False, autoincrement = False, nullable = True)
	
	#品名:
	BrandID = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#品名名称:
	BrandName = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#ERP订单号:
	ERPOrderNo = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#计划重量:
	PlanQuantity = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#实际重量:
	ActQuantity = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#录入时间:
	EnterTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#计划开始时间:
	PlanBeginTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)

	PlanEndTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
	
	#实际开始时间:
	ActBeginTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#实际完成时间:
	ActEndTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#计划状态:
	ZYPlanStatus = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#计划锁定状态:
	LockStatus = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#接口处理状态:
	INFStatus = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#仓储送料状态:
	WMSStatus = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
class ZYPlanWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allZYPlansCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ZYPlan(
						PlanDate= odata['PlanDate'],
						PlanNo= odata['PlanNo'],
						BatchID= odata['BatchID'],
						PlanSeq= odata['PlanSeq'],
						PUID= odata['PUID'],
						PlanType= odata['PlanType'],
						BrandID= '',#odata['BrandID'],
						BrandName= odata['BrandName'],
						ERPOrderNo= odata['ERPOrderNo'],
						PlanQuantity= odata['PlanQuantity'],
						ActQuantity= odata['ActQuantity'],
						Unit= odata['Unit'],
						# EnterTime= odata['EnterTime'],
						PlanBeginTime= odata['PlanBeginTime'],
						PlanEndTime= odata['PlanEndTime'],
						ActBeginTime= odata['ActBeginTime'],
						ActEndTime= odata['ActEndTime'],
						ZYPlanStatus= odata['ZYPlanStatus'],
						LockStatus= odata['LockStatus'],
						INFStatus= odata['INFStatus'],
						WMSStatus= odata['WMSStatus']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYPlansDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ZYPlanid = key
					try:
						oclass = session.query(Model.core.ZYPlan).filter_by(ID=ZYPlanid).first()
						taskids = session.query(Model.core.ZYTask.ID).filter_by(PUID=oclass.PUID, BatchID=oclass.BatchID)
						for taskid in taskids:
							taskoclass = session.query(Model.core.ZYTask).filter_by(ID=taskid).first()
							session.delete(taskoclass)
							session.commit()
						session.delete(oclass)
						session.commit()
					except Exception as ee:
						print(ee)
						return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
												  ensure_ascii=False)
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ZYPlansFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ZYPlan.ID)).scalar()
				qDatas = session.query(Model.core.ZYPlan).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ZYPlan).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYPlansUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ZYPlanid = int(odata['ID'])
				oclass = session.query(Model.core.ZYPlan).filter_by(ID=ZYPlanid).first()
				oclass.PlanDate = odata['PlanDate']
				oclass.PlanNo = odata['PlanNo']
				oclass.BatchID = odata['BatchID']
				oclass.PlanSeq = odata['PlanSeq']
				oclass.PUID = odata['PUID']
				oclass.PlanType = odata['PlanType']
				# oclass.BrandID= odata['BrandID']
				oclass.BrandName = odata['BrandName']
				oclass.ERPOrderNo = odata['ERPOrderNo']
				oclass.PlanQuantity = odata['PlanQuantity']
				oclass.ActQuantity = odata['ActQuantity']
				oclass.Unit = odata['Unit']
				# oclass.EnterTime = odata['EnterTime']
				oclass.PlanBeginTime = odata['PlanBeginTime']
				oclass.PlanEndTime = odata['PlanEndTime']
				oclass.ActBeginTime = odata['ActBeginTime']
				oclass.ActEndTime = odata['ActEndTime']
				oclass.ZYPlanStatus = odata['ZYPlanStatus']
				oclass.LockStatus = odata['LockStatus']
				oclass.INFStatus = odata['INFStatus']
				oclass.WMSStatus = odata['WMSStatus']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYPlansSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ZYPlanscount = session.query(Model.core.ZYPlan).filter(
							ZYPlan.BatchID.like(strconditon)).all()
				total = Counter(ZYPlanscount)
				jsonZYPlans = json.dumps(ZYPlanscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonZYPlans = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonZYPlans + "}"
				return jsonZYPlans
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ZYPlanMaterial:
class ZYPlanMaterial(Base):
	__tablename__ = "ZYPlanMaterial" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = False)
	
	#计划日期:
	PlanDate = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#制药计划单号:
	PlanID = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#批次号:
	BatchID = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#顺序号:
	PlanSeq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#工艺段:
	PUID = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

	# 工艺路线名称:
	PDUnitRouteName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)
	
	#计划类型:
	PlanType = Column(Unicode(16), primary_key = False, autoincrement = False, nullable = True)
	
	#牌号编码:
	BrandCode = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#牌号名称:
	BrandName = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#物料ID:
	MaterialID = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#物料名称名称:
	MaterialName = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#计划重量:
	PlanQuantity = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#实际重量:
	ActQuantity = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#录入时间:
	EnterTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
class ZYPlanMaterialWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allZYPlanMaterialsCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ZYPlanMaterial(
						PlanDate=odata['PlanDate'],
						PlanID=odata['PlanID'],
						BatchID=odata['BatchID'],
						PlanSeq=odata['PlanSeq'],
						PUID=odata['PUID'],
						PlanType=odata['PlanType'],
						BrandCode=odata['BrandCode'],
						BrandName=odata['BrandName'],
						MaterialID=odata['MaterialID'],
						MaterialName=odata['MaterialName'],
						PlanQuantity=odata['PlanQuantity'],
						ActQuantity=odata['ActQuantity'],
						Unit=odata['Unit'],
						EnterTime=odata['EnterTime']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYPlanMaterialsDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ZYPlanMaterialid = int(key)
					try:
						oclass = session.query(Model.core.ZYPlanMaterial).filter_by(ID=ZYPlanMaterialid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ZYPlanMaterialsFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ZYPlanMaterial.ID)).scalar()
				qDatas = session.query(Model.core.ZYPlanMaterial).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ZYPlanMaterial).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYPlanMaterialsUpdate(self,rcvdata):
		global oclass
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ZYPlanMaterialid = int(odata['ID'])
				oclass = session.query(Model.core.ZYPlanMaterial).filter_by(ID=ZYPlanMaterialid).first()
				oclass.PlanDate = odata['PlanDate']
				oclass.PlanID = odata['PlanID']
				oclass.BatchID = odata['BatchID']
				oclass.PlanSeq = odata['PlanSeq']
				oclass.PUID = odata['PUID']
				oclass.PlanType = odata['PlanType']
				oclass.BrandCode = odata['BrandCode']
				oclass.BrandName = odata['BrandName']
				oclass.MaterialID = odata['MaterialID']
				oclass.MaterialName = odata['MaterialName']
				oclass.PlanQuantity = odata['PlanQuantity']
				oclass.ActQuantity = odata['ActQuantity']
				oclass.Unit = odata['Unit']
				oclass.EnterTime = odata['EnterTime']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYPlanMaterialsSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ZYPlanMaterialscount = session.query(Model.core.ZYPlanMaterial).filter(
							ZYPlanMaterial.BatchID.like(strconditon)).all()
				total = Counter(ZYPlanMaterialscount)
				jsonZYPlanMaterials = json.dumps(ZYPlanMaterialscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonZYPlanMaterials = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonZYPlanMaterials + "}"
				return jsonZYPlanMaterials
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ZYTask:
class ZYTask(Base):
	__tablename__ = "ZYTask" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = True)

	# 设备ID:
	EquipmentID = Column(Unicode(30), primary_key=False, autoincrement=True, nullable=True)
	
	#计划日期:
	PlanDate = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#制药任务单号:
	TaskID = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#批次号:
	BatchID = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#顺序号:
	PlanSeq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#工艺段:
	PUID = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

	# 工艺路线名称:
	PDUnitRouteName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	#计划类型:
	PlanType = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#牌号编码:
	BrandID = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#牌号名称:
	BrandName = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#计划重量:
	PlanQuantity = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#实际重量:
	ActQuantity = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#录入时间:
	EnterTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#实际开始时间:
	ActBeginTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#实际完成时间:
	ActEndTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#设定重复次数:
	SetRepeatCount = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#当前重复次数:
	CurretnRepeatCount = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#实际罐号:
	ActTank = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#任务状态:
	TaskStatus = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#任务锁定状态:
	LockStatus = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
class ZYTaskWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allZYTasksCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ZYTask(
						PlanDate=odata['PlanDate'],
						TaskID=odata['TaskID'],
						BatchID=odata['BatchID'],
						PlanSeq=odata['PlanSeq'],
						PUID=odata['PUID'],
						PlanType=odata['PlanType'],
						BrandID=odata['BrandID'],
						BrandName=odata['BrandName'],
						PlanQuantity=odata['PlanQuantity'],
						ActQuantity=odata['ActQuantity'],
						Unit=odata['Unit'],
						# EnterTime=odata['EnterTime'],
						ActBeginTime=odata['ActBeginTime'],
						ActEndTime=odata['ActEndTime'],
						SetRepeatCount=odata['SetRepeatCount'],
						CurretnRepeatCount=odata['CurretnRepeatCount'],
						ActTank=odata['ActTank'],
						TaskStatus=odata['TaskStatus'],
						LockStatus=odata['LockStatus']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYTasksDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ZYTaskid = int(key)
					try:
						oclass = session.query(Model.core.ZYTask).filter_by(ID=ZYTaskid).first()
						session.delete(oclass)
						session.commit()
					except Exception as ee:
						print(ee)
						return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
												  ensure_ascii=False)
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ZYTasksFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ZYTask.ID)).scalar()
				qDatas = session.query(Model.core.ZYTask).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ZYTask).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYTasksUpdate(self,rcvdata):
		global oclass
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ZYTaskid = int(odata['ID'])
				oclass = session.query(Model.core.ZYTask).filter_by(ID=ZYTaskid).first()
				oclass.PlanDate = odata['PlanDate']
				oclass.TaskID = odata['TaskID']
				oclass.BatchID = odata['BatchID']
				oclass.PlanSeq = odata['PlanSeq']
				oclass.PUID = odata['PUID']
				oclass.PlanType = odata['PlanType']
				oclass.BrandID = odata['BrandID']
				oclass.BrandName = odata['BrandName']
				oclass.PlanQuantity = odata['PlanQuantity']
				oclass.ActQuantity = odata['ActQuantity']
				oclass.Unit = odata['Unit']
				oclass.EnterTime = odata['EnterTime']
				oclass.ActBeginTime = odata['ActBeginTime']
				oclass.ActEndTime = odata['ActEndTime']
				oclass.SetRepeatCount = odata['SetRepeatCount']
				oclass.CurretnRepeatCount = odata['CurretnRepeatCount']
				oclass.ActTank = odata['ActTank']
				oclass.TaskStatus = odata['TaskStatus']
				oclass.LockStatus = odata['LockStatus']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allZYTasksSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ZYTaskscount = session.query(Model.core.ZYTask).filter(
							ZYTask.TaskID.like(strconditon)).all()
				total = Counter(ZYTaskscount)
				jsonZYTasks = json.dumps(ZYTaskscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonZYTasks = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonZYTasks + "}"
				return jsonZYTasks
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ProductLine:
class ProductLine(Base):
	__tablename__ = "ProductLine" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#生产线编码:
	PLineCode = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#生产线名称:
	PLineName = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#车间ID:
	AreaID =Column(Integer, ForeignKey("Area.ID"), nullable=False, primary_key=False)

	#描述:
	Desc = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#产线能力:
	PLineCapacity = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#计划类型:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class ProductLineWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allProductLinesCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ProductLine(
						PLineCode=odata['PLineCode'],
						PLineName=odata['PLineName'],
						AreaID = odata['AreaID'],
						PLineCapacity=odata['PLineCapacity'],
						Seq=odata['Seq'],
						Unit=odata['Unit'],
						Desc=odata['Desc']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductLinesDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ProductLineid = int(key)
					try:
						oclass = session.query(Model.core.ProductLine).filter_by(ID=ProductLineid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ProductLinesFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ProductLine.ID)).scalar()
				qDatas = session.query(Model.core.ProductLine).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ProductLine).all()[inipage:endpage]

					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductLinesUpdate(self,rcvdata):
		global oclass
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ProductLineid = int(odata['ID'])
				oclass = session.query(Model.core.ProductLine).filter_by(ID=ProductLineid).first()
				oclass.PLineCode = odata['PLineCode']
				oclass.PLineName = odata['PLineName']
				oclass.AreaID = odata['AreaID']
				oclass.Seq = odata['Seq']
				oclass.Desc = odata['Desc']
				oclass.PLineCapacity = odata['PLineCapacity']
				oclass.Unit = odata['Unit']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductLinesSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ProductLinescount = session.query(Model.core.ProductLine).filter(
							ProductLine.PLineName.like(strconditon)).all()
				total = Counter(ProductLinescount)
				jsonProductLines = json.dumps(ProductLinescount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonProductLines = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonProductLines + "}"
				return jsonProductLines
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ProcessUnit:
class ProcessUnit(Base):
	__tablename__ = "ProcessUnit" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#工艺段编码:
	PUCode = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#工艺段名称:
	PUName = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#生产线ID:
	PLineID =Column(Integer, ForeignKey("ProductLine.ID"), nullable=False, primary_key=False)

	#描述:
	Desc = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)
	
	#工艺段额定生产能力:
	PURateCapacity = Column(Unicode(30), primary_key = False, autoincrement = False, nullable = True)
	
	#工艺段计划生产能力:
	PUPLanCapacity = Column(Unicode(30), primary_key = False, autoincrement = False, nullable = True)
	
	#工艺段顺序号:
	Seq = Column(Unicode(30), primary_key = False, autoincrement = False, nullable = True)
	
	#能力单位:
	CapacityUnit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#静置时间:
	PlaceTime = Column(Unicode(30), primary_key = False, autoincrement = False, nullable = True)
	
	#时间单位:
	TimeUnit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#批次运行时间:
	BatchRunTime = Column(Unicode(30), primary_key = False, autoincrement = False, nullable = True)

class ProcessUnitWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allProcessUnitsCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ProcessUnit(
						PUCode=odata['PUCode'],
						PUName=odata['PUName'],
						PLineID=int(odata['PLineID']),
						Desc=odata['Desc'],
						PURateCapacity=odata['PURateCapacity'],
						PUPLanCapacity=odata['PUPLanCapacity'],
						Seq=odata['Seq'],
						CapacityUnit=odata['CapacityUnit'],
						PlaceTime=odata['PlaceTime'],
						TimeUnit=odata['TimeUnit'],
						BatchRunTime=odata['BatchRunTime']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProcessUnitsDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ProcessUnitid = int(key)
					try:
						oclass = session.query(Model.core.ProcessUnit).filter_by(ID=ProcessUnitid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ProcessUnitsFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ProcessUnit.ID)).scalar()
				qDatas = session.query(Model.core.ProcessUnit).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ProcessUnit).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProcessUnitsUpdate(self,rcvdata):
		global oclass
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ProcessUnitid = int(odata['ID'])
				oclass = session.query(Model.core.ProcessUnit).filter_by(ID=ProcessUnitid).first()
				oclass.PUCode = odata['PUCode']
				oclass.PUName = odata['PUName']
				oclass.PLineID = odata['PLineID']
				oclass.Desc = odata['Desc']
				oclass.PURateCapacity = odata['PURateCapacity']
				oclass.PUPLanCapacity = odata['PUPLanCapacity']
				oclass.Seq = odata['Seq']
				oclass.CapacityUnit = odata['CapacityUnit']
				oclass.PlaceTime = odata['PlaceTime']
				oclass.TimeUnit = odata['TimeUnit']
				oclass.BatchRunTime = odata['BatchRunTime']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProcessUnitsSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ProcessUnitscount = session.query(Model.core.ProcessUnit).filter(
							ProcessUnit.PUName.like(strconditon)).all()
				total = Counter(ProcessUnitscount)
				jsonProcessUnits = json.dumps(ProcessUnitscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonProcessUnits = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonProcessUnits + "}"
				return jsonProcessUnits
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#Equipment:
class Equipment(Base):
	__tablename__ = "Equipment" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#设备编码:
	EQPCode = Column(Unicode(30), primary_key = False, autoincrement = False, nullable = True)
	
	#设备名称:
	EQPName = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)

	# 企业编码:
	EnterpriseCode = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 企业名称:
	EnterpriseName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 批次对应的opc变量名
	BatchOpcTag = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	# 牌号对应的opc变量名
	BrandOpcTag = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	# 设备型号:
	Equipment_Model = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	# 生产厂家:
	Manufactor  = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	# 设备状态:
	Equipment_State = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	#金额(原值):
	money = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	# 来源:
	Equipment_From = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	# 设备类型:
	Equipment_Type = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	#  设备功率(KW/h):
	Equipment_Power = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	#工艺段ID:
	PUID =Column(Integer, nullable=False, primary_key=False)

	#描述:
	Desc = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)

	# 生产日期:
	Manufacture_Date = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)


# 设备建模表
class Pequipment(Base):
	__tablename__ = "Pequipment"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)

	# 设备编码:
	EQPCode = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)

	# 设备名称:
	EQPName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

	# 工艺段ID:
	PUID = Column(Integer, nullable=False, primary_key=False)

	#描述:
	Desc = Column(Unicode(50), primary_key = False, autoincrement = False, nullable = True)

class EquipmentWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allEquipmentsCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.Equipment(
						EQPCode=odata['EQPCode'],
						EQPName=odata['EQPName'],
						EnterpriseCode=odata['EnterpriseCode'],
						EnterpriseName=odata['EnterpriseName'],
						BatchOpcTag=odata['BatchOpcTag'],
						BrandOpcTag=odata['BrandOpcTag'],
						Equipment_Model=odata['Equipment_Model'],
						Manufactor=odata['Manufactor'],
						Equipment_State=odata['Equipment_State'],
						money=odata['money'],
						Equipment_From=odata['Equipment_From'],
						Equipment_Type=odata['Equipment_Type'],
						Equipment_Power=odata['Equipment_Power'],
						PUID=odata['PUID'],
						Desc=odata['Desc'],
						Manufacture_Date=odata['Manufacture_Date']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allEquipmentsDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					Equipmentid = int(key)
					try:
						oclass = session.query(Model.core.Equipment).filter_by(ID=Equipmentid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def EquipmentsFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.Equipment.ID)).scalar()
				qDatas = session.query(Model.core.Equipment).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.Equipment).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allEquipmentsUpdate(self,rcvdata):
		global oclass
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				Equipmentid = int(odata['ID'])
				oclass = session.query(Model.core.Equipment).filter_by(ID=Equipmentid).first()
				oclass.EQPCode = odata['EQPCode']
				oclass.EQPName = odata['EQPName']
				oclass.EnterpriseCode = odata['EnterpriseCode']
				oclass.EnterpriseName = odata['EnterpriseName']
				oclass.BatchOpcTag = odata['BatchOpcTag']
				oclass.BrandOpcTag = odata['BrandOpcTag']
				oclass.Equipment_Model = odata['Equipment_Model']
				oclass.Manufactor = odata['Manufactor']
				oclass.Equipment_State = odata['Equipment_State']
				oclass.money = odata['money']
				oclass.Equipment_From = odata['Equipment_From']
				oclass.Equipment_Type = odata['Equipment_Type']
				oclass.Equipment_Power = odata['Equipment_Power']
				oclass.PUID = odata['PUID']
				oclass.Desc = odata['Desc']
				oclass.Manufacture_Date = odata['Manufacture_Date']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allEquipmentsSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				Equipmentscount = session.query(Model.core.Equipment).filter(
							Equipment.EQPCode.like(strconditon)).all()
				total = Counter(Equipmentscount)
				jsonEquipments = json.dumps(Equipmentscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonEquipments = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonEquipments + "}"
				return jsonEquipments
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#BatchData:
class BatchData(Base):
	__tablename__ = "BatchData" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = True)
	
	#任务关联ID:
	TaskID =Column(BigInteger, ForeignKey("ZYTask.ID"), nullable=False, primary_key=False)

	#批记录采集项:
	Item = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#值:
	Value = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#类型:
	Type = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
#Enterprise:
class Enterprise(Base):
	__tablename__ = "Enterprise" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#企业编码:
	EnterpriseCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#企业名称:
	EnterpriseName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#企业代码:
	EnterpriseNo = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)

	#父节点名称
	ParentNodeName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#企业类型:
	Type = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#上级企业:
	ParentNode = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#顺序:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class EnterpriseWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allEnterprisesCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.Enterprise(
						EnterpriseCode=odata['EnterpriseCode'],
						EnterpriseName=odata['EnterpriseName'],
						EnterpriseNo = odata['EnterpriseNo'],
						ParentNodeName = odata['ParentNodeName'],
						ParentNode = odata['ParentNode'],
						Seq=odata['Seq'],
						Desc=odata['Desc'],
						Type=odata['Type']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allEnterprisesDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					Enterpriseid = int(key)
					try:
						oclass = session.query(Model.core.Enterprise).filter_by(ID=Enterpriseid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def EnterprisesFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.Enterprise.ID)).scalar()
				qDatas = session.query(Model.core.Enterprise).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.Enterprise).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allEnterprisesUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				Enterpriseid = int(odata['ID'])
				oclass = session.query(Model.core.Enterprise).filter_by(ID=Enterpriseid).first()
				oclass.EnterpriseCode = odata['EnterpriseCode']
				oclass.EnterpriseName = odata['EnterpriseName']
				oclass.EnterpriseNo = odata['EnterpriseNo']
				oclass.ParentNodeName = odata['ParentNodeName']
				oclass.ParentNode = odata['ParentNode']
				oclass.Seq = odata['Seq']
				oclass.Desc = odata['Desc']
				oclass.Type = odata['Type']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allEnterprisesSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				Enterprisescount = session.query(Model.core.Enterprise).filter(
							Enterprise.EnterpriseName.like(strconditon)).all()
				total = Counter(Enterprisescount)
				jsonEnterprises = json.dumps(Enterprisescount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonEnterprises = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonEnterprises + "}"
				return jsonEnterprises
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#Factory:
class Factory(Base):
	__tablename__ = "Factory" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#工厂编码:
	FactoryCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#工厂名称:
	FactoryName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#工厂代码:
	FactoryNo = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)

	# 父节点名称
	ParentNodeName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#工厂类型:
	Type = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#上级企业:
	ParentEnterprise = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#顺序:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class FactoryWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allFactorysCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.Factory(
						FactoryCode=odata['FactoryCode'],
						FactoryName=odata['FactoryName'],
						FactoryNo = odata['FactoryNo'],
						ParentNodeName = odata['ParentNodeName'],
						Desc=odata['Desc'],
						Type=odata['Type'],
						ParentEnterprise = odata['ParentEnterprise'],
					    Seq = odata['Seq']
				))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allFactorysDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					Factoryid = int(key)
					try:
						oclass = session.query(Model.core.Factory).filter_by(ID=Factoryid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def FactorysFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.Factory.ID)).scalar()
				qDatas = session.query(Model.core.Factory).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.Factory).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allFactorysUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				Factoryid = int(odata['ID'])
				oclass = session.query(Model.core.Factory).filter_by(ID=Factoryid).first()
				oclass.FactoryCode = odata['FactoryCode']
				oclass.FactoryName = odata['FactoryName']
				oclass.FactoryNo = odata['FactoryNo']
				oclass.ParentNodeName = odata['ParentNodeName']
				oclass.ParentEnterprise = odata['ParentEnterprise']
				oclass.Seq = odata['Seq']
				oclass.Desc = odata['Desc']
				oclass.Type = odata['Type']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allFactorysSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				Factoryscount = session.query(Model.core.Factory).filter(
							Factory.FactoryName.like(strconditon)).all()
				total = Counter(Factoryscount)
				jsonFactorys = json.dumps(Factoryscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonFactorys = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonFactorys + "}"
				return jsonFactorys
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#Area:
class Area(Base):
	__tablename__ = "Area" 
	
	#int:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#varchar(32):
	AreaCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#varchar(32):
	AreaName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#Varchar(200):
	AreaNo = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)

	##Varchar(200):
	ParentNodeName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#varchar(32):
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#Int:
	Type = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#Int:
	ParentFactory = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#int:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class AreaWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allAreasCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.Area(
						AreaCode=odata['AreaCode'],
						AreaName=odata['AreaName'],
						AreaNo = odata['AreaNo'],
						ParentNodeName = odata['ParentNodeName'],
						ParentFactory = odata['ParentFactory'],
						Seq=odata['Seq'],
						Desc=odata['Desc'],
						Type=odata['Type']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allAreasDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					Areaid = int(key)
					try:
						oclass = session.query(Model.core.Area).filter_by(ID=Areaid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def AreasFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.Area.ID)).scalar()
				qDatas = session.query(Model.core.Area).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.Area).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allAreasUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				Areaid = int(odata['ID'])
				oclass = session.query(Model.core.Area).filter_by(ID=Areaid).first()
				oclass.AreaCode = odata['AreaCode']
				oclass.AreaName = odata['AreaName']
				oclass.AreaNo = odata['AreaNo']
				oclass.ParentNodeName = odata['ParentNodeName']
				oclass.ParentFactory = odata['ParentFactory']
				oclass.Seq = odata['Seq']
				oclass.Desc = odata['Desc']
				oclass.Type = odata['Type']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allAreasSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				Areascount = session.query(Model.core.Area).filter(
							Area.AreaName.like(strconditon)).all()
				total = Counter(Areascount)
				jsonAreas = json.dumps(Areascount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonAreas = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonAreas + "}"
				return jsonAreas
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

#ProductRule:
class ProductRule(Base):
	__tablename__ = "ProductRule" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#产品定义编码:
	PRCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#产品定义名称:
	PRName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#版本:
	Version = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(200), primary_key = False, autoincrement = False, nullable = True)
	
	#发布日期:
	Publish_date = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#使用日期:
	Appy_date = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#是否使用:
	IsUsed = Column(BIT, primary_key = False, autoincrement = False, nullable = True)

class ProductRuleWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allProductRulesCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ProductRule(
						PRCode=odata['PRCode'],
						PRName=odata['PRName'],
						Version = odata['Version'],
						Desc=odata['Desc'],
						Publish_date = odata['Publish_date'],
						Appy_date=odata['Appy_date'],
						IsUsed=odata['IsUsed']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductRulesDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ProductRuleid = int(key)
					try:
						oclass = session.query(Model.core.ProductRule).filter_by(ID=ProductRuleid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ProductRulesFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ProductRule.ID)).scalar()
				qDatas = session.query(Model.core.ProductRule).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ProductRule).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductRulesUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ProductRuleid = int(odata['ID'])
				oclass = session.query(Model.core.ProductRule).filter_by(ID=ProductRuleid).first()
				oclass.PRCode = odata['PRCode']
				oclass.PRName = odata['PRName']
				oclass.Version = odata['Version']
				oclass.Desc = odata['Desc']
				oclass.Publish_date = odata['Publish_date']
				oclass.Appy_date = odata['Appy_date']
				oclass.IsUsed = odata['IsUsed']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductRulesSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ProductRulescount = session.query(Model.core.ProductRule).filter(
							ProductRule.PRName.like(strconditon)).all()
				total = Counter(ProductRulescount)
				jsonProductRules = json.dumps(ProductRulescount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonProductRules = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonProductRules + "}"
				return jsonProductRules
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ProductUnit:
class ProductUnit(Base):
	__tablename__ = "ProductUnit" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#产品段编码:
	PDUnitCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#产品段名称:
	PDUnitName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#持续时间:
	Duration = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#产品定义ID:
	ProductRuleID =Column(Integer, nullable=False, primary_key=False)

	#工艺段ID:
	PUID =Column(Integer, nullable=False, primary_key=False)

	#顺序号:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class ProductUnitWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allProductUnitsCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ProductUnit(
						PDUnitCode=odata['PDUnitCode'],
						PDUnitName=odata['PDUnitName'],
						Desc = odata['Desc'],
						Duration=odata['Duration'],
						Unit = odata['Unit'],
						ProductRuleID=odata['ProductRuleID'],
						PUID=odata['PUID'],
						Seq=odata['Seq']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductUnitsDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ProductUnitid = int(key)
					try:
						oclass = session.query(Model.core.ProductUnit).filter_by(ID=ProductUnitid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ProductUnitsFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ProductUnit.ID)).scalar()
				qDatas = session.query(Model.core.ProductUnit).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ProductUnit).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductUnitsUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ProductUnitid = int(odata['ID'])
				oclass = session.query(Model.core.ProductUnit).filter_by(ID=ProductUnitid).first()
				oclass.PDUnitCode = odata['PDUnitCode']
				oclass.PDUnitName = odata['PDUnitName']
				oclass.Desc = odata['Desc']
				oclass.Duration = odata['Duration']
				oclass.Unit = odata['Unit']
				oclass.ProductRuleID = odata['ProductRuleID']
				oclass.PUID = odata['PUID']
				oclass.Seq = odata['Seq']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductUnitsSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ProductUnitscount = session.query(Model.core.ProductUnit).filter(
							ProductUnit.PDUnitName.like(strconditon)).all()
				total = Counter(ProductUnitscount)
				jsonProductUnits = json.dumps(ProductUnitscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonProductUnits = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonProductUnits + "}"
				return jsonProductUnits
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ProductControlTask:
class ProductControlTask(Base):
	__tablename__ = "ProductControlTask" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = True)
	
	#产品段编码:
	PDCtrlTaskCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#产品段名称:
	PDCtrlTaskName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#低限:
	LowLimit = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#高限:
	HighLimit = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#相关任务数:
	RelateTaskCount = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#产品定义ID:
	ProductRuleID =Column(Integer, nullable=False, primary_key=False)

	#工艺段ID:
	PUID =Column(Integer, nullable=False, primary_key=False)

	#顺序号:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
class ProductControlTaskWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allProductControlTasksCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ProductControlTask(
						PDCtrlTaskCode=odata['PDCtrlTaskCode'],
						PDCtrlTaskName=odata['PDCtrlTaskName'],
						Desc=odata['Desc'],
						LowLimit=odata['LowLimit'],
						HighLimit=odata['HighLimit'],
						RelateTaskCount=odata['RelateTaskCount'],
						ProductRuleID=odata['ProductRuleID'],
						PUID=odata['PUID'],
						Seq=odata['Seq']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductControlTasksDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ProductControlTaskid = int(key)
					try:
						oclass = session.query(Model.core.ProductControlTask).filter_by(ID=ProductControlTaskid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ProductControlTasksFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ProductControlTask.ID)).scalar()
				qDatas = session.query(Model.core.ProductControlTask).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ProductControlTask).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductControlTasksUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ProductControlTaskid = int(odata['ID'])
				oclass = session.query(Model.core.ProductControlTask).filter_by(ID=ProductControlTaskid).first()
				oclass.PDCtrlTaskCode = odata['PDCtrlTaskCode']
				oclass.PDCtrlTaskName = odata['PDCtrlTaskName']
				oclass.Desc = odata['Desc']
				oclass.LowLimit = odata['LowLimit']
				oclass.HighLimit = odata['HighLimit']
				oclass.RelateTaskCount = odata['RelateTaskCount']
				oclass.ProductRuleID = odata['ProductRuleID']
				oclass.PUID = odata['PUID']
				oclass.Seq = odata['Seq']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductControlTasksSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ProductControlTaskscount = session.query(Model.core.ProductControlTask).filter(
							ProductControlTask.PDCtrlTaskName.like(strconditon)).all()
				total = Counter(ProductControlTaskscount)
				jsonProductControlTasks = json.dumps(ProductControlTaskscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonProductControlTasks = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonProductControlTasks + "}"
				return jsonProductControlTasks
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ProductParameter:
class ProductParameter(Base):
	__tablename__ = "ProductParameter" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = True)
	
	#产品段工艺参数编码:
	PDParaCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#产品段工艺参数名称:
	PDParaName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#值:
	Value = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#产品定义ID:
	ProductRuleID =Column(Integer, nullable=False, primary_key=False)

	#工艺段ID:
	PUID =Column(Integer, nullable=False, primary_key=False)

	#顺序号:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class ProductParameterWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allProductParametersCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ProductParameter(
						PDParaCode=odata['PDParaCode'],
						PDParaName=odata['PDParaName'],
						Desc=odata['Desc'],
						Value=odata['Value'],
						Unit=odata['Unit'],
						ProductRuleID=odata['ProductRuleID'],
						PUID=odata['PUID'],
						Seq=odata['Seq']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductParametersDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ProductParameterid = int(key)
					try:
						oclass = session.query(Model.core.ProductParameter).filter_by(ID=ProductParameterid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ProductParametersFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ProductParameter.ID)).scalar()
				qDatas = session.query(Model.core.ProductParameter).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ProductParameter).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductParametersUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ProductParameterid = int(odata['ID'])
				oclass = session.query(Model.core.ProductParameter).filter_by(ID=ProductParameterid).first()
				oclass.PDParaCode = odata['PDParaCode']
				oclass.PDParaName = odata['PDParaName']
				oclass.Desc = odata['Desc']
				oclass.Value = odata['Value']
				oclass.Unit = odata['Unit']
				oclass.ProductRuleID = odata['ProductRuleID']
				oclass.PUID = odata['PUID']
				oclass.Seq = odata['Seq']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductParametersSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ProductParameterscount = session.query(Model.core.ProductParameter).filter(
							ProductParameter.PDParaName.like(strconditon)).all()
				total = Counter(ProductParameterscount)
				jsonProductParameters = json.dumps(ProductParameterscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonProductParameters = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonProductParameters + "}"
				return jsonProductParameters
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#MaterialType:
class MaterialType(Base):
	__tablename__ = "MaterialType" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#产品段工艺参数编码:
	MATTypeCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#产品段工艺参数名称:
	MATTypeName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)

	#顺序号:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class MaterialTypeWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allMaterialTypesCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.MaterialType(
						MATTypeCode=odata['MATTypeCode'],
						MATTypeName=odata['MATTypeName'],
						Desc=odata['Desc'],
						Seq=odata['Seq']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialTypesDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					MaterialTypeid = int(key)
					try:
						oclass = session.query(Model.core.MaterialType).filter_by(ID=MaterialTypeid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def MaterialTypesFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.MaterialType.ID)).scalar()
				qDatas = session.query(Model.core.MaterialType).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.MaterialType).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialTypesUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				MaterialTypeid = int(odata['ID'])
				oclass = session.query(Model.core.MaterialType).filter_by(ID=MaterialTypeid).first()
				oclass.MATTypeCode = odata['MATTypeCode']
				oclass.MATTypeName = odata['MATTypeName']
				oclass.Desc = odata['Desc']
				oclass.Seq = odata['Seq']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialTypesSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				MaterialTypescount = session.query(Model.core.MaterialType).filter(
							MaterialType.MATTypeName.like(strconditon)).all()
				total = Counter(MaterialTypescount)
				jsonMaterialTypes = json.dumps(MaterialTypescount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonMaterialTypes = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonMaterialTypes + "}"
				return jsonMaterialTypes
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#Material:
class Material(Base):
	__tablename__ = "Material" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#物料编码:
	MATCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#物料名称:
	MATName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#物料描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#物料类型ID:
	MATTypeID =Column(Integer,  nullable=False, primary_key=False)

	#顺序号:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#等级:
	Grade = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#物料批次号:
	MATBatchNo = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
class MaterialWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allMaterialsCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.Material(
						MATCode=odata['MATCode'],
						MATName=odata['MATName'],
						MATTypeID=odata['MATTypeID'],
						Desc=odata['Desc'],
						Seq=odata['Seq'],
						Grade=odata['Grade'],
						MATBatchNo=odata['MATBatchNo']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialsDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					Materialid = int(key)
					try:
						oclass = session.query(Model.core.Material).filter_by(ID=Materialid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def MaterialsFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.Material.ID)).scalar()
				qDatas = session.query(Model.core.Material).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.Material).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialsUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				Materialid = int(odata['ID'])
				oclass = session.query(Model.core.Material).filter_by(ID=Materialid).first()
				oclass.MATCode = odata['MATCode']
				oclass.MATName = odata['MATName']
				oclass.MATTypeID = odata['MATTypeID']
				oclass.Desc = odata['Desc']
				oclass.Seq = odata['Seq']
				oclass.Grade = odata['Grade']
				oclass.MATBatchNo = odata['MATBatchNo']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialsSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				Materialscount = session.query(Model.core.Material).filter(
							Material.MATName.like(strconditon)).all()
				total = Counter(Materialscount)
				jsonMaterials = json.dumps(Materialscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonMaterials = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonMaterials + "}"
				return jsonMaterials
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#MaterialBOM:
class MaterialBOM(Base):
	__tablename__ = "MaterialBOM" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#物料ID:
	MATID =Column(Integer, nullable=False, primary_key=False)

	#投料批总重量:
	BatchTotalWeight = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#投料单一物料重量:
	BatchSingleMATWeight = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#百分比:
	BatchPercentage = Column(Float(53), primary_key = False, autoincrement = False, nullable = True)
	
	#产品定义ID:
	ProductRuleID =Column(Integer, nullable=False, primary_key=False)

	#工艺段ID:
	PUID =Column(Integer, nullable=False, primary_key=False)

	#物料类型ID:
	MATTypeID =Column(Integer, nullable=False, primary_key=False)

	#顺序号:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#等级:
	Grade = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class MaterialBOMWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allMaterialBOMsCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.MaterialBOM(
						MATID=odata['MATID'],
						BatchTotalWeight=odata['BatchTotalWeight'],
						BatchSingleMATWeight=odata['BatchSingleMATWeight'],
						Unit=odata['Unit'],
						BatchPercentage=odata['BatchPercentage'],
						ProductRuleID=odata['ProductRuleID'],
						PUID=odata['PUID'],
						MATTypeID=odata['MATTypeID'],
						Seq=odata['Seq'],
						Grade=odata['Grade']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialBOMsDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					MaterialBOMid = int(key)
					try:
						oclass = session.query(Model.core.MaterialBOM).filter_by(ID=MaterialBOMid).first()
						session.delete(oclass)
						session.commit()
					except Exception as ee:
						print(ee)
						return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
												  ensure_ascii=False)
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def MaterialBOMsFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.MaterialBOM.ID)).scalar()
				qDatas = session.query(Model.core.MaterialBOM).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.MaterialBOM).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialBOMsUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				MaterialBOMid = int(odata['ID'])
				oclass = session.query(Model.core.MaterialBOM).filter_by(ID=MaterialBOMid).first()
				oclass.MATID = odata['MATID']
				oclass.BatchTotalWeight = odata['BatchTotalWeight']
				oclass.BatchSingleMATWeight = odata['BatchSingleMATWeight']
				oclass.Unit = odata['Unit']
				oclass.BatchPercentage = odata['BatchPercentage']
				oclass.ProductRuleID = odata['ProductRuleID']
				oclass.PUID = odata['PUID']
				oclass.MATTypeID = odata['MATTypeID']
				oclass.Seq = odata['Seq']
				oclass.Grade = odata['Grade']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allMaterialBOMsSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				MaterialBOMscount = session.query(Model.core.MaterialBOM).filter(
							MaterialBOM.MATID.like(strconditon)).all()
				total = Counter(MaterialBOMscount)
				jsonMaterialBOMs = json.dumps(MaterialBOMscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonMaterialBOMs = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonMaterialBOMs + "}"
				return jsonMaterialBOMs
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#ProductUnitRoute:
class ProductUnitRoute(Base):
	__tablename__ = "ProductUnitRoute" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = True)
	
	#工艺路线编码:
	PDUnitRouteCode =Column(Unicode(64), nullable=False, primary_key=False)

	#工艺路线名称:
	PDUnitRouteName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)

	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#持续时间:
	Duration = Column(Integer, primary_key = False, autoincrement = False, nullable = True)
	
	#单位:
	Unit = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)
	
	#产品定义ID:
	ProductRuleID =Column(Integer, nullable=False, primary_key=False)

	#工艺段ID:
	PUID =Column(Integer, nullable=False, primary_key=False)

	#顺序号:
	Seq = Column(Integer, primary_key = False, autoincrement = False, nullable = True)

class ProductUnitRouteWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allProductUnitRoutesCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.ProductUnitRoute(
						PDUnitRouteCode=odata['PDUnitRouteCode'],
						PDUnitRouteName=odata['PDUnitRouteName'],
						Desc=odata['Desc'],
						Duration=odata['Duration'],
						Unit=odata['Unit'],
						ProductRuleID=odata['ProductRuleID'],
						PUID=odata['PUID'],
						Seq=odata['Seq']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductUnitRoutesDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					ProductUnitRouteid = int(key)
					try:
						oclass = session.query(Model.core.ProductUnitRoute).filter_by(ID=ProductUnitRouteid).first()
						session.delete(oclass)
						session.commit()
					except Exception as ee:
						print(ee)
						return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
												  ensure_ascii=False)
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def ProductUnitRoutesFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.ProductUnitRoute.ID)).scalar()
				qDatas = session.query(Model.core.ProductUnitRoute).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.ProductUnitRoute).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductUnitRoutesUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				ProductUnitRouteid = int(odata['ID'])
				oclass = session.query(Model.core.ProductUnitRoute).filter_by(ID=ProductUnitRouteid).first()
				oclass.PDUnitRouteCode = odata['PDUnitRouteCode']
				oclass.PDUnitRouteName = odata['PDUnitRouteName']
				oclass.Desc = odata['Desc']
				oclass.Duration = odata['Duration']
				oclass.Unit = odata['Unit']
				oclass.ProductRuleID = odata['ProductRuleID']
				oclass.PUID = odata['PUID']
				oclass.Seq = odata['Seq']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allProductUnitRoutesSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				ProductUnitRoutescount = session.query(Model.core.ProductUnitRoute).filter(
							ProductUnitRoute.PDUnitRouteName.like(strconditon)).all()
				total = Counter(ProductUnitRoutescount)
				jsonProductUnitRoutes = json.dumps(ProductUnitRoutescount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonProductUnitRoutes = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonProductUnitRoutes + "}"
				return jsonProductUnitRoutes
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
	
#SchedulePlan:
class SchedulePlan(Base):
	__tablename__ = "SchedulePlan" 
	
	#ID:
	ID = Column(BigInteger, primary_key = True, autoincrement = True, nullable = True)
	
	#调度编号:
	SchedulePlanCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#调度计划开始时间:
	PlanBeginTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#调度计划结束时间:
	PlanEndTime = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)
	
	#调度类型:
	Type = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)

class SchedulePlanWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allSchedulePlansCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.SchedulePlan(
						SchedulePlanCode=odata['SchedulePlanCode'],
						Desc=odata['Desc'],
						PlanBeginTime=odata['PlanBeginTime'],
						PlanEndTime=odata['PlanEndTime'],
						Type=odata['Type']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allSchedulePlansDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					SchedulePlanid = int(key)
					try:
						oclass = session.query(Model.core.SchedulePlan).filter_by(ID=SchedulePlanid).first()
						session.delete(oclass)
						session.commit()
					except Exception as ee:
						print(ee)
						return json.dumps([{"status": "error:" + str(ee)}], cls=Model.BSFramwork.AlchemyEncoder,
												  ensure_ascii=False)
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def SchedulePlansFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.SchedulePlan.ID)).scalar()
				qDatas = session.query(Model.core.SchedulePlan).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.SchedulePlan).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allSchedulePlansUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				SchedulePlanid = int(odata['ID'])
				oclass = session.query(Model.core.SchedulePlan).filter_by(ID=SchedulePlanid).first()
				oclass.SchedulePlanCode = odata['SchedulePlanCode']
				oclass.Desc = odata['Desc']
				oclass.PlanBeginTime = odata['PlanBeginTime']
				oclass.PlanEndTime = odata['PlanEndTime']
				oclass.Type = odata['Type']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allSchedulePlansSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				SchedulePlanscount = session.query(Model.core.SchedulePlan).filter(
							SchedulePlan.SchedulePlanCode.like(strconditon)).all()
				total = Counter(SchedulePlanscount)
				jsonSchedulePlans = json.dumps(SchedulePlanscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonSchedulePlans = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonSchedulePlans + "}"
				return jsonSchedulePlans
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

class PlanManager(Base):
	__tablename__ = "PlanManager"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)

	# 调度编号:
	SchedulePlanCode = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

	# 批次号:
	BatchID = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 计划重量:
	PlanQuantity = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 单位:
	Unit = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 品名ID:
	BrandID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 品名:
	BrandName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 计划状态:
	PlanStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 调度计划开始时间:
	PlanBeginTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

	# 计划完成时间:
	PlanEndTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

	# 调度类型:
	Type = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# # 序号:
	# Seq = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# PLineID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)
    #
	# PLineName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

class PlanManagerWebIFS(object):
	def __init__(self, name):
		self.name = name

	def allPlanManagersCreate(self, rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.PlanManager(
						SchedulePlanCode=odata['SchedulePlanCode'],
						BatchID=odata['BatchID'],
						BrandID=int(odata['BrandID']),
						BrandName=odata['BrandName'],
						PlanQuantity=int(odata['PlanQuantity']),
						Unit=odata['Unit'],
						# Seq=int(odata['Seq']),
						PlanBeginTime=odata['PlanBeginTime'],#datetime.datetime.strptime(odata['PlanBeginTime'],'%Y-%m-%d %H:%M'),
						PlanEndTime = odata['PlanEndTime'],#datetime.datetime.strptime(odata['PlanEndTime'],'%Y-%m-%d %H:%M'),
						PlanStatus = Model.Global.PlanStatus.NEW.value,
						Type = odata['Type']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK],
								  cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
							  ensure_ascii=False)

	def allPlanManagersDelete(self, rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					PlanManagerid = int(key)
					try:
						oclass = session.query(Model.core.PlanManager).filter_by(ID=PlanManagerid).first()
						oclassW = session.query(WorkFlowStatus).filter_by(PlanManageID=PlanManagerid).first()
						session.delete(oclassW)
						session.delete(oclass)
						oclassFs = session.query(WorkFlowEventPlan).filter_by(PlanManageID=PlanManagerid).all()
						for oclassF in oclassFs:
							session.delete(oclassF)
						zYPlans = session.query(ZYPlan).filter_by(BatchID=oclass.BatchID).all()
						zYTasks = session.query(ZYTask).filter_by(BatchID=oclass.BatchID).all()
						for zYPlan in zYPlans:
							session.delete(zYPlan)
						for zYTask in zYTasks:
							session.delete(oclass)
						session.commit()
					except Exception as ee:
						session.rollback()
						print(ee)
						logger.error(ee)
						return json.dumps([{"status": "error:" + str(ee)}],
										  cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK],
								  cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
							  ensure_ascii=False)

	def PlanManagersFind(self, rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.PlanManager.ID)).scalar()
				qDatas = session.query(Model.core.PlanManager).order_by(desc("ID")).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.PlanManager).order_by(desc("ID")).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas, cls=Model.BSFramwork.AlchemyEncoder,
												  ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
						total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
							  ensure_ascii=False)

	def allPlanManagersUpdate(self, rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				PlanManagerid = int(odata['ID'])
				oclass = session.query(Model.core.PlanManager).filter_by(ID=PlanManagerid).first()
				oclass.SchedulePlanCode = odata['SchedulePlanCode']
				oclass.BatchID = odata['BatchID']
				oclass.BrandID = odata['BrandID']
				oclass.BrandName = odata['BrandName']
				oclass.PlanQuantity = odata['PlanQuantity']
				oclass.Unit = odata['Unit']
				# oclass.Seq = odata['Seq']
				oclass.PlanBeginTime = odata['PlanBeginTime']
				oclass.PlanEndTime = odata['PlanEndTime']
				oclass.Type = odata['Type']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK],
								  cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
							  ensure_ascii=False)

	def allPlanManagersSearch(self, rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['BatchID'] + "%"
				PlanManagerscount = session.query(Model.core.PlanManager).filter(
					PlanManager.BatchID.like(strconditon)).order_by(desc("PlanBeginTime")).all()
				total = Counter(PlanManagerscount)
				jsonPlanManagers = json.dumps(PlanManagerscount, cls=Model.BSFramwork.AlchemyEncoder,
											   ensure_ascii=False)
				jsonPlanManagers = '{"total"' + ":" + str(
					total.__len__()) + ',"rows"' + ":\n" + jsonPlanManagers + "}"
				return jsonPlanManagers
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
							  ensure_ascii=False)
	
#Unit:
class Unit(Base):
	__tablename__ = "Unit" 
	
	#ID:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = True)
	
	#单位编码:
	UnitCode = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#单位名称:
	UnitName = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)
	
	#描述:
	Desc = Column(Unicode(64), primary_key = False, autoincrement = False, nullable = True)

class UnitWebIFS(object):
	def __init__(self, name):
		self.name = name
	def allUnitsCreate(self,rcvdata):
		try:
			odata = rcvdata
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				session.add(
					Model.core.Unit(
						UnitCode=odata['UnitCode'],
						UnitName=odata['UnitName'],
						Desc=odata['Desc']))
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
								  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allUnitsDelete(self,rcvdata):
		odata = rcvdata
		try:
			jsonstr = json.dumps(odata.to_dict())
			if len(jsonstr) > 10:
				jsonnumber = re.findall(r"\d+\.?\d*", jsonstr)
				for key in jsonnumber:
					# for subkey in list(key):
					Unitid = int(key)
					try:
						oclass = session.query(Model.core.Unit).filter_by(ID=Unitid).first()
						session.delete(oclass)
						session.commit()
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
					# return json.dumps([{"status": "Error"+ string(e)}], cls=AlchemyEncoder, ensure_ascii=False)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def UnitsFind(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			print(json_str)
			if len(json_str) > 10:
				pages = int(odata['page'])
				rowsnumber = int(odata['rows'])
				inipage = (pages - 1) * rowsnumber + 0
				endpage = (pages - 1) * rowsnumber + rowsnumber
				total = session.query(func.count(Model.core.Unit.ID)).scalar()
				qDatas = session.query(Model.core.Unit).all()[inipage:endpage]
				if total > 0:
					qDatas = session.query(Model.core.Unit).all()[inipage:endpage]
					# ORM模型转换json格式
					jsonorganzitions = json.dumps(qDatas,cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
					jsonorganzitions = '{"total"' + ":" + str(
								total) + ',"rows"' + ":\n" + jsonorganzitions + "}"
					return jsonorganzitions
				else:
					return ""
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allUnitsUpdate(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 10:
				Unitid = int(odata['ID'])
				oclass = session.query(Model.core.Unit).filter_by(ID=Unitid).first()
				oclass.UnitCode = odata['UnitCode']
				oclass.UnitName = odata['UnitName']
				oclass.Desc = odata['Desc']
				session.commit()
				return json.dumps([Model.Global.GLOBAL_JSON_RETURN_OK], cls=Model.BSFramwork.AlchemyEncoder,
										  ensure_ascii=False)
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error:" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allUnitsSearch(self,rcvdata):
		odata = rcvdata
		try:
			json_str = json.dumps(odata.to_dict())
			if len(json_str) > 2:
				strconditon = "%" + odata['condition'] + "%"
				Unitscount = session.query(Model.core.Unit).filter(
							Unit.UnitCode.like(strconditon)).all()
				total = Counter(Unitscount)
				jsonUnits = json.dumps(Unitscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
				jsonUnits = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonUnits + "}"
				return jsonUnits
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)

	def allUnitsSearchByCondition(self,condition):
		try:
			strconditon = "%" + condition + "%"
			Unitscount = session.query(Model.core.Unit).filter(
				Unit.UnitCode.like(strconditon)).all()
			total = Counter(Unitscount)
			jsonUnits = json.dumps(Unitscount, cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)
			jsonUnits = '{"total"' + ":" + str(total.__len__()) + ',"rows"' + ":\n" + jsonUnits + "}"
			return jsonUnits
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
							  ensure_ascii=False)

	def getUnitByCondition(self,condition):
		sz = []
		strcondition = "%" + condition + "%"
		strSelected = "true"
		try:
			objs = session.query(Model.core.Unit).filter(
				Unit.UnitCode.like(strcondition)).all()
			for obj in objs:
				sz.append({"ID": obj.ID, "text": obj.UnitCode,"selected":strSelected})
			# data = string(sz)"'"
			# data.replace(srep, '')
			return sz
		except Exception as e:
			print(e)
			logger.error(e)
			return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder, ensure_ascii=False)


# TaskNoGenerator:
class TaskNoGenerator(Base):
	__tablename__ = "TaskNoGenerator"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)

	# 单位编码:
	TaskNoInt = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 单位名称:
	TaskNoVar = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 描述:
	Desc = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

class SysLog(Base):
	__tablename__ = "SysLog"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)

	# IP:
	IP = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 计算机名称:
	ComputerName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 操作用户:
	UserName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

	# 操作日期:
	OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

	# 操作内容:
	OperationContent = Column(Unicode(2048), primary_key=False, autoincrement=False, nullable=True)

	# 类型:
	OperationType = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)


# 服务配置
class ServerConfig(Base):
    __tablename__ = 'ServerConfig'

    # ID
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 服务配置名称
    ServerConfigName = Column(Unicode(30), nullable=True)

    # IP地址
    IP = Column(Unicode(30), nullable=True)

    # 端口
    Port = Column(Unicode(20), nullable=True)

    # auth_key
    AuthKey = Column(Unicode(100), nullable=True)

# Opc服务
class OpcServer(Base):
	__tablename__ = 'OpcServer'

	# ID
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# 服务名称
	ServerName = Column(Unicode(30), nullable=True)

	# 资源地址
	URI = Column(Unicode(30), nullable=True)

	# 描述
	Desc = Column(Unicode(100), nullable=True)


# OpcTag配置表
class OpcTag(Base):
	__tablename__ = 'OpcTag'

	# ID
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# OpcServerID
	OpcServerID = Column(Integer, nullable=True)

	# NodeID
	NodeID = Column(Unicode(200), nullable=True)

	# 名称
	DisplayName = Column(Unicode(200), nullable=True)

	# 注释
	Note = Column(Unicode(100), nullable=True)

	# 父节点
	ParentID = Column(Unicode(200), nullable=True)

	# 备注
	Desc = Column(Unicode(100), nullable=True)


class CollectParamsTemplate(Base):
	__tablename__ = 'CollectParamsTemplate'

	# ID
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	#模板名称
	TemplateName = Column(Unicode(32), nullable=True)

	# 描述信息
	Desc = Column(Unicode(100), nullable=True)


class CollectParams(Base):
	__tablename__ = 'CollectParams'

	#ID
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# CollectParamsTemplateID
	CollectParamsTemplateID = Column(Integer, nullable=True)

	# OpcTagID
	OpcTagID = Column(Integer, nullable=True)

	# 描述
	Desc = Column(Unicode(100), nullable=True)


class Collectionstrategy(Base):
	__tablename__ = 'Collectionstrategy'

	# ID
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# 间隔时间
	Interval = Column(Integer, nullable=True)

	# NodeID
	NodeID = Column(Unicode(200), nullable=True)

	# 策略名称
	StrategyName = Column(Unicode(30), nullable=True)

	# 描述
	Desc = Column(Unicode(100), nullable=True)

class CollectTask(Base):
    __tablename__ = 'CollecTask'
    #ID
    ID = Column(Integer,primary_key=True,autoincrement=True,nullable=False)

    #采集任务名称
    CollectTaskName = Column(Unicode(32),nullable=True)

    #存放采集数据的表名
    TableName = Column(Unicode(32),nullable=True)

    #全局策略
    GlobalStrategyID = Column(Integer,nullable=True)

    #是否启用
    Enabled = Column(Boolean,default=False,nullable=False)

    #描述
    Desc = Column(Unicode(100),nullable=True)


class CollectTaskCollection(Base):
	__tablename__ = 'CollectTaskCollection'

	#ID
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# 采集参数模板ID
	CollectParamsTemplateID = Column(Integer, nullable=True)

	# 采集参数模板名称
	TemplateName = Column(Unicode(32), nullable=True)

	# 采集策略ID
	CollectionStrategyID = Column(Integer, nullable=True)

	# 策略名称
	StrategyName = Column(Unicode(30), nullable=True)

	#采集任务ID
	CollectTaskID = Column(Integer, nullable=True)

	# 采集任务名称
	CollectTaskName = Column(Unicode(32), nullable=True)

	# 描述
	Desc = Column(Unicode(100), nullable=True)

# 用于在MES存储调度计划事件信息:
class WorkFlowEventPlan(Base):
	__tablename__ = "WorkFlowEventPlan"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# PlanManage表ID:
	PlanManageID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 用户名:
	userName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 描述:
	Desc = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

	# 事件类型:
	Type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 事件发生的时间:
	EventTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 用于在MES存储调度计划事件信息:
class WorkFlowEventZYPlan(Base):
	__tablename__ = "WorkFlowEventZYPlan"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# ZYPlan表ID:
	ZYPlanID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 用户名:
	userName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 描述:
	Desc = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

	# 事件类型:
	Type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 事件发生的时间:
	EventTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 用于在MES流程流转表:
class WorkFlowStatus(Base):
	__tablename__ = "WorkFlowStatus"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# PlanManage表ID:
	PlanManageID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# ZYPlan表ID:
	ZYPlanID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# ZYTask表ID:
	ZYTaskID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 审核状态:
	AuditStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 描述:
	Desc = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

# 准备工作表:
class ReadyWork(Base):
	__tablename__ = "ReadyWork"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# ZYPlan表ID:
	ZYPlanID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 准备项名称
	ReadyName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# 是否检查合格
	IsCheck = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	#描述
	Describe = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	#生产前生产后的标识0代表生产前，1代表生产后
	ProductionFlag = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

	# #检查工作区域是否有《清场合格证》
	# ClearFieldCard = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    #
	# #是否清除工作区域、设备上的上一批次的物料或产品
	# ClearLastMateriel = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    #
	# #检查是否已经清除上一批次物料的状态标志
	# ClearLastMaterielStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    #
	# #检查生产设备、生产现场是否完好清洁
	# ClaernEquipLocal = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    #
	# #是否清除生产现场与本批产品无关的文件
	# ClarnFile = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    #
	# #检查设备、电器件、介质是否正常处于安全状态
	# SafetyStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# nodeId_note
class NodeIdNote(Base):
	__tablename__ = 'NodeIdNote'

	#ID
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# NodeID
	NodeID = Column(Unicode(32), nullable=True)

	# Note
	Note = Column(Unicode(32), nullable=True)

# all = session.query(OpcTag).all()
# print(all)
# for oclass in all:
# 	session.delete(oclass)
# 	session.commit()
# 生成表单的执行语句
Base.metadata.create_all(engine)



