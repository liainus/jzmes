from MES import db_session
import xlrd
from constant import constant
from Model.core import QualityControlTree

def read_Excel(file_dir):
    # 打开文件
    workbook = xlrd.open_workbook(file_dir)
    if workbook:
        # 获取所有sheet
        # print(workbook.sheet_names())# [u'sheet1', u'sheet2']
        # sheet1_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        # sheet1 = workbook.sheet_by_index(0)
        sheet1 = workbook.sheet_by_name('Sheet1')

        # sheet的名称，行数，列数
        print(sheet1.name, sheet1.nrows, sheet1.ncols)

        if sheet1:
            if sheet1.nrows <= 0:
                return
            for row in range(1, sheet1.nrows):
                row_value = sheet1.row_values(row)
                if row_value[0] is None or row_value[0] == '':
                    continue
                db_session.add(QualityControlTree(
                    Name=row_value[0],
                    Note=row_value[1],
                    ParentNode= int(row_value[2])))
                db_session.commit()


    # 获取单元格内容的数据类型
    # print(sheet2.cell(1, 0).ctype)


if __name__ == '__main__':
    file_dir = r'C:\Users\maomao\Desktop\JZZYMES\质量控制-过程连续数据.xlsx'
    read_Excel(file_dir)
