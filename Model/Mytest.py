import MicroMES.Model.core
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Column,ForeignKey, Table, DateTime, Integer, String
from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode,BigInteger
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy import func
import MicroMES.Model.Global
from collections import Counter
import datetime
import json
import re
import sys
from enum import Enum
from datetime import datetime, date, timedelta
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy_views import CreateView, DropView
from sqlalchemy.sql import select
from prettytable import PrettyTable
import types
from MicroMES.Model.BSFramwork import AlchemyEncoder

#引入mssql数据库引擎
import pymssql

# 创建对象的基类
engine = create_engine(MicroMES.Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
# Session = sessionmaker(bind=engine)
# session = Session()
# Base = declarative_base(engine)

Base = declarative_base(engine)
session = sessionmaker(engine)()

class MaterialBOMQuery:
    def __init__(self,ID, MATName, BatchTotalWeight,BatchSingleMATWeight, Unit, BatchPercentage,Seq,PRName,PUName,MATTypeName):
        # self.Name = Name
        self.ID = ID
        self.MATName = MATName
        self.BatchTotalWeight=BatchTotalWeight
        self.BatchSingleMATWeight = BatchSingleMATWeight
        self.Unit = Unit
        self.BatchPercentage = BatchPercentage
        self.Seq = Seq
        self.PRName= PRName
        self.PUName = PUName
        self.MATTypeName = MATTypeName

    def __repr__(self):
        return repr((self.ID, self.MATName, self.BatchTotalWeight, self.BatchSingleMATWeight, self.Unit,self.BatchPercentage,self.Seq,self.BatchSingleMATWeight,self.PRName,self.PUName,self.MATTypeName))

qDatas = session.query(MicroMES.Model.core.MaterialBOM.ID , MicroMES.Model.core.Material.MATName,
								  MicroMES.Model.core.MaterialBOM.BatchTotalWeight, MicroMES.Model.core.MaterialBOM.BatchSingleMATWeight,
								  MicroMES.Model.core.MaterialBOM.Unit, MicroMES.Model.core.MaterialBOM.BatchPercentage, MicroMES.Model.core.MaterialBOM.Seq,
								  MicroMES.Model.core.ProductRule.PRName, MicroMES.Model.core.ProcessUnit.PUName,MicroMES.Model.core.MaterialType.MATTypeName)\
                    .outerjoin(MicroMES.Model.core.ProductRule,MicroMES.Model.core.MaterialBOM.ProductRuleID == MicroMES.Model.core.ProductRule.ID)\
                    .join(MicroMES.Model.core.ProcessUnit,MicroMES.Model.core.MaterialBOM.PUID == MicroMES.Model.core.ProcessUnit.ID)\
				.join(MicroMES.Model.core.Material,MicroMES.Model.core.MaterialBOM.MATID == MicroMES.Model.core.Material.ID)\
				.join(MicroMES.Model.core.MaterialType,MicroMES.Model.core.MaterialBOM.MATTypeID == MicroMES.Model.core.MaterialType.ID)\
				.filter(MicroMES.Model.core.MaterialBOM.ProductRuleID == 1).all()[0:10]

__listBOM = []
for obj in qDatas:
    a =  MaterialBOMQuery(obj.ID,obj.MATName,obj.BatchTotalWeight,obj.BatchSingleMATWeight,obj.Unit,obj.BatchPercentage,obj.Seq,obj.PRName,obj.PUName,obj.MATTypeName)
    __listBOM.append(a)
json = json.dumps(__listBOM, default=lambda o: o.__dict__, sort_keys=True, indent=4)
print(json)



# x = PrettyTable(["ID", "BatchTotalWeight", "BatchSingleMATWeight", "Unit","BatchPercentage","Seq","PRName","PUName","MATName","MATTypeName"])
#
# import pandas as pd
# # conn = pymssql.connect(host='127.0.0.1', port=1433, user='sa', passwd='Qcsw@123', db='MES')
# conn = conn=pymssql.connect(server='127.0.0.1:1433',user='sa',password='Qcsw@123',database='MES')
# cursor = conn.cursor()
# # cursor.execute("DROP TABLE IF EXISTS test")#必须用cursor才行
#
# sql = "SELECT   MaterialBOM.ID, MaterialBOM.BatchTotalWeight, MaterialBOM.BatchSingleMATWeight, MaterialBOM.Unit, "\
#                 "MaterialBOM.BatchPercentage, MaterialBOM.Seq, MaterialBOM.Grade, Material.MATName, "\
#                 "MaterialType.MATTypeName, ProcessUnit.PUName, ProductRule.PRName "\
# "FROM      MaterialBOM INNER JOIN "\
#                 "Material ON MaterialBOM.MATID = Material.ID INNER JOIN "\
#                 "MaterialType ON MaterialBOM.MATTypeID = MaterialType.ID INNER JOIN "\
#                 "ProcessUnit ON MaterialBOM.PUID = ProcessUnit.ID INNER JOIN "\
#                 "ProductRule ON MaterialBOM.ProductRuleID = ProductRule.ID"
#
# df = pd.read_sql(sql,conn,)
#
# aa=pd.DataFrame(df)

# print (aa)
sRetruen = ""
icount = 0
for obj in qDatas:
     icount = len(obj)
     for x in range(0,icount):
         if isinstance(obj[x], int):
             sRetruen = sRetruen + "\""+obj._fieds[x]+"\":"+str(obj[x])
             print(sRetruen)






