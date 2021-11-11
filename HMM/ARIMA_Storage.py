############IMPORT LIBRARIES#####################################
from pandas import ExcelFile, read_excel
from pandas import datetime
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt

##################### DIFFERENT COIN FILES ###############################
coin_file = 'Filecoin_New.xlsx'
# coin_file = 'Genaro_New.xlsx'
# coin_file = 'Sia_New' # all
# coin_file = 'Storj_New.xlsx'

####################### READ EXCEL FILE ##################################
xls = ExcelFile(coin_file)

###################### DATE PARSER #######################################
def parser(x):
	try:
		return datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S')
	except:
		return datetime.strptime(str(x),'%Y-%m-%d')
series = read_excel(xls, 'storage', header = 0, parse_dates =[0], index_col = 0, squeeze = True, date_parser = parser)
series = series.fillna(0)

####################### STORE IN ARRAY ###################################
X = series.values

############## FOR BANDWIDTH UP AND DOWN ######################
# X = []
# for i in X1:
#     X.append(i[1])

######################### TRAIN TEST SPLIT ##############################
size = int(len(X)*0.80)   					# 80% - 20% split 
train,test = X[0:size], X[size:len(X)]	
history = [x for x in train]				
predictions = list()						# List of predictions
rmse = list()								# List of RMSEs for 28 days
test_sus = list()							# Test data for 28 days

######################### FIT MODEL AND PREDICT ########################
for t in range(len(test)):
	
	############# ARIMA model #################
	model = ARIMA(history, order=(5,1,0))
	model_fit = model.fit(disp=0)

	############## OUTPUT #####################
	output = model_fit.forecast()
	yhat = output[0]

	############# CHECK IF NEGATIVE ###########
	if yhat < 0:
		yhat = 0

	############### LIST OF PREDICTIONS AND TEST DATA ############### 
	predictions.append(yhat)
	test_sus.append(test[t])

	########### APPEND YHAT TO HISTORY ###################
	history.append(yhat)

	##################### RMSE FOR SUSTAINABILITY ################
	rmse.append(sqrt(mean_squared_error(test_sus, predictions)))
	
	############## PRINT PREDICTED AND EXPECTED VALUES ############
	obs = test[t]
	print('predicted=%f, expected=%f' % (yhat, obs))

####################### PRINT FINAL RMSE ###################################
error = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % error)

###################### PRINT RMSE FOR 7th, 14th, 21st and 28th days #########
print('%.3f %.3f %.3f %.3f' %(rmse[6], rmse[13], rmse[20], rmse[27]))

###################### PRINT RANGE OF TEST DATA ###########################
print('%.3f %.3f' %(min(test), max(test)))

