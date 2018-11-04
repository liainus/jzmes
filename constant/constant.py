import os,configparser
from enum import Enum
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR,r'config\config.ini')
config = configparser.ConfigParser()
config.read(CONFIG_DIR,encoding='UTF-8')

DATA_REALTIME_SERVER_DOMAIN = config['data_realtime_server']['domain']
DATA_REALTIME_SERVER_PORT = int(config['data_realtime_server']['port']) if config['data_realtime_server']['port'].isdigit() else 6000
DATA_REALTIME_SERVER_AUTH_KEY = config['data_realtime_server']['auth_key']
DATABASE_SERVER_URI = config['database_server']['URI']

TAGS_DIR = os.path.join(BASE_DIR,r'tags')
TAGS_CONFIG_DIR = os.path.join(TAGS_DIR,r'tags_cfg')

LOG_DIR = os.path.join(BASE_DIR,r'logs')