
from multiprocessing.managers import BaseManager
from constant import constant

MANAGER_PORT = constant.DATA_REALTIME_SERVER_PORT
MANAGER_DOMAIN = constant.DATA_REALTIME_SERVER_DOMAIN
MANAGER_AUTH_KEY = constant.DATA_REALTIME_SERVER_AUTH_KEY.encode(encoding='utf-8')

#定义一个Manager类
class InfoManager(BaseManager): pass

from collections import Iterable
class DictItem():
    def __init__(self, ):
        self.items = dict()

    def set(self, key, value):
        self.items[key] = value

    def get(self, key):
        return self.items.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def getItems(self):
        return self.items

#为这个manager类注册存储容器，也就是通过这个manager类实现的共享的变量，
#这个变量最好是一个类实例，自己定义的或者python自动的类的实例都可以
#这里不能把d改成dict()，因为Client那边执行d['keyi']='value'的时候会报错：d这个变量不能修改
dataItems = DictItem()
dataItems.set('isalive_flag',False)
InfoManager.register('dict', callable=lambda:dataItems)

class ManagerServer():
    '''
    multiprocess Manager服务类
    '''

    def __init__(self, domain, port, auth_key):
        self.domain = domain
        self.port = port
        self.auth_key = auth_key
        self.is_stop = 0

    def start_manager_server(self):
        self.queue_manager = InfoManager(address=(self.domain, self.port), authkey=self.auth_key)
        self.server = self.queue_manager.get_server()

    def run(self):
        self.start_manager_server()

        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.is_stop = 1


class ManagerClient():
    '''
    访问mutiprocess Manager的类
    '''

    def __init__(self, domain, port, auth_key):
        self.domain = domain
        self.port = port
        self.auth_key = auth_key
        # self.get_share_dict()
        self.info_manager = InfoManager(address=(self.domain, self.port), authkey=self.auth_key)
        self.info_manager.connect()

    def get_dict(self):
        self.dict = self.info_manager.dict()
        return self.dict

if __name__ == '__main__':
    pass