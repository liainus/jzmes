#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import base64
import hashlib
import time
import redis
from flask import Blueprint, render_template, request, make_response
import json
import datetime
from sqlalchemy import desc, create_engine
from flask_login import login_required, logout_user, login_user,current_user,LoginManager
import arrow
from sqlalchemy.orm import sessionmaker
from tools.common import logger, insertSyslog
import Model
from Model.system import TrayNumberRedisTag, WMSTrayNumber
from constant import constant

engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
db_session = Session()

pool = redis.ConnectionPool(host=constant.REDIS_HOST, password=constant.REDIS_PASSWORD)
def run():
    try:
        while True:
            data_dict = {}
            redis_conn = redis.Redis(connection_pool=pool)
            #trays = constant.TrayNumber
            eqps = constant.EQPNameS
            for key in eqps:
                value = redis_conn.hget(constant.REDIS_TABLENAME, eqps.get(key)).decode('utf-8')
                tagvalue = db_session.query(TrayNumberRedisTag).filter(TrayNumberRedisTag.PalletID == eqps.get(key)).first()
                if tagvalue.value != value and value == "TRUE":#FALSE---TRUE托盘进罐
                    reds = db_session.query(TrayNumberRedisTag).filter(TrayNumberRedisTag.TagID == key).all()
                    for red in reds:
                        pvalue = redis_conn.hget(constant.REDIS_TABLENAME, red.PalletID).decode('utf-8')
                        red.value = pvalue
                        red.inTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elif tagvalue.value != value and value == "FALSE":#TRUE---FALSE托盘出罐
                    reds = db_session.query(TrayNumberRedisTag).filter(TrayNumberRedisTag.TagID == key).all()
                    for red in reds:
                        red.outTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                tagvalue.value = value
                db_session.commit()
            time.sleep(3)
    except Exception as e:
        print(e)
        db_session.rollback()
        logger.error(e)
        insertSyslog("error", "同步托盘redis信息报错Error：" + str(e), current_user.Name)
        return json.dumps([{"status": "Error：" + str(e)}], cls=Model.BSFramwork.AlchemyEncoder,
                          ensure_ascii=False)


class TagRedisPallet(object):
    """
    RedisTag定义
    """

    def __init__(self, ADeviceid):
        '''
        :param tagID: 要采集的变量名称
        :param src: 数据源,为dict类型
        '''
        self._deviceid = ADeviceid
        self._currentvalue = ""
        self._prevalue = ""
        self._tagtype = ""
        self._RdTag_Hold = ""
        self._RdTag_Pallet1 = ""
        self._RdTag_Pallet2 = ""
        self._RdTag_Pallet3 = ""

    def refresh(self):
        print()


if __name__ == '__main__':
    run()