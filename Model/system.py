
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
    Column,ForeignKey, Table, DateTime, Integer, String
from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode
from sqlalchemy.dialects.mssql.base import BIT
import Model.Global
from datetime import datetime


#引入mssql数据库引擎
import pymssql


# 创建对象的基类
engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base(engine)


#引入mssql数据库引擎
import pymssql

# 用户与菜单关联表
User_Menu = Table(
    "user_menu",
    Base.metadata,
    Column("User_ID", Integer, ForeignKey("user.ID"), nullable=False, primary_key=True),
    Column("Menu_ID", Integer, ForeignKey("menu.ID"), nullable=False, primary_key=True)
)

# 菜单与权限关联表
Permission_Menu = Table(
    "permission_menu",
    Base.metadata,
    Column("Permission_ID", Integer, ForeignKey("permission.Per_ID"), nullable=False, primary_key=True),
    Column("Menu_ID", Integer, ForeignKey("menu.ID"), nullable=False, primary_key=True)
)


# 模块菜单表
class Menu(Base):
    __tablename__ = 'menu'
    # 模块ID
    ID = Column(Integer, primary_key=True, autoincrement=True)

    # 模块名称
    ModuleName = Column(String(60), nullable=False)

    # 模块编码
    ModuleCode = Column(String(100),nullable=False)

    # 模块路由
    Url = Column(String(100), nullable=True)

    # 描述
    Description = Column(String(1024), nullable=True)

    # 创建时间
    CreateDate = Column(DateTime, default=datetime.now, nullable=True)

    # 创建人
    Creator = Column(String(50), nullable=True)

    # 父节点
    ParentNode = Column(Integer, nullable=True)

    # 开放与关闭状态
    state = Column(String(20), nullable=False)

    # 与用户建立多对多
    Users = relationship("User", secondary=User_Menu)

    # 与权限建立多对多
    Permissions = relationship("Permission", secondary=Permission_Menu)

    def __repr__(self):
        return "<Menu ID='%s' ModuleName='%s' ModuleCode=%s Url=%s ParentNode=%s>" % (self.ID, self.ModuleName, self.ModuleCode, self.Url, self.Permission)


# 权限与角色关联表
Permission_User = Table(
    "permission_user",
    Base.metadata,
    Column("Permission_ID", Integer, ForeignKey("permission.Per_ID"), nullable=False, primary_key=True),
    Column("User_ID", Integer, ForeignKey("user.ID"), nullable=False, primary_key=True)
)


# 权限表
class Permission(Base):
    __tablename__ = 'permission'
    # ID
    Per_ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 权限名称
    Per_Name = Column(String(100), nullable=False)

    # 创建时间
    CreateData = Column(DateTime, default=datetime.now)

    # 创建人
    Creator = Column(String(50), nullable=True)

    # 查询角色
    users = relationship("User", secondary=Permission_User)

    # 查询菜单
    menus = relationship('Menu', secondary=Permission_Menu)

    def __repr__(self):
        return "<Permission ID='%s' Per_Name='%s'>" % (self.ID, self.RoleName)

# 角色与用户关联表
user_role = Table(
    "user_role",
    Base.metadata,
    Column("User_ID", Integer, ForeignKey("user.ID"), nullable=False, primary_key=True),
    Column("Role_ID", Integer, ForeignKey("role.ID"), nullable=False, primary_key=True)
)

# 角色表
class Role(Base):
    __tablename__ = 'role'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 角色编码:
    RoleCode = Column(String(100), primary_key=False, autoincrement=False, nullable=True)

    # 角色顺序:
    RoleSeq = Column(String(10), primary_key=False, autoincrement=False, nullable=True)

    # 角色名称:
    RoleName = Column(String(200), primary_key=False, autoincrement=False, nullable=True)

    # 角色说明:
    Description = Column(String(2048), primary_key=False, autoincrement=False, nullable=True)

    # 创建人:
    CreatePerson = Column(String(20), primary_key=False, autoincrement=False, nullable=True)

    # 创建时间:
    CreateDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 父节点
    ParentNode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 查询用户
    users = relationship("User", secondary=user_role)

    def __repr__(self):
        return "<Role ID='%s' RoleName='%s' RoleCode=%s>" % (self.ID, self.RoleName, self.RoleCode)

# 用户表
class User(Base):
    __tablename__ = 'user'

    # ID
    ID = Column(Integer, primary_key=True, autoincrement=True)

    # 用户名
    Name = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 密码
    Password = Column(String(128), nullable=False)

    # 登录名
    LoginName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    #登录状态
    Status = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    #创建用户
    Creater = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    #创建时间
    CreateTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    #上次登录时间
    LastLoginTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    #是否锁定
    IsLock = Column(BIT, primary_key=False, autoincrement=False, nullable=True)

    #所属部门
    OrganizationName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 查询角色
    roles = relationship("Role", secondary=user_role)

    # 查询菜单
    menu = relationship("Menu", secondary=User_Menu)

    # 查询权限
    permissions = relationship("Permission", secondary=Permission_User)

    def __repr__(self):
        return "<User ID='%s' Name='%s'>" % (self.ID, self.Name)


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

    # 显示图标:
    Img = Column(Unicode(40), primary_key=False, autoincrement=False, nullable=True)

    # 显示图标:
    Color = Column(Unicode(40), primary_key=False, autoincrement=False, nullable=True)




# 生成表单的执行语句
Base.metadata.create_all(engine)

