from enum import Enum, IntEnum, unique

#JSON返回成功！
GLOBAL_JSON_RETURN_OK={"status": "OK"}

#数据库连接字符串！
GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:Qcsw@758@192.168.2.102:1433/MES?charset=utf8"#Qcsw@758@192.168.2.111  root@192.168.2.112  jzjtxxzx@123@192.168.100.150


# #数据库连接字符串！
# GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:Qcsw@758@192.168.2.103:1433/MES?charset=utf8"

GLOBAL_NULL_STRING= ""

GLOBAL_PLANSTARTTIME= "09:00:00"
GLOBAL_PLANENDTIME= "08:59:59"

#计划planmanager
class PlanStatus(Enum):
    NEW = "10"#新增
    Checked = "11"#已审核
    Realse = "20"#已下发
    Recall = "40"#撤回
    RUN = "50"#执行
    FINISH = "60"#已完成
    QApass = "70"#QA放行

#计划ZYPlan
class ZYPlanStatus(Enum):
    NEW = "10"#新增
    Realse = "20"#下发
    Control = "30"#中控已确认
    ControlChecked = "31"#中控已复核
    QAChecked = "32"#QA已复核
    COMFIRM = "40"#确认
    RUN = "50"#执行
    FINISH = "60"#完成
    AgainControl = "61"#中控确认生产结束清场
    AgainControlChecked = "62"#中控复核生产结束清场
    AgainQAChecked = "63"#QA清场复核

#任务ZYTask
class TASKSTATUS(Enum):
    NEW = "10"#新增
    Realse = "20"#下发
    COMFIRM = "40"#确认
    RUN = "50"#执行
    FINISH = "60"#完成
    CANCEL = "70"#取消
    PAUSE = "80"#暂停
    ERROR = "85"#故障
    TERMINAL = "90"#中止

#计划状态
class AuditStatus(Enum):
    Unaudited = "10"#未审核
    Checked = "20"#审核
    Realse = "30"#下发
    Recall = "40"#撤回
    ClearField = "50"#清场
    Recheck = "60"#清场复核
    ReviewPass = "70"#QA审核通过
    BatchEndPass = "80"#QA批次结束放行

#WorkFlowEventPlan的type
class Type(Enum):
    NEW = "10"#生产部门制定计划
    Checked = "11"#生产部分复核计划
    Realse = "20"#下发计划
    Recall = "21"# 生产部门撤回计划
    Control = "30"#中控操作确认
    ControlChecked = "31"#中控操作复核
    COMFIRM = "40"  # 任务确认
    QAChecked = "32"#QA复核
    RUN = "50"#执行计划
    FINISH = "60"#完成计划
    AgainControl = "61"  #中控确认生产结束清场
    AgainControlChecked = "62"  #中控复核生产结束清场
    AgainQAChecked = "63"  #QA清场复核
    QApass = "70"#QA放行

#WorkFlowEventZYPlan的TypeZY
class TypeZY(Enum):
    NEW = "10"#下发生成计划
    Control = "30"#中控操作确认
    ControlChecked = "31"#中控操作复核
    QAChecked = "32"#QA复核
    COMFIRM = "40"#任务确认
    RUN = "50"#执行计划
    FINISH = "60"#完成计划
    AgainControl = "61"  # 中控确认生产结束清场
    AgainControlChecked = "62"  # 中控复核生产结束清场
    AgainQAChecked = "63"  # QA清场复核

#处理状态
class Handle(Enum):
    Untreated = "0"#未处理
    Treated = "1"#已处理

class TASKLOCKSTATUS(Enum):
    LOCKED = "10"
    UNLOCK = "0"


class SCHEDULETYPE(Enum):
    DAY = "日计划"
    MONTH = "月计划"
    YEAR = "年计划"


class PLANTYPE(Enum):
    SCHEDULE = "调度计划"

WeightUnit = 'kg'


