
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
class User(Base):
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

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # python 3

# 用户回调的回调函数
###加载用户的回调函数接收以Unicode字符串形式表示的用户标示符
###如果能找到用户，这个函数必须返回用户对象，否则返回None。



# 生成表单的执行语句
# Base.metadata.create_all(engine)
# import json
# UnReadMsg = db_session.query(Role).all()
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

# 批物料平衡
class BatchMaterielBalance(Base):
    __tablename__ = 'BatchMaterielBalance'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 计划ID:
    PlanManagerID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, nullable=False, primary_key=False)

    # 偏差说明:
    DeviationDescription = Column(String(120), primary_key=False, autoincrement=False, nullable=True)

    # 审核意见:
    CheckedSuggestion = Column(Unicode(120), primary_key=False, autoincrement=False, nullable=True)

    # 审核人:
    CheckedPerson = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 工序负责人:
    PUIDChargePerson = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 操作间编号:
    OperationSpaceNum = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 操作时间:
    OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 太子参:
    taizishen = Column(String(32), primary_key=False, autoincrement=False, nullable=True)

    # 炒麦芽:
    chaomaiya = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 净山楂:
    jingshanzha = Column(String(32), primary_key=False, autoincrement=False, nullable=True)

    # 陈皮:
    chenpi = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 净肿节风:
    jingzjf = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 进:
    input = Column(String(32), primary_key=False, autoincrement=False, nullable=True)

    # 出:
    output = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)



# 设备操作手册
class OperationManual(Base):
    __tablename__ = 'OperationManual'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 手册名称:
    ManualName = Column(String(800), primary_key=False, autoincrement=False, nullable=True)

    # 手册文件:
    ManualFile = Column(String(800), primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Description = Column(String(800), primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    Type = Column(String(800), primary_key=False, autoincrement=False, nullable=True)

    # 操作时间:
    UploadDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 批记录操作步骤（SOP）
class OperationProcedure(Base):
    __tablename__ = 'OperationProcedure'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, nullable=False, primary_key=False)

    # 设备编码
    EQPCode = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 操作步骤内容:
    Content = Column(String(800), primary_key=False, autoincrement=False, nullable=True)

    # 操作值:
    OperationpValue = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 开始时间:
    StartTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 结束时间:
    EndTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    Type = Column(String(800), primary_key=False, autoincrement=False, nullable=True)

    #顺序号:
    Seq = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)

    # 描述:
    Description = Column(String(800), primary_key=False, autoincrement=False, nullable=True)


# 电子批记录
class ElectronicBatch(Base):
    __tablename__ = 'ElectronicBatch'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # id:
    TaskID = Column(Integer, primary_key=False, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段编码:
    PDUnitRouteID = Column(Integer, nullable=False, primary_key=False)

    # 设备编码
    EQPID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    OpcTagID = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    BrandID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    BrandName = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    # 采样值:
    SampleValue = Column(Unicode(64), primary_key=False, autoincrement=False, nullable=True)

    # 采样时间:
    SampleDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 重复次数：
    RepeatCount = Column(Integer, primary_key=False, autoincrement=False, nullable=True, default=0)

    # 描述:
    Description = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Type = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    # 单位:
    Unit = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 质量控制
class QualityControl(Base):
    __tablename__ = 'QualityControl'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, nullable=False, primary_key=False)

    # 设备编码
    EQPCode = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 温度:
    Temperature = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 比重值:
    ProportionValue = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 测量时间:
    MeasureDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Description = Column(Unicode(800), primary_key=False, autoincrement=False, nullable=True)

# 类型
class Type(Base):
    __tablename__ = 'Type'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 类型编码:
    TypeCode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    TypeDescription = Column(Unicode(200), primary_key=False, autoincrement=False, nullable=True)

    #描述
    Desc = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

# 类型模板
class TypeCollection(Base):
    __tablename__ = 'TypeCollection'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 类型编码:
    TypeCode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 类型:
    OpcTagID = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)

    #描述
    Desc = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

