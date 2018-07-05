#coding=utf-8
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
    r_id = Column(Integer,ForeignKey("permission_role.id"), primary_key=True)


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
    user_id = Column(Integer,ForeignKey("user.id"), primary_key=True)
    role_id = Column(Integer,ForeignKey("permission_role.id"), primary_key=True)

'''用户表'''
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    user_name = Column(String(60), unique=True, nullable=False)
    job_number = Column(String(50), unique=True, nullable=False)
    _password = Column('password', String(128), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    tel = Column(String(50), unique=True, nullable=False)
    create_time = Column(DateTime, default=datetime.now)

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
    """角色表"""
    __tablename__ = 'permission_role'
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 角色名称:
    name = Column(String(200), primary_key=False, autoincrement=False, nullable=True)

    #角色编码
    code = Column(String(20),nullable=False)

    # 角色说明:
    description = Column(String(2048), primary_key=False, autoincrement=False, nullable=True)

    # 创建时间:
    create_time = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 创建人:
    creator = Column(String(20), primary_key=False, autoincrement=False, nullable=True)

    #角色表和用户表多对多查询关系
    users = relationship("User", secondary=UserToRole.__table__)

    #角色表和权限表多对多查询关系
    permissions = relationship("Permission", secondary=PermissionToRole.__table__)

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

    def __repr__(self):
        return 'id:{},name:{},description:{},create_time:{},creator:{}'.format(
            self.id,
            self.name,
            self.description,
            self.create_time,
            self.creator,
        )

Base.metadata.create_all(engine)