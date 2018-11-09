from MES import db_session
import xlrd
from Model.core import OpcTag

def read_Excel(file_dir):
    # 打开文件
    workbook = xlrd.open_workbook(r'C:\Users\maomao\Desktop\JZZYMES\监视变量.xlsx')
    if workbook:
        # 获取所有sheet
        # print(workbook.sheet_names())# [u'sheet1', u'sheet2']
        # sheet1_name = workbook.sheet_names()[0]
        # 根据sheet索引或者名称获取sheet内容
        # sheet1 = workbook.sheet_by_index(0)
        sheet1 = workbook.sheet_by_name('Sheet1')

        # sheet的名称，行数，列数
        print(sheet1.name, sheet1.nrows, sheet1.ncols)
        count = 0
        while 1:
            count += 1
            if count<= sheet1.nrows:
                rows = sheet1.row_values(count)# ['SY系统运行时间', '运行时间', 's']
                print(count)
                if rows[0] is None or rows[0] == '':
                        continue
                db_session.add(OpcTag(
                    NodeID= 't|'+ rows[0],
                    Note=rows[1],
                    Unit=rows[2]))
                db_session.commit()



    # 获取单元格内容的数据类型
    # print(sheet2.cell(1, 0).ctype)


if __name__ == '__main__':
    file_dir = r'C:\Users\maomao\Desktop\JZZYMES\监视变量.xlsx'
    read_Excel(file_dir)