# 准备工作NEW
class NewReadyWork(Base):
    __tablename__ = 'NewReadyWork'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, nullable=False, primary_key=False)

    # 类型:
    Type = Column(String(20), primary_key=False, autoincrement=False, nullable=True)

    # 操作人:
    OperationPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 复核人:
    CheckedPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # QA确认人:
    QAConfirmPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Description = Column(String(60), primary_key=False, autoincrement=False, nullable=True)

    # 操作时间:
    OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 设备运转情况表
class EquipmentWork(Base):
    __tablename__ = 'EquipmentWork'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 设备名称:
    EQPName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 设备编码
    EQPCode = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)

    # 设备运转情况
    ISNormal = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 操作人:
    OperationPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 复核人:
    CheckedPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 生产过程是否符合安全管理规定:
    IsStandard = Column(String(20), primary_key=False, autoincrement=False, nullable=True)

    # QA确认人:
    QAConfirmPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 操作时间:
    OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

#收粉结束，包装材料统计
class PackMaterial(Base):
    __tablename__ = 'PackMaterial'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 名称:
    MaterialName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 物料号：
    MaterialCode = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)

    # 批号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 准备只：
    ReadyUnit = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 使用只：
    UserUnit = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 余只：
    SurplusUnit = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 不合格只：
    DefectiveUnit = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 损耗只：
    AttritionUnit = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 退库只：
    CancelStocksUnit = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 统计人:
    OperationPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 复核人:
    CheckedPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # QA确认人:
    QAConfirmPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, nullable=False, primary_key=False)

    # 操作时间:
    OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)


# 物料来源
class MaterialSource(Base):
    __tablename__ = 'MaterialSource'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 物料名称:
    MaterialName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 物料号：
    MaterialCode = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)

    # 批号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 检验单号：
    CheckedNum = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 数量（只）：
    Number = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    # 复核人:
    CheckedPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # QA确认人:
    QAConfirmPeople = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, nullable=False, primary_key=False)

    # 操作时间:
    OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 批记录操作步骤（SOP）
class EletronicBatchDataStore(Base):
    __tablename__ = 'EletronicBatchDataStore'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批次号:
    BatchID = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工艺段ID:
    PUID = Column(Integer, nullable=False, primary_key=False)

    # 操作步骤内容:
    Content = Column(String(60), primary_key=False, autoincrement=False, nullable=True)

    # 操作值:
    OperationpValue = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

    #操作人:
    Operator = Column(Unicode(32), primary_key = False, autoincrement = False, nullable = True)

    # 描述:
    Description = Column(String(100), primary_key=False, autoincrement=False, nullable=True)

#  维护周期
class MaintenanceCycle(Base):
    __tablename__ = 'MaintenanceCycle'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 维护类型（设备润滑，仪表调校） :
    MaintenanceType = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 维护周期范围低限 :
    MaintenanceLower = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 维护周期范围高限:
    MaintenanceHeigh = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 单位描述:
    DescriptionUnit = Column(Unicode(60), primary_key=False, autoincrement=False, nullable=True)

#   维护状态表
class MaintenanceStatus(Base):
    __tablename__ = 'MaintenanceStatus'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 开始使用日期 :
    StartDateTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 效验周期 :
    ValidationCycle = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 下一个效验时间 :
    NextValidationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 是否开始使用 :
    IsNotUse = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Description = Column(String(100), primary_key=False, autoincrement=False, nullable=True)

#   设备包含仪表
class Instruments(Base):
    __tablename__ = 'Instruments'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 设备ID（设备表 里设备类型生 产设备）:
    EquipmentID = Column(Integer, primary_key=False, autoincrement=True, nullable=False)

    # 设备ID（设备表 里设备类型为 仪表） :
    InstrumentsID = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 区域
class Area(Base):
    __tablename__ = 'Area'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 区域编码 :
    AreaCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 区域名称 ：
    AreaName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 区域编号 :
    AreaNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 描述:
    Description = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 类型 ：
    AreaType = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 上级工厂 ：
    PeFactory = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 顺序:
    seq = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

