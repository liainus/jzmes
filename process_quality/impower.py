import codecs

f = open("D:/成品皮苷10548.CH2","r")  # 打开txt文件，以‘utf-8’编码读取
line = f.readline()   # 以行的形式进行读取文件
list1 = []
while line:
    a = line.split()
    b = a[:-1]   # 这是选取需要读取的位数
    list1.append(b)  # 将其添加在列表之中
    line = f.readline()
f.close()

for i in list1:
    print(i)