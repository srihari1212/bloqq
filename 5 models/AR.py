# SES example
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pandas import ExcelFile, read_excel
from pandas import datetime
from sklearn.metrics import mean_squared_error
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
import time

##################### DIFFERENT COIN FILES ###############################
coin_file = '1_SNM.xlsx'

####################### READ EXCEL FILE ##################################
xls = ExcelFile(coin_file)

###################### DATE PARSER #######################################
def parser(x):
	try:
		return datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S')
	except:
		return datetime.strptime(str(x),'%Y-%m-%d')
series = read_excel(xls, 'deals', header = 0, parse_dates =[0], index_col = 0, squeeze = True, date_parser = parser)
series = series.fillna(0)

####################### STORE IN ARRAY ###################################
X = series.values

######################### TRAIN TEST SPLIT ##############################
size = int(len(X)*0.80)
train,test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()
expectations = list()
rmse = list()
######################### 1. AR MODEL #######################################
# start = time.time()
# for i in range(28):
#     # fit model
#     model = AR(history)
#     model_fit = model.fit()
#     pred = (time.time() - start)
#     print('Train time : %.3f' %pred)
#     # make prediction
#     yhat = model_fit.predict(len(history), len(history))
#     # for integer variables
#     # yhat = round(yhat[0])
#     history.append(yhat)
#     predictions.append(yhat)
#     expectations.append(test[i])
#     rmse.append(sqrt(mean_squared_error(predictions,expectations)))
# end = time.time() - start
# print('Prediction time : %.3f'%end)
# RMSE = sqrt(mean_squared_error(predictions, expectations))
# print('RMSE %.3f %.3f %.3f %.3f'%(rmse[6],rmse[13],rmse[20],rmse[27]))

######################### 2. MA MODEL #######################################
# start = time.time()
# for i in range(28):
#     # fit model
#     model = ARMA(history, order = (0,1))
#     model_fit = model.fit(disp = False)
#     print('Training time :%.3f'%(time.time() - start))
#     # make prediction
#     yhat = model_fit.predict(len(history), len(history))
#     # for integer variables
#     # yhat = round(yhat[0])
#     history.append(yhat)
#     predictions.append(yhat)
#     expectations.append(test[i])
#     rmse.append(sqrt(mean_squared_error(predictions,expectations)))
  
# end = time.time() - start
# print('Prediction time : %.3f'%end)
# RMSE = sqrt(mean_squared_error(predictions, expectations))
# print('RMSE %.3f %.3f %.3f %.3f'%(rmse[6],rmse[13],rmse[20],rmse[27]))

######################### 3. ARMA MODEL #######################################
# start = time.time()
# for i in range(28):
#     # fit model
#     model = ARMA(history, order = (5,1))
#     model_fit = model.fit(disp = False)
#     print('Training time %.3f' %(time.time()-start))
#     # make prediction
#     yhat = model_fit.predict(len(history), len(history))
#     # for integer variables
#     yhat = round(yhat[0])
#     history.append(yhat)
#     predictions.append(yhat)
#     expectations.append(test[i])
#     rmse.append(sqrt(mean_squared_error(predictions,expectations)))
  
# end = time.time() - start
# print('Prediction time : %.3f'%end)
# RMSE = sqrt(mean_squared_error(predictions, expectations))
# print('RMSE %.3f %.3f %.3f %.3f'%(rmse[6],rmse[13],rmse[20],rmse[27]))

######################### 4. Simple exponential smoothing MODEL #######################################
# start = time.time()
# for i in range(28):
#     # fit model
#     model = SimpleExpSmoothing(history)
#     model_fit = model.fit()
#     print('Training time %.3f' %(time.time()-start))
#     # make prediction
#     yhat = model_fit.predict(len(history), len(history))
#     # for integer variables
#     # yhat = round(yhat[0])
#     history.append(yhat)
#     predictions.append(yhat)
#     expectations.append(test[i])
#     rmse.append(sqrt(mean_squared_error(predictions,expectations)))

  
# end = time.time() - start
# print('Prediction time : %.3f'%end)
# RMSE = sqrt(mean_squared_error(predictions, expectations))
# print('RMSE %.3f %.3f %.3f %.3f'%(rmse[6],rmse[13],rmse[20],rmse[27]))
######################### 5. Holt winters exponential smoothing MODEL #######################################
start = time.time()
for i in range(28):
    # fit model
    model = ExponentialSmoothing(history)
    model_fit = model.fit()
    print('Training time %.3f' %(time.time()-start))
    # make prediction
    yhat = model_fit.predict(len(history), len(history))
    # for integer variables
    yhat = round(yhat[0])
    history.append(yhat)
    predictions.append(yhat)
    expectations.append(test[i])
    rmse.append(sqrt(mean_squared_error(predictions,expectations)))
  
end = time.time() - start
print('Prediction time : %.3f'%end)
RMSE = sqrt(mean_squared_error(predictions, expectations))
print('RMSE %.3f %.3f %.3f %.3f'%(rmse[6],rmse[13],rmse[20],rmse[27]))