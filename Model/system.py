
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


# # 模块菜单表
# class ModuleMenu(Base):
#     __tablename__ = 'ModuleMenu'
#     # 菜单ID
#     ID = Column(Integer, primary_key=True, autoincrement=True)
#     # 菜单名称
#     ModuleName = Column(String(60), nullable=False)
#     # 模块编码
#     ModuleCode = Column(String(100),nullable=False)
#     # 模块路由
#     Url = Column(String(100), nullable=True)
#     # 描述
#     Description = Column(String(1024), nullable=True)
#     # 创建时间
#     CreateDate = Column(DateTime, default=datetime.now, nullable=True)
#     # 创建人
#     Creator = Column(String(50), nullable=True)
    # # 权限ID
    # Permission_ID = relationship(Integer, ForeignKey('Permission.Per_ID'))
    # # 与权限建立一对一关系
    # Permission = relationship("Permission", uselist=False, back_populates="Permission")


# # 角色与权限多对多关联表
# Permission_Role = Table('Permission_Role',Base.metadata,
#         Column('Permission_ID',Integer, ForeignKey('Permission.Per_ID'), nullable=False, primary_key=True),
#         Column('Role_ID',Integer, ForeignKey('Role.ID'), nullable=False, primary_key=True)
# )

# 权限表
# class Permission(Base):
#     __tablename__ = 'Permission'
#     # ID
#     Per_ID = Column(Integer, primary_key=True, autoincrement=True)
#     # 权限名称
#     Per_Name = Column(String(100),nullable=False)
#     # 创建时间
#     CreateData = Column(DateTime, default=datetime.now)
#     # 创建人
#     Creator = Column(String(50),nullable=True)
    # # 与菜单建立一对一关系
    # Menu = relationship("Menu", back_populates="Menu")
    # 查询角色
    # Role = relationship('Role', secondary=Permission_Role)

# # 用户与角色关联表
# User_Role = Table('User_Role',Base.metadata,
#         Column('User_ID',Integer,ForeignKey('User.ID'),nullable=False, primary_key=True),
#         Column('Role_ID',Integer,ForeignKey('Role.ID'),nullable=False, primary_key=True)
# )




    # Roles = relationship('Role', secondary=User_Role)
    #
    # # 将password字段定义为User类的一个属性，其中设置该属性不可读，若读取抛出AttributeError。
    # @property
    # def password(self):
    #     raise AttributeError('password cannot be read')
    #
    # # 定义password字段的写方法，我们调用generate_password_hash将明文密码password转成密文Shadow
    # @password.setter
    # def password(self, password):
    #     self.Shadow = generate_password_hash(password)
    #
    # # 定义验证密码的函数confirm_password
    # def confirm_password(self, password):
    #     return check_password_hash(self.Shadow, password)
    #
    # def __repr__(self):
    #     return '<User %r>' % self.userName



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
    # 查询用户
    # Users = relationship('User', secondary=User_Role)


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

#用户表
class User(Base):
    __tablename__ = 'User'
    #ID
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 用户名
    UserName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)
    # 登录账号
    LoginName = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)
    # 登录状态
    Status = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 创建用户
    Creater = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)
    # 创建时间
    CreateTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 上次登录时间
    LastLoginTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 是否锁定
    IsLock = Column(BIT, primary_key=False, autoincrement=False, nullable=True)
    # 所属组织
    OrganizationCode = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

# 生成表单的执行语句
Base.metadata.create_all(engine)