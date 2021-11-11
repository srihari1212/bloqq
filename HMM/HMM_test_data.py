#######################IMPORT LIBRARIES##################################
from pandas import ExcelFile, read_excel
from pandas import datetime
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
import warnings
from hmmlearn.hmm import GaussianHMM
import numpy as np

##################### DIFFERENT COIN FILES ###############################
# coin_file = 'Filecoin_New.xlsx'
# coin_file = 'Genaro_New.xlsx'
# coin_file = 'Sia_New.xlsx'
# coin_file = 'Storj_New.xlsx'
coin_file = '4_RLC.xlsx'

####################### READ EXCEL FILE ##################################
xls = ExcelFile(coin_file)

###################### DATE PARSER #######################################
def parser(x):
	try:
		return datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S')
	except:
		return datetime.strptime(str(x),'%Y-%m-%d')
series = read_excel(xls, 'blocktime', header = 0, parse_dates =[0], index_col = 0, squeeze = True, date_parser = parser)
series = series.fillna(0)

####################### STORE IN ARRAY ###################################
X = series.values

######################### TRAIN TEST SPLIT ###############################
size = int(len(X)*0.80)   	# 80 % - 20 % split
train,test = X[0:size], X[size:len(X)]

############################# RMSE DECLARE ###############################
rmse_test = list()          # RMSE for test data

history = train.reshape(-1,1)

######################## GAUSSIAN HIDDEN MARKOV MODEL ##############
hmm = GaussianHMM(n_components = 7, covariance_type = 'diag', n_iter = 1000)
with warnings.catch_warnings():
	warnings.simplefilter('ignore')
	hmm.fit(history)
####################### FIND AVERAGE RMSE OVER 30 iterations #############
for j in range(1):	

	######################## FOR FINAL RMSE ############################
	pred = list()
	expect = list()	
	num_samples_test = len(test)        # LENGTH OF TEST DATA

	######################## RESHAPE TRAINING DATA #####################
	history = train.reshape(-1,1)

	######################## GAUSSIAN HIDDEN MARKOV MODEL ##############
	hmm = GaussianHMM(n_components = 7, covariance_type = 'diag', n_iter = 1000)
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')
		hmm.fit(history)
	
	######################### GENERATE SAMPLES ########################
	samples_test, _ = hmm.sample(num_samples_test)

	####################### LOOP OVER TEST DATA #######################
	for i in range(len(test)):

		# INTEGER VALUES

		# if round(samples_test[i][0]) < 0:
		# 	pred.append(0)
		# else:
		# 	pred.append(round(samples_test[i][0]))
		
		# DECIMAL VALUES
		if samples_test[i][0] < 0:
			pred.append(0)
		else :
			pred.append(samples_test[i][0])
		
		expect.append(test[i])

		
	rmse_test.append(sqrt(mean_squared_error(pred,expect)))
	print(len(rmse_test))

##################### PRINT AVERAGE RMSE FOR TEST DATA #####################
print(np.array(rmse_test).mean())

