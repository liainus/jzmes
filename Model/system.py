
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
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Column,ForeignKey, Table, DateTime, Integer, String
from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode
from sqlalchemy.dialects.mssql.base import BIT
import Model.Global



#引入mssql数据库引擎
import pymssql

# 创建对象的基类
engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base(engine)
#Role:
class Role(Base):
	__tablename__ = "Role"

	#id:
	ID = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
	
	#角色编码:
	RoleCode = Column(String(100), primary_key = False, autoincrement = False, nullable = True)
	
	#角色顺序:
	RoleSeq = Column(String(10) , primary_key = False, autoincrement = False, nullable = True)
	
	#角色名称:
	RoleName = Column(String(200) , primary_key = False, autoincrement = False, nullable = True)
	
	#角色说明:
	Description = Column(String(2048) , primary_key = False, autoincrement = False, nullable = True)
	
	#创建人:
	CreatePerson = Column(String(20) , primary_key = False, autoincrement = False, nullable = True)
	
	#创建时间:
	CreateDate = Column(DateTime, primary_key = False, autoincrement = False, nullable = True)





# 生成表单的执行语句
# Base.metadata.create_all(engine)
# import json
# UnReadMsg = session.query(Role).all()
# print (UnReadMsg[0].RoleName.encode('utf-8').decode('utf-8'))


# Organization:
class Organization(Base):
	__tablename__ = "Organization"

	# ID:
	ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

	# 组织结构编码:
	OrganizationCode = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

	# 父组织机构:
	ParentNode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

	# 顺序号:
	OrganizationSeq = Column(Unicode(10), primary_key=False, autoincrement=False, nullable=True)

	# 组织机构名称:
	OrganizationName = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

	# 说明:
	Description = Column(Unicode(2048), primary_key=False, autoincrement=False, nullable=True)

	# 创建人:
	CreatePerson = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

	# 创建时间:
	CreateDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=False)

    #显示图标:
	Img = Column(Unicode(40), primary_key=False, autoincrement=False, nullable=True)

#显示图标:
	Color = Column(Unicode(40), primary_key=False, autoincrement=False, nullable=True)

# 生成表单的执行语句
Base.metadata.create_all(engine)