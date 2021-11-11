############IMPORT LIBRARIES#####################################
from pandas import ExcelFile, read_excel
from pandas import datetime
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_pacf
from sklearn.metrics import mean_squared_error
from math import sqrt
import numpy as np
import pmdarima as pm
import matplotlib.pyplot as plt

##################### DIFFERENT COIN FILES ###############################
coin_file = '1_SNM.xlsx'
# coin_file = '2_DCP.xlsx' # transaction, exchange
# coin_file = '3_GNT.xlsx' # all
# coin_file = '4_RLC.xlsx'

####################### READ EXCEL FILE ##################################
xls = ExcelFile(coin_file)

###################### DATE PARSER #######################################
def parser(x):
	try:
		return datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S')
	except:
		return datetime.strptime(str(x),'%Y-%m-%d')
series = read_excel(xls, 'exchange', header = 0, parse_dates =[0], index_col = 0, squeeze = True, date_parser = parser)
series = series.fillna(0)

####################### STORE IN ARRAY ###################################
X = series.values

######################### TRAIN TEST SPLIT ##############################
size = int(len(X)*0.80)
train,test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()

######################### SARIMA hyperparameters ############################
# # define model configuration
# my_order = (8, 0, 0)
# my_seasonal_order = (1, 0, 0, 0)

############################### AUTO ARIMA ##################################
# model = pm.auto_arima(X, start_p=5, start_q=0,
# 				#   test='adf',       # use adftest to find optimal 'd'
# 					max_p=5, max_q=0, # maximum p and q
# 				#   m=1,              # frequency of series
# 					d=1,           # let model determine 'd'
# 					seasonal=False,   # No Seasonality
# 					start_P=0, 
# 					D=0, 
# 					trace=True,
# 					error_action='ignore',  
# 					suppress_warnings=True, 
# 					stepwise=True)

######################### FIT MODEL AND PREDICT ########################
for t in range(len(test)):
	
	# ARIMA model
	model = ARIMA(history, order=(5,1,0))
	
	# SARIMA model
	# model = SARIMAX(history, order = my_order, seasonal_order = my_seasonal_order)


	model_fit = model.fit(disp=0)
	output = model_fit.forecast()
	yhat = output[0]

	# for integer values###############
	# yhat1 = round(yhat[0])
	predictions.append(yhat)
	############################
	
	obs = test[t]
	history.append(obs)
	print('predicted=%f, expected=%f' % (yhat, obs))

####################### PRINT RMSE ###################################
error = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % error)

######################### MODEL DIAGNOSTICS ############################
# print(model.summary())
# model.plot_diagnostics(figsize = (10,10))
# plt.show()
######################### PLOT RESULTS ################################
# pyplot.plot(test, label = 'Expected')
# pyplot.plot(predictions, color='red', label = 'Predicted')
# pyplot.ylabel('Deals->')
# pyplot.xlabel('Time   -->')
# pyplot.title('Deals vs. Time: SNM')
# pyplot.grid(True)
# pyplot.legend()
# pyplot.show()
####################################################################


