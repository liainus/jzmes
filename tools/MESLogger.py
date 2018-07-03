import logging
import time
import os
import threading
from enum import Enum

class LogLevel(Enum):
    info = 'info'
    warning = 'warning'
    error = 'error'
    debug = 'debug'
    critical = 'critical'
class MESLogger(logging.getLoggerClass()):
   # __instance = None
    _instance_lock = threading.Lock()
    def __init__(self,log_dir,name=None):
        self.parent = None
        self.level = logging.NOTSET
        self.filters = []
        self.propagate = True
        self.handlers = []
        self.disabled = False
        self._log_dir = log_dir
        self._last_day = None
        self._LOGGING_MSG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(filename)s] [%(module)s] [%(funcName)s] [%(lineno)d] %(message)s'
        self._LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        self.init(log_dir,name)
    def init(self,log_dir,logger_name=None):
        '''
        #获取一个配置好的日志对象
        :return: a logger
        '''
        self._log_dir = log_dir
        current_day = time.strftime("%Y%m%d")
        self._last_day = current_day
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, current_day + '.log')
        self.name = (log_dir if logger_name is None else logger_name)

        fh = logging.FileHandler(log_file, encoding='utf-8')
        self.addHandler(fh)
        fmt = logging.Formatter(self._LOGGING_MSG_FORMAT, datefmt=self._LOGGING_DATE_FORMAT)
        fh.setFormatter(fmt)
        #self.setLevel(logging.INFO)

    def __new__(cls, *args, **kwd):
        # if LoggerHelper.__instance is None:
        #     LoggerHelper.__instance = object.__new__(cls, *args, **kwd)
        # return LoggerHelper.__instance

        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(MESLogger, cls).__new__(cls)
        return cls._instance
    def change_logfile(self):
        current_day = time.strftime("%Y%m%d")
        if self._last_day == current_day:
            return None
        self._last_day = current_day
        log_file = os.path.join(self._log_dir, current_day + '.log')
        if os.path.exists(log_file):
           # print(log_file)
            return None
        fh = logging.FileHandler(log_file, encoding='utf-8')
        self.removeHandler(self.handlers)
        self.addHandler(fh)
        fmt = logging.Formatter(self._LOGGING_MSG_FORMAT, datefmt=self._LOGGING_DATE_FORMAT)
        fh.setFormatter(fmt)
        return log_file
    def info(self, msg, *args, **kwargs):
        self.change_logfile()
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)
    def warning(self, msg, *args, **kwargs):
        self.change_logfile()
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)
    def error(self, msg, *args, **kwargs):
        self.change_logfile()
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)