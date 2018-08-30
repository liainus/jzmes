from Model.core import session,Base,engine,CollectTask,CollectTaskCollection,CollectParams,Collectionstrategy,CollectParamsTemplate,OpcTag
from sqlalchemy.ext.declarative import declarative_base
import Model.Global

# 获取每个采集任务的表名
def get_tableName():
    tableName_list = []
    table_names = session.query(CollectTask.TableName).all()
    for name in table_names:
        tableName_list.append(name)
    return tableName_list

# 生成键为表名，值为NodeID的字典
def get_dict(tableName_list):
    tableName_nodeID_dict = {}
    for tableName in tableName_list:
        nodeIDs = []
        task_name = session.query(CollectTask.CollectTaskName).filter_by(
            TableName=tableName).first()
        TemplateID = session.query(CollectTaskCollection.CollectParamsTemplateID).filter_by(
            CollectTaskName=task_name).first()
        opctagIDs = session.query(CollectParams.OpcTagID).filter_by(
            CollectParamsTemplateID=TemplateID).all()
        for opctagId in opctagIDs:
            nodeID = session.query(OpcTag.NodeID).filter_by(ID=opctagId).first()[0]
            nodeIDs.append(nodeID)
        table_name = '%s'%tableName
        tableName_nodeID_dict.update({table_name: nodeIDs})
    return tableName_nodeID_dict


# 动态生成任务采集指标表
def make_classes(table_dict):
    from sqlalchemy import Column, Integer, Unicode, create_engine
    engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
    Base = declarative_base(engine)
    task_dict = globals()
    task_dict.clear()
    for tableName,params in table_dict.items():
        attrdict = dict(__tablename__=tableName)
        attrdict['ID'] = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
        attrdict['SampleTime'] = Column(Unicode(50))
        for param in params:
            attrdict[param] = Column(Unicode(30), nullable=True)
        task_dict[tableName] = type(tableName, (Base,), attrdict)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return task_dict

def make_dynamic_classes():
    tableName_list = get_tableName()
    table_dict = get_dict(tableName_list)
    task_dict = make_classes(table_dict)
    return task_dict


# {'tableone': ['i=2258'], 'two': ['i=2262', 'i=2260'], 'Nono': ['i=2259', 'i=2263', 'i=2260']}
# 生成表单的执行语句

