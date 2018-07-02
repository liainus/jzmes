from enum import Enum, IntEnum, unique

#JSON返回成功！
GLOBAL_JSON_RETURN_OK={"status": "OK"}

#数据库连接字符串！
GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:123456@127.0.0.1:1433/MES?charset=utf8"


#数据库连接字符串！
#GLOBAL_DATABASE_CONNECT_STRING= "mssql+pymssql://sa:Qcsw@123@127.0.0.1:1433/MES?charset=utf8"

GLOBAL_NULL_STRING= ""

GLOBAL_PLANSTARTTIME= "09:00:00"
GLOBAL_PLANENDTIME= "08:59:59"


class TASKSTATUS(Enum):
    COMPILE = "10"
    REDAY = "20"
    NEW = "30"
    COMFIRM = "40"
    RUN = "50"
    FINISH = "60"
    CANCEL = "70"
    PAUSE = "80"
    ERROR = "85"
    TERMINAL = "90"


class TASKLOCKSTATUS(Enum):
    LOCKED = "10"
    UNLOCK = "0"


class SCHEDULETYPE(Enum):
    DAY = "日计划"
    MONTH = "月计划"
    YEAR = "年计划"


class PLANTYPE(Enum):
    SCHEDULE = "调度计划"


