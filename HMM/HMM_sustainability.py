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

rmse_sus = list() 			# RMSE for 7th, 14th, 21st and 28th days

####################### FIND AVERAGE RMSE OVER 30 iterations #############
for j in range(30):	

	rmse = list() 				# RMSE for 28 days
	####################### FOR SUSTAINABILITY ANALYSIS#################
	predictions = list()
	expectations = list()
	num_samples = 28

	######################## RESHAPE TRAINING DATA #####################
	history = train.reshape(-1,1)

	######################## GAUSSIAN HIDDEN MARKOV MODEL ##############
	hmm = GaussianHMM(n_components = 7, covariance_type = 'diag', n_iter = 1000)
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')
		hmm.fit(history)
	
	######################### GENERATE SAMPLES ########################
	samples, _ = hmm.sample(num_samples)
	
	####################### LOOP OVER TEST DATA FOR 28 DAYS ##########
	for i in range(28):

		# INTEGER VALUES
		# if round(samples[i][0]) < 0:
		# 	predictions.append(0)
		# else:
		# 	predictions.append(round(samples[i][0]))
		
		# DECIMAL VALUES
		if samples[i][0] < 0:
			predictions.append(0)
		else:
			predictions.append(samples[i][0])
		
		expectations.append(test[i])
		rmse.append(sqrt(mean_squared_error(predictions,expectations)))

	################## APPEND 7th, 14th, 21st and 28th RMSE values ####	
	rmse_sus.append((rmse[6],rmse[13],rmse[20],rmse[27]))
##################### AVERAGE RMSE FOR 7th, 14th, 21st and 28th days ######
rmse_7 = 0; rmse_14 = 0; rmse_21 = 0; rmse_28 = 0
for j in range(30):
	rmse_7  += rmse_sus[j][0]/30.0
	rmse_14 += rmse_sus[j][1]/30.0
	rmse_21 += rmse_sus[j][2]/30.0
	rmse_28 += rmse_sus[j][3]/30.0

##################### PRINT AVERAGE RMSE FOR SUSTAINABILITY ANALYSIS #######
print(rmse_7,rmse_14,rmse_21,rmse_28)