# 备件库存
class SparePartStock(Base):
    __tablename__ = 'SparePartStock'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 区域（江中罗亭）  :
    AreaName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 库存数量（入库+1，出库-1） ：
    StockNum = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 库存预警数量  :
    StockWarnningNum = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

    # 库存预警提醒标识 :
    StockWarnningFlag = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 描述 ：
    Description = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

#  调度日期
class SchedulePlan(Base):
    __tablename__ = 'SchedulePlan'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 调度编码 :
    SchedulePlanCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 调度描述：
    Desc = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 调度开始时间:
    PlanBeginTime = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 调度结束时间  :
    PlanEndTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 类型 ：
    Type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

#  设备维护
class EquipmentMaintain(Base):
    __tablename__ = 'EquipmentMaintain'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 设备维护计划单号 :
    MaintainPlanNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 类型（润滑，巡检，维修） ：
    MaintainType = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 设备（可以多选）  :
    EquipmentName = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 计划开始时间 :
    PlanBeginDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 计划结束时间  ：
    PlanEndDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 维护要求  ：
    MaintainDemand = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 状态 ：
    MaintainStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 描述 ：
    Description = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 制定计划人:
    MakePlanPeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 审核人:
    CheckPeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 检修人:
    FinishedPeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

#  设备维护知识库
class EquipmentMaintenanceKnowledge(Base):
    __tablename__ = 'EquipmentMaintenanceKnowledge'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 故障类型（机械，电气）  :
    FailureReportingType = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 故障描述   ：
    FailureReportingDesc = Column(Unicode(120), primary_key=False, autoincrement=False, nullable=True)

    # 故障处理  ：
    FailureReportingHandle = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 描述  ：
    Description = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

# 备件出入库管理
class SparePartInStockManagement(Base):
    __tablename__ = 'SparePartInStockManagement'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 备件编码:
    SpareCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 区域（江中罗亭）  :
    AreaName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 操作（出库，入库）：
    Operation = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 备件使用状况（全新，旧备件）  :
    StockUseStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 录入人:
    InStockPeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 审核人:
    CheckedPeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 录入时间  :
    InStockDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 审核时间  :
    CheckedDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 描述 ：
    Description = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

#  备件库
class SpareStock(Base):
    __tablename__ = 'SpareStock'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 备件编码:
    SpareCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 备件名称：
    SpareName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 备件状态:
    SpareStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 备件型号:
    SpareModel = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 生产厂家:
    SpareFactory = Column(Unicode(62), primary_key=False, autoincrement=False, nullable=True)

    # 备件类型：
    SpareType = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 备件功率：
    SparePower = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 描述：
    Description = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 备件使用状况（全新，旧备件）  :
    StockUseStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 生产日期:
    ProductionDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 录入时间:
    CreateDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 录入人:
    InStockPeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 审核人:
    CheckedPeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 审核时间:
    CheckedDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

    # 入库时间:
    InStockDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

#  备件类型库
class SpareTypeStore(Base):
    __tablename__ = 'SpareTypeStore'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 备件类型编码
    SpareTypeCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 备件类型名称
    SpareTypeName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 父节点
    ParentNode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True, default='0')

#  设备运行记录
class EquipmentRunRecord(Base):
    __tablename__ = 'EquipmentRunRecord'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 车间
    Workshop = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工序
    PUIDName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 设备名称:
    EQPName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 设备编码
    EQPCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 日期:
    InputDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 班次:
    Classes = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 运行时间:
    RunDate = Column(Float, primary_key=False, autoincrement=False, nullable=True)

    # 清场时间:
    ClearDate = Column(Float, primary_key=False, autoincrement=False, nullable=True)

    # 故障时间:
    FailureDate = Column(Float, primary_key=False, autoincrement=False, nullable=True)

    # 操作人:
    OperatePeople = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 产品名称:
    BrandName1 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 产品批号:
    BatchID1 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 产品名称:
    BrandName2 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 产品批号:
    BatchID2 = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 添加时间:
    CreateDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

