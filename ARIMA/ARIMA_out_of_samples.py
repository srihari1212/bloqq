#############################IMPORT LIBRARIES##################################################
from pandas import read_csv
from pandas import ExcelFile, read_excel
from pandas import datetime
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt
import numpy as np
import numpy
import warnings
import time

############################# DIFFERENT COIN FILES ###########################################
# coin_file = './1_SNM.xlsx'
# coin_file = './2_DCP.xlsx'
coin_file = './3_GNT.xlsx' # all
# coin_file = './4_RLC.xlsx'

############################# READ EXCEL FILE ###############################################
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

############## FOR BANDWIDTH UP AND DOWN ######################
# X = []
# for i in X1:
#     X.append(i[1])

######################### TRAIN TEST SPLIT 80% - 20%  ##############################
size = int(len(X)*0.80)
train,test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()
expectations = []
RMSE = []

training_start = time.time()
model = ARIMA(history, order=(8,1,2))
model_fit = model.fit(disp=0)
training_end = time.time()
training_time = training_end-training_start

print('Time taken for training is: %.3f seconds'%(training_time))

pred_start = time.time()
######################### FIT MODEL AND PREDICT ########################
for t in range(28):
    model = ARIMA(history, order=(8,1,2))
    model_fit = model.fit(disp=0)

    output = model_fit.forecast()
    yhat = output[0]
    # for integer values###############
    # yhat = round(yhat[0])
    predictions.append(yhat)
    ###################################
    history.append(yhat)

    expectations.append(test[t])
    RMSE.append(sqrt(mean_squared_error(predictions, expectations)))
    warnings.filterwarnings('ignore')

pred_end = time.time()
print('Tme taken for prediction is %.3f seconds' %(pred_end - pred_start))
print('\n The RMSEs for first four weeks are:')
print(RMSE[6],RMSE[13],RMSE[20],RMSE[27])
print ('\n The minimum and maximum values of test data are')
print(min(test))
print(max(test))
