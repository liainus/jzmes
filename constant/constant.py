import os,configparser
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR,r'config\config.ini')
config = configparser.ConfigParser()
config.read(CONFIG_DIR,encoding='UTF-8')


REDIS_HOST = config['data_realtime_server']['host']
REDIS_TABLENAME = config['data_realtime_server']['tablename']
REDIS_PORT = int(config['data_realtime_server']['port']) if config['data_realtime_server'][
    'port'].isdigit() else 6379
REDIS_PASSWORD = config['data_realtime_server']['password']