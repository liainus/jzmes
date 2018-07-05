
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

from sqlalchemy import (Column, Integer, String,
                        DateTime, ForeignKey)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import Model.Global

# 创建对象的基类
engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base(engine)


#引入mssql数据库引擎
import pymssql
class Handler(Base):
    __tablename__= 'permission_handler'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    p_id = Column(Integer, ForeignKey("permission_permission.id"))

    permission = relationship("Permission", uselist=False)

    @classmethod
    def all(cls):
        return session.query(cls).all()

    @classmethod
    def by_id(cls, id):
        return session.query(cls).filter_by(id=id).first()

    @classmethod
    def by_uuid(cls, uuid):
        return session.query(cls).filter_by(uuid=uuid).first()

    @classmethod
    def by_name(cls, name):
        return session.query(cls).filter_by(name=name).first()

'''模块菜单'''
class Menu(Base):
    __tablename__='permission_menu'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    p_id = Column(Integer, ForeignKey("permission_permission.id"))

    permission = relationship("Permission", uselist=False) #要赋值一个Permission类的对象

    @classmethod
    def all(cls):
        return session.query(cls).all()

    @classmethod
    def by_id(cls, id):
        return session.query(cls).filter_by(id=id).first()

    @classmethod
    def by_uuid(cls, uuid):
        return session.query(cls).filter_by(uuid=uuid).first()

    @classmethod
    def by_name(cls, name):
        return session.query(cls).filter_by(name=name).first()


class PermissionToRole(Base):
    """权限角色多对多关系表"""
    __tablename__='permission_to_role'
    p_id = Column(Integer,ForeignKey("permission_permission.id"), primary_key=True)
    r_id = Column(Integer,ForeignKey("Role.ID"), primary_key=True)


class Permission(Base):
    """权限表"""
    __tablename__ = 'permission_permission'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    strcode = Column(String(50), nullable=False) #权限码

    roles = relationship("Role", secondary=PermissionToRole.__table__)

    menu = relationship("Menu", uselist=False)

    handler = relationship("Handler", uselist=False)


    @classmethod
    def all(cls):
        return session.query(cls).all()

    @classmethod
    def by_id(cls, id):
        return session.query(cls).filter_by(id=id).first()

    @classmethod
    def by_uuid(cls, uuid):
        return session.query(cls).filter_by(uuid=uuid).first()

    @classmethod
    def by_name(cls, name):
        return session.query(cls).filter_by(name=name).first()



class UserToRole(Base):
    """用户角色多对多关系表"""
    __tablename__="permission_user_to_role"
    user_id = Column(Integer,ForeignKey("User.ID"), primary_key=True)
    role_id = Column(Integer,ForeignKey("permission_role.id"), primary_key=True)

#用户表
class User(Base):
    __tablename__ = 'User'
    #ID
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    #用户名
    UserName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)
    #登录账号
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


    roles = relationship("Role", secondary=UserToRole.__table__)

    def __repr__(self):
        return 'id:{},user_name:{},job_number:{},_password:{},email:{},tel:{},create_time:{}'.format(
            self.id,
            self.user_name,
            self.job_number,
            self.password,
            self.email,
            self.tel,
            self.create_time,
        )

    @classmethod
    def all(cls):
        return session.query(cls).all()
    @classmethod
    def uuid(cls, uuid):
        return session.query(cls).filter_by(uuid=uuid).first()
    @classmethod
    def by_email(cls, email):
        return session.query(cls).filter_by(email=email).first()
    def by_name(cls, name):
        return session.query(cls).filter_by(user_name=name).first()

    # 密码哈希加密
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(Base):
    __tablename__ = "Role"

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

    # 用户与角色关系
    users = relationship('User', secondary=UserToRole.__table__)

    # 角色与权限关系
    permission = relationship('Permission', secondary=PermissionToRole.__table__)



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