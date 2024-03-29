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

MES_DATABASE_HOST = config['MES_DataBase']['host']
MES_DATABASE_USER = config['MES_DataBase']['user']
MES_DATABASE_PASSWD = config['MES_DataBase']['password']
MES_DATABASE_NAME = config['MES_DataBase']['database']
MES_DATABASE_CHARSET = config['MES_DataBase']['charset']

OUTPUT_COMPARE_INPUT = config['output_compare']['input']
OUTPUT_COMPARE_OUTPUT = config['output_compare']['output']
OUTPUT_COMPARE_SAMPLE = config['output_compare']['sampling_quantity']

def transform_dict(position):
    if position:
        dict_ = dict()
        for key in eval(position).keys():
            dict_[key] = eval(position)[key]
        return dict_

MONITOR_TRANSPORT_BLUE_TAG = transform_dict("config['transport_section_blue']")
MONITOR_TRANSPORT_RED_TAG = transform_dict("config['transport_section_red']")

CPK_TAG_LIST = config['CPK_Tag']
SINGLE_CONCENTRATION_TAG =transform_dict("config['Single_effect_concentration']")
ALCOHOLPRECIPITATION_TAG = transform_dict("config['AlcoholPrecipitation']")

materia_tracing_A_drug = config['materia_tracing_A_drug']
A_drug = [i for i in materia_tracing_A_drug.keys()]
materia_tracing_B_drug = config['materia_tracing_B_drug']
B_drug = [j for j in materia_tracing_B_drug.keys()]

Decocting_A_EquipID = eval(config['EquipID']['Decocting_A'])
Decocting_B_EquipID = eval(config['EquipID']['Decocting_B'])
AlcoholEquipID = eval(config['EquipID']['Alcohol'])
TrayNumber = config['TrayNumber']
EQPNameS = config['EQPNameS']