#  设备维修记录表
class EquipmentReportingRecord(Base):
    __tablename__ = 'EquipmentReportingRecord'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 设备维修计划单号  :
    ReportingNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 工序  ：
    PUIDName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 故障时间:
    FailureDate = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 早晚班  :
    Shift = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 设备名称:
    EQPName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 故障描述   ：
    FailureReportingDesc = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 原因分析   ：
    AnalysisFailure = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 解决措施  ：
    Precautions = Column(Unicode(65), primary_key=False, autoincrement=False, nullable=True)

    # 不影响生产（分钟）  ：
    UnAffectingProduction = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 影响生产（分钟）  ：
    AffectingProduction = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 维修人:
    Repairman = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 备件更换情况:
    ReplacementOfSpareParts = Column(Unicode(40), primary_key=False, autoincrement=False, nullable=True)

class EquipmentRunPUID(Base):
    __tablename__ = 'EquipmentRunPUID'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 工序
    PUIDName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 设备名称:
    EQPName = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)

    # 设备编码
    EQPCode = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 父节点
    ParentNode = Column(Integer, primary_key=False, autoincrement=False, nullable=True)

class BatchNameTypeName(Base):
    __tablename__ = 'BatchNameTypeName'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 批记录对应的Name：
    BatchName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 采集对应的TypeName:
    TypeName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 设备保养标准
class EquipmentMaintenanceStandard(Base):
    __tablename__ = 'EquipmentMaintenanceStandard'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 设备名称
    EquipentName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 保养周期
    MaintenanceCycle = Column(Unicode(25), primary_key=False, autoincrement=False, nullable=True)

    # 保养提醒周期
    MaintenanceReminderCycle = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 录入人
    EntryPerson = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 录入时间
    EntryTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 设备保养数据
class EquipmentMaintenanceStore(Base):
    __tablename__ = 'EquipmentMaintenanceStore'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 设备型号
    EquipmentType = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 设备名称
    EquipentName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 设备编号
    EquipmentNumber = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 操作内容
    Content = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 操作值
    OperationValue = Column(Boolean, primary_key=False, autoincrement=False, nullable=True)

    #日期
    Date = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    #保养责任人
    PersonLiable = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 督导人
    SuperVisor = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 操作时间
    OperationDate = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 成本中心
class CenterCost(Base):
    __tablename__ = 'CenterCost'
    # id:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # 成本中心号
    CenterCostNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

    # 成本中心
    CharityPerson = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

class EquipmentStatusCount(Base):
    __tablename__ = "EquipmentStatusCount"
    # ID:
    ID = Column(BigInteger, primary_key=True, autoincrement=True, nullable=True)
    #采集时间
    SampleTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 系统内部设备编码:
    SYSEQPCode = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)
    # 状态
    Status =  Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)
    # 状态类型
    StatusType = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)
    # 是否停机
    IsStop = Column(Unicode(10), primary_key=False, autoincrement=False, nullable=True)
    #持续时间
    Duration = Column(Float, primary_key=False, autoincrement=False, nullable=True)

# 班次
class Shifts(Base):
    __tablename__ = "Shifts"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 班次编码
    ShiftsCode = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)
    # 班次名称
    ShiftsName = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)
    #班次开始时间
    BeginTime = Column(Time, primary_key=False, autoincrement=False, nullable=True)
    # 班次结束时间
    EndTime = Column(Time, primary_key=False, autoincrement=False, nullable=True)


# 设备运行数据自动采集树形
class EquipmentTimeStatisticTree(Base):

    __tablename__ = "EquipmentTimeStatisticTree"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 树节点
    Key = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)
    # 品名
    Brand = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)
    # 父节点
    ParentNode = Column(Unicode(10), primary_key=False, autoincrement=False, nullable=True)

# 设备运行记录设备编码
class SystemEQPCode(Base):
    __tablename__ = "SystemEQPCode"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 工序
    Unit = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)
    # Brand
    Brand = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)
    # EquipCode
    EquipCode = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)

