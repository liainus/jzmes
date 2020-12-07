
#/******************************************************************************************
# ************* STK make model usage:
# ************* version: print python3.6.3  version
# ************* make: make Python file
# ************* STK makemodel.py 1.0.0
# ************* @author Xujin
# ************* @date 2017-12-21 23:08:22
# ************* @Model 
# ******************************************************************************************/


#引入必要的类库
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy import create_engine, \
    Column, ForeignKey, Table, DateTime, Integer, String, BigInteger, Time
from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode, Boolean
from sqlalchemy.dialects.mssql.base import BIT
from werkzeug.security import generate_password_hash, check_password_hash
import Model.Global
from datetime import datetime
from flask_login import UserMixin,LoginManager


login_manager = LoginManager()
#引入mssql数据库引擎
import pymssql


# 创建对象的基类
engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session= Session()
Base = declarative_base(engine)
#引入mssql数据库引擎
import pymssql

class SapBatchInfo(Base):
    '''
    SAP工单信息（批次计划信息）
    '''
    __tablename__ = 'SapBatchInfo'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # MES请求唯一编码:
    RID = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 订单号 :
    AUFNR = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 订单类型:
    DAUAT = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工厂
    DWERK = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 批次编号:
    CHARG = Column(Unicode(60), primary_key=False, autoincrement=False, nullable=True)

    # 产品编码:
    MATNR = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 产品名称:
    MAKTX = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 计划生产数量:
    GAMNG = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 单位:
    UNIT = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 生产版本:
    VERID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 预留编号 :
    RSNUM = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺路线编号:
    ROUTN = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 计划开始日期
    GSTRP = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 计划结束日期:
    GLTRP = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 状态 :
    STATE = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 配方组 :
    PLNNR = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 配方组计数器:
    PLNAL = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 配方描述:
    KTEXT = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 取样量
    GESSTICHPR = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 检验依据:
    QBASE = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)



class SapBrandUnitInfo(Base):
    '''
    SAP流程订单工序信息（工艺段信息及报工接口信息）
    '''
    __tablename__ = 'SapBrandUnitInfo'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # MES请求唯一编码:
    RID = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 订单号 :
    AUFNR = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺路线编号:
    ROUTN = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 操作/活动编号
    VORNR = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 工序短文本 :
    LTXA1 = Column(Unicode(60), primary_key=False, autoincrement=False, nullable=True)

    # 工序数量:
    MGVRG = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工序单位:
    UNIT = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 控制码:
    STEUS = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 标准值码:
    VORGSCHL = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 工时1:
    VGW01 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工时2 :
    VGW02 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工时3:
    VGW03 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工时4
    VGW04 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工时5
    VGW05 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工时6 :
    VGW06 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 过账日期 :
    BUDAT = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 实际开始日期
    ActStartTime = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 实际结束时间 :
    ActFinishTime = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 取样量
    NUM1 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 批数量
    QTY = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 请验日期:
    QDATE = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 生产日期
    HSDAT = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 差异原因
    AGRND = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 废品
    SCRAP = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 报工产量
    PRQTY = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 确认类型
    FCONF = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)



class SapMatailInfo(Base):
    '''
    SAP流程订单物料信息（批次物料信息）
    '''
    __tablename__ = 'SapMatailInfo'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # MES请求唯一编码:
    RID = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 订单号 :
    AUFNR  = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 预留编号:
    RSNUM = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 预留项目号
    RSPOS = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 阶段 :
    VORNR = Column(Unicode(60), primary_key=False, autoincrement=False, nullable=True)

    # 次序:
    SEQNO = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 物料编号:
    MATNR = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 物料描述:
    MAKTX = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 物料数量:
    BDMNG = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 物料单位:
    MEINS = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 移动类型 :
    BWART = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 批次编号:
    CHARG = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工厂
    WERKS = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 存储地点
    LGORT = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 称量标记 :
    WEIGH = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

# 生成表单的执行语句
Base.metadata.create_all(engine)

