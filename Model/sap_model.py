
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
    RID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

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



class SapBatchInfo(Base):
    '''
    SAP工单信息（批次计划信息）
    '''
    __tablename__ = 'SapBatchInfo'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # MES请求唯一编码:
    RID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

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


# 生成表单的执行语句
Base.metadata.create_all(engine)