# 设备运行记录自动获取
class EquipmentTimeStatistic(Base):
    __tablename__ = "EquipmentTimeStatistic"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 采样时间
    SampleTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 班次ID
    ShiftsCode= Column(Integer, primary_key=False, autoincrement=False, nullable=True)
    # 设备编码
    EquipmentCode = Column(Unicode(20), primary_key=False, autoincrement=False, nullable=True)
    # 运行时间
    RunTime = Column(Float, primary_key=False, autoincrement=False, nullable=True)
    # 故障时间
    ErrorTime = Column(Float, primary_key=False, autoincrement=False, nullable=True)
    # 停机时间
    StopTime = Column(Float, primary_key=False, autoincrement=False, nullable=True)
    # 清场时间
    ClearTime = Column(Float, primary_key=False, autoincrement=False, nullable=True)

# 设备说明书
class EquipmentManagementManua(Base):
    __tablename__ = "EquipmentManagementManua"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 说明书名称
    Name = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)
    # 存储路径
    Path = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)
    # 作者
    Author = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)
    # 上传时间
    UploadTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 工厂日历
class plantCalendarScheduling(Base):
    __tablename__ = "plantCalendarMode"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 时间
    start = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)
    # 排产
    title = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)
    #颜色
    color = Column(Unicode(30), primary_key=False, autoincrement=False, nullable=True)

#物料主数据
class product_info(Base):
    __tablename__ = "product_info"
    # 物料编码
    product_code = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 物料名称
    product_name = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)
    # 计量单位
    product_unit = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 物料类型
    product_type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 物料主数据表
class product_infoERP(Base):
    __tablename__ = "product_infoERP"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 物料编码
    product_code = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 物料名称
    product_name = Column(Unicode(100), primary_key=False, autoincrement=False, nullable=True)
    # 计量单位
    product_unit = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 物料类型
    product_type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 生产计划表
class product_plan(Base):
    __tablename__ = "product_plan"
    # 计划ID:
    plan_id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 计划期间（YYYYMM）
    plan_period = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 产品(即物料)编码
    product_code = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 产品(即物料)名称
    product_name = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 计量单位 kg\批
    product_unit = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 计量类型 'B' 批次  'W'重量
    meter_type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 计划数量
    plan_quantity = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 计划类型 'M' 月计划
    plan_type = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 插入时间
    create_time = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 数据对接时间
    transform_time = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 数据对接MES 1 已对接 0 未对接
    transform_flag = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 排产表
class Scheduling(Base):
    __tablename__ = "Scheduling"
    ## ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 产品名称
    PRName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    #排产时间(工厂日历)
    SchedulingTime = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 排产序列号
    SchedulingNum = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 批数
    BatchNumS = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 排产状态
    SchedulingStatus = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 创建时间
    create_time = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 修改时间
    update_time = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# 排产库存表
class SchedulingStock(Base):
    __tablename__ = "SchedulingStock"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 产品(即物料)编码
    product_code = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)
    # 物料名称
    MATName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 仓库库存
    StockHouse = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 安全库存
    SafetyStock = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 创建时间
    create_time = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 修改时间
    update_time = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)

# ERP产品编码与mes对应的产品名称
class ERPproductcode_prname(Base):
    __tablename__ = "ERPproductcode_prname"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 产品(即物料)编码
    product_code = Column(Unicode(50), primary_key=False, autoincrement=False, nullable=True)
    # 产品名称
    PRName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 排产规范表--一天做多少批产品，一批产品等于多少公斤原材料
class SchedulingStandard(Base):
    __tablename__ = "SchedulingStandard"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 产品名称
    PRName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 批数（批/每天）
    DayBatchNumS = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 物料重量（kg/批）
    Batch_quantity = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 物料库存消耗表
class SchedulingMaterial(Base):
    __tablename__ = "SchedulingMaterial"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 物料名称
    MaterialName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 时间
    SchedulingTime = Column(DateTime, primary_key=False, autoincrement=False, nullable=True)
    # 物料剩余量
    Surplus_quantity = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 得率维护表
class YieldMaintain(Base):
    __tablename__ = "YieldMaintain"
    # ID:
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    # 品名
    PRName = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 得率PRName
    Yield = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 成品总重量
    FinishProduct = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 取样量
    SamplingQuantity = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)
    # 药材总投料量
    TotalQuantity = Column(Unicode(32), primary_key=False, autoincrement=False, nullable=True)

# 生成表单的执行语句
Base.metadata.create_all(engine)

