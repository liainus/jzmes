from enum import Enum
from sqlalchemy import Column, Unicode,Integer,Boolean,DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import Model.Global

engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Base = declarative_base(engine)
session = sessionmaker(engine)()
class NodeStatus(Enum):
    NOTEXE = 0  #未执行
    PASSED = 10  #通过
    REJECTED = 20 #未通过
class type(Enum):
    planmanager = 10
    zyplan = 20
    zytask = 30
class flowPathNameJWXSP(Enum):
    A = "审核计划流程"
    B = "下发计划流程"
    C = "（备料段）生产前准备流程"
    D = "备料操作按SOP执行流程"
    E = "（备料段）生产结束清场流程"
    F = "（煎煮段）生产前准备流程"
    G = "煎煮开始，操作按SOP执行流程"
    H = "静置开始，操作按SOP执行流程"
    I = "（煎煮段）生产结束清场流程"
    J = "（浓缩段）生产前准备流程"
    K = "浓缩开始，操作按SOP执行流程"
    L = "浓缩结束清场流程"
    M = "（喷雾干燥段）生产前准备流程"
    N = "喷雾干燥开始，操作按SOP执行流程"
    O = "喷雾干燥结束，按SOP清场流程"
    P = "（收粉段）生产前准备流程"
    Q = "收粉开始，操作按SOP执行流程"
    R = "收粉结束，按SOP清场流程"
    S = "QA放行流程"
class flowPathNameCSHHP(Enum):
    A = "审核计划流程"
    B = "下发计划流程"
    C = "（备料段）生产前准备流程"
    D = "备料操作按SOP执行流程"
    E = "（备料段）生产结束清场流程"
    F = "（煎煮段）生产前准备流程"
    G = "煎煮开始，操作按SOP执行流程"
    H = "静置开始，操作按SOP执行流程"
    I = "（煎煮段）生产结束清场流程"
    J = "（浓缩段）生产前准备流程"
    K = "浓缩开始，操作按SOP执行流程"
    L = "浓缩结束清场流程"
    M = "（醇沉段）生产前准备流程"
    N = "醇沉开始，操作按SOP执行流程"
    O = "醇沉结束，按SOP清场流程"
    P = "（单效浓缩段）生产前准备流程"
    Q = "单效浓缩开始，操作按SOP执行流程"
    R = "单效浓缩结束，按SOP清场流程"
    S = "（收膏段）生产前准备流程"
    T = "收膏开始，操作按SOP执行流程"
    U = "收膏结束，按SOP清场流程"
    V = "QA放行流程"
class BaseNode(object):
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(32),nullable=True)
    status = Column(Integer,nullable=True,default=NodeStatus.NOTEXE.value)
    desc = Column(Unicode(32), nullable=True)
    def doPass(self):
        print("pass")
        self.status = NodeStatus.PASSED
    def doReject(self):
        print('reject')
        self.status = NodeStatus.REJECTED
class Node(BaseNode,Base):
    __tablename__ = 'node'

class NodeCollection(BaseNode,Base):
    __tablename__ = 'nodecollection'
    oddNum = Column(Unicode(32), nullable=True)
    oddUser = Column(Unicode(32), nullable=True)
    opertionTime = Column(DateTime, nullable = True)
    seq =  Column(Integer, nullable=True)
class  Procedure(Base):
    __tablename__ = 'procedure'
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    nodeName = Column(Unicode(32), nullable=True)
    preNodeName = Column(Unicode(32), nullable=True)
    nextNodeName = Column(Unicode(32), nullable=True)
    flowPathName = Column(Unicode(32), nullable=True)
    desc = Column(Unicode(32), nullable=True)

class FlowPath(Base):
    __tablename__ = 'flowpath'
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(32),nullable=True)
    type =  Column(Integer, nullable=True)
    desc = Column(Unicode(32), nullable=True)

class Odd(Base):
    __tablename__ = 'odd'
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    oddNum = Column(Unicode(32), nullable=True)
    flowPathName = Column(Unicode(32), nullable=True)
    desc = Column(Unicode(32), nullable=True)

Base.metadata.create_all(engine)