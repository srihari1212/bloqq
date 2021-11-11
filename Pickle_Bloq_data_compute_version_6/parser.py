######################### IMPORT LIBRARIES ########################

from pandas import read_excel,ExcelFile,datetime
import xlwt
from xlwt import Workbook
import re

###################### DATE PARSER ##################################

token = '2_DCP.xlsx'
variable = 'transaction'
sheet = '1'

xls = ExcelFile(token)
def parser(x):
	try:
		return datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S')
	except:
		return datetime.strptime(str(x),'%Y-%m-%d')
series = read_excel(xls,variable, header = 0, parse_dates =[0], index_col = 0, squeeze = True, date_parser = parser)
series = series.fillna(0)

wb = Workbook()
sheet1 = wb.add_sheet(sheet)
for i in range(len(series.index)):
	ind = series.index[i]
	# val = series.values[i]
	z = re.findall('\d\d\d\d-\d\d-\d\d',str(ind))
	sheet1.write(i,0,z)
	# sheet1.write(i,1,series.values[i])
	
wb.save('./DCP.xlsx')