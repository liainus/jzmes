
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
session = Session()
Base = declarative_base(engine)


#引入mssql数据库引擎
import pymssql


# 菜单与角色关联表
Role_Menu = Table(
    "role_menu",
    Base.metadata,
    Column("Role_ID", Integer, ForeignKey("role.ID"), nullable=False, primary_key=True),
    Column("Menu_ID", Integer, ForeignKey("menu.ID"), nullable=False, primary_key=True)
)


# 模块菜单表
class Menu(Base):
    __tablename__ = 'menu'
    # 模块ID
    ID = Column(Integer, primary_key=True, autoincrement=True)

    # 模块名称
    ModuleName = Column(Unicode(32), nullable=False)

    # 模块编码
    ModuleCode = Column(String(100),nullable=False)

    # 模块路由
    Url = Column(String(100), nullable=True)

    # 描述
    Description = Column(Unicode(1024), nullable=True)

    # 创建时间
    CreateDate = Column(DateTime, default=datetime.now, nullable=True)

    # 创建人
    Creator = Column(Unicode(50), nullable=True)

    # 父节点
    ParentNode = Column(Integer, nullable=True)

    # 查询角色
    roles = relationship("Role", secondary=Role_Menu)




# 权限与角色关联表
# Permission_Role = Table(
#     "permission_role",
#     Base.metadata,
#     Column("Permission_ID", Integer, ForeignKey("permission.ID"), nullable=False, primary_key=True),
#     Column("Role_ID", Integer, ForeignKey("role.ID"), nullable=False, primary_key=True)
# )

# 权限表
# class Permission(Base):
#     __tablename__ = 'permission'
#     # ID
#     ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#
#     # 权限名称
#     Per_Name = Column(String(100), nullable=False)
#
#     # 创建时间
#     CreateData = Column(DateTime, default=datetime.now)
#
#     # 创建人
#     Creator = Column(String(50), nullable=True)
#
#     # 查询角色
#     roles = relationship("Role", secondary=Permission_Role)
#
#     # 查询菜单
#     menus = relationship('Menu', secondary=Permission_Menu)

# 角色表
class Role(Base):
    __tablename__ = 'role'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # # 角色编码:
    # RoleCode = Column(String(100), primary_key=False, autoincrement=False, nullable=True)

    # 角色顺序:
    RoleSeq = Column(String(10), primary_key=False, autoincrement=False, nullable=True)

    # 角色名称:
    RoleName = Column(Unicode(128), primary_key=False, autoincrement=False, nullable=True)

    # 角色说明:
    Description = Column(Unicode(2048), primary_key=False, autoincrement=False, nullable=True)

    # 创建人:
    CreatePerson = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 创建时间:
    CreateDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 父节点
    ParentNode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 查询权限
    menus = relationship("Menu", secondary=Role_Menu)



# 用户表
class User(Base,UserMixin):
    __tablename__ = 'user'

    # id
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 用户名
    Name = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 密码
    Password = Column(String(128), nullable=False)

    # 工号
    WorkNumber = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

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

    # 角色名称:
    RoleName = Column(Unicode(128), primary_key=False, autoincrement=False, nullable=True)

    # @property
    # def password(self):
    #     raise AttributeError('password is not a readable attribute')

    # 定义password字段的写方法，我们调用generate_password_hash将明文密码password转成密文Shadow
    # @password.setter
    def password(self, password):
        self.Password = generate_password_hash(password)
        return self.Password

    # 定义验证密码的函数confirm_password
    def confirm_password(self, password):
        return check_password_hash(self.Password, password)

# 用户回调的回调函数
@login_manager.user_loader
###加载用户的回调函数接收以Unicode字符串形式表示的用户标示符
###如果能找到用户，这个函数必须返回用户对象，否则返回None。
def load_user(user_id):
    return User.query.get(int(user_id))


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

# users_data = session.query(User).join(user_role, isouter=True).filter_by(Role_ID=1).all()
# print(users_data)
# per_data = session.query(Permission.Per_ID).join(Permission_User, isouter=True).filter_by(User_ID=1).all()
# print(per_data)
