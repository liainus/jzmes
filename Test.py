from Model.system import Role,Organization
from Model.BSFramwork import AlchemyEncoder
import Model.Global
import json
import sqlalchemy
import time,datetime,decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Column,ForeignKey, Table, DateTime, Integer, String
from sqlalchemy import func
import string
import re
from collections import Counter
import configparser

engine = create_engine(Model.Global.GLOBAL_DATABASE_CONNECT_STRING, deprecate_large_types=True)
Session = sessionmaker(bind=engine)
session = Session()

# def CreateOrganiztionTree(id):
#     sRe = ""
#     try:
#         orgs = session.query(Organization).filter_by(ParentNode = id).all()
#         if orgs.count() > 0:
#             for org in orgs:
#                 if org.ParentNode
#         else:
#             sRe = "{"+"""OrganizationName""" + ":" + orgs.OrganizationName + ","+ """image"""+":" +  "Moreno", "image": "antonio.jpg", "title": "团队领导", "colorScheme": "#1696d3"}
#
#
#     except Exception as e:
#     return 'OK'

# import json
# source=[
#     {"name":"my document","id":1 , "parentid": 0 },
#     {"name":"photos","id":2 , "parentid": 1 },
#     {"name":"Friend","id":3 , "parentid": 2 },
#     {"name":"Wife","id":4 , "parentid": 2 },
#     {"name":"Company","id":5 , "parentid": 2 },
#     {"name":"Program Files","id":6 , "parentid": 1 },
#     {"name":"intel","id":7 , "parentid": 6 },
#     {"name":"java","id":8 , "parentid": 6 },
# ]
#
# def getChildren(id=0):
#     sz=[]
#     for obj in source:
#         if obj["parentid"] ==id:
#             sz.append({"id":obj["id"],"text":obj["name"],"children":getChildren(obj["id"])})
#     return sz
#
# def getOrganizationChildren(id=0):
#     sz=[]
#     orgs = session.query(Organization).filter().all()
#     for obj in orgs:
#         if obj.ParentNode ==id:
#             sz.append({"id":obj.ID,"title":obj.OrganizationName,"items":getOrganizationChildren(obj.ID)})
#     return sz
#
# data = getOrganizationChildren(0)
# jsondata = json.dumps(data)
# print (jsondata)
class myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    # 这里重写了optionxform方法，直接返回选项名
    def optionxform(self, optionstr):
        return optionstr

def replaceTpye(s,config,types,import_str_tail):
    for type in types:
        if type:
            pat = '&'+type
            import_str_tail.append(','+config['colType'][type])
            s = re.sub(pat,config['colType'][type],s)
    return s,import_str_tail

def MakeHTMLTableField(self):
    cp = myconf()
    cf = cp.read("Htmlcfg.ini")
    secs = cp.sections()
    options = cp.options("HTMLTableField")
    notes = ""
    for opt in options:
        val = cp.get("HTMLTableField", opt)
        valflag = "i" + opt
        notes += "                <tr>\n"
        notes += "                    <td class=\"kv-label\">" + val + "</td>\n"
        notes += "                    <td class=\"kv-content\">\n"
        notes += "                        <input  name=\"" + valflag + "\" type=\"text\" class=\"textbox-text validatebox-text textbox-prompt\" autocomplete=\"off\" placeholder="">\n"
        notes += "                    </td>\n"
        notes += "                </tr>\n"
    return notes

def MakeJSColumnField(self):
    cp = myconf()
    cf = cp.read("Htmlcfg.ini")
    secs = cp.sections()
    options = cp.options("HTMLTableField")
    notes = "            {\n"
    notes +="                field: \'ck\',\n"
    notes +="                width: 100,\n"
    notes +="                checkbox: true,\n"
    notes +="                align: 'center',\n"
    notes +="            },\n"
    for opt in options:
        val = cp.get("HTMLTableField", opt)
        notes += "            {\n"
        notes += "                field: \'" + opt + "\',\n"
        notes += "                title: \'" + val + "\',\n"
        notes += "                align: 'center',\n"
        notes += "                width: 200\n"
        notes += "            },\n"
    return notes[:-2]

def MakeJScreateValue(self):
    cp = myconf()
    cf = cp.read("Htmlcfg.ini")
    secs = cp.sections()
    options = cp.options("HTMLTableField")
    notes = ""
    for opt in options:
        val = cp.get("HTMLTableField", opt)
        valflag = "i" + opt
        notes += "            $('input[name=\"{inputTag}\"]').val("");\n"
        notes = notes.replace("{inputTag}", valflag)
    return notes

def MakeJSupdateValue(self):
    cp = myconf()
    cf = cp.read("Htmlcfg.ini")
    secs = cp.sections()
    options = cp.options("HTMLTableField")
    notes = ""
    for opt in options:
        val = cp.get("HTMLTableField", opt)
        valflag = "i" + opt
        notes += "                    $('input[name=\"{updatetag1}\"]').val(row.{updatetag2});\n"
        notes = notes.replace("{updatetag1}", valflag)
        notes = notes.replace("{updatetag2}",val)
    return notes

def MakeCode(self):
    cp = myconf()
    cf = cp.read("Htmlcfg.ini")
    secs = cp.sections()
    options = cp.options("TableField")
    notesCreate = ""
    notesUpdate = ""
    notesJS01 = ""
    notesJS02 = ""
    notesJS03 = ""
    notesJS04 = ""
    for opt in options:
        val = cp.get("TableField", opt)
        notesCreate = "PDUnitName = odata['"+ opt + "'],\n"
        notesUpdate = "oclass." + opt + "= odata['" + opt + "']\n"
        notesJS01  = MakeHTMLTableField()
        notesJS02 = MakeJSColumnField()
        notesJS03 = MakeJScreateValue()
        notesJS04 = MakeJSupdateValue()
        print(notesCreate)
        print ("***********************************")
        print(notesUpdate)
        print ("***********************************")
        print(notesJS01)
        print ("***********************************")
        print(notesJS02)
        print ("***********************************")
        print(notesJS03)
        print ("***********************************")
        print(notesJS04)
        print("***********************************")
    return "OK"

if __name__ == '__main__':
    str = ""
    cp = myconf()
    cf = cp.read("Htmlcfg.ini")
    secs = cp.sections()
    options = cp.options("TableField")
    notesCreate = ""
    notesUpdate = ""
    notesJS01 = ""
    notesJS02 = ""
    notesJS03 = ""
    notesJS04 = ""
    for opt in options:
        val = cp.get("TableField", opt)
        notesCreate = "PDUnitName = odata['" + opt + "'],\n"
        notesUpdate = "oclass." + opt + "= odata['" + opt + "']\n"
        notesJS01 = MakeHTMLTableField()
        notesJS02 = MakeJSColumnField()
        notesJS03 = MakeJScreateValue()
        notesJS04 = MakeJSupdateValue()
        print(notesCreate)
        print("***********************************")
        print(notesUpdate)
        print("***********************************")
        print(notesJS01)
        print("***********************************")
        print(notesJS02)
        print("***********************************")
        print(notesJS03)
        print("***********************************")
        print(notesJS04)
        print("***********************************")





