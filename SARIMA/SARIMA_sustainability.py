############################### IMPORt LIBRARIES ###########################
from math import sqrt
from multiprocessing import cpu_count
from joblib import Parallel
from joblib import delayed
from warnings import catch_warnings
from warnings import filterwarnings
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
from pandas import read_csv
from math import sqrt
import numpy as np
from pandas import ExcelFile, read_excel
from pandas import datetime
from matplotlib import pyplot
import time
# one-step sarima forecast

################ COIN FILES #################################################
# coin_file = '1_SNM.xlsx'
# coin_file = '2_DCP.xlsx' # transaction, exchange
# coin_file = '3_GNT.xlsx' # all
coin_file = '4_RLC.xlsx'

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
test_size = int(len(X)*0.20)
###########################################################################

############################### SARIMA FORECAST ############################
def sarima_forecast(history, config):
	order, sorder, trend = config
	# define model

	start1 = time.time()
	model = SARIMAX(history, order=order, seasonal_order=sorder, trend=trend, enforce_stationarity=False, enforce_invertibility=False)
	# fit model
	model_fit = model.fit(disp=False)
	end1 = time.time()
	# make one step forecast
	print('Time taken for training is :')
	print('%.3f' %(end1-start1))
	yhat = model_fit.predict(len(history), len(history))
	return yhat[0]

# root mean squared error or rmse
def measure_rmse(actual, predicted):
	return sqrt(mean_squared_error(actual, predicted))

# split a univariate dataset into train/test sets
def train_test_split(data, n_test):
	return data[:-n_test], data[-n_test:]

# walk-forward validation for univariate data
def walk_forward_validation(data, n_test, cfg):
	predictions = list()
	expectations = list()
	RMSE = list()
	
	# split dataset
	train, test = train_test_split(data, n_test)
	# seed history with training dataset
	history = [x for x in train]
	# step over each time-step in the test set
	start = time.time()
	for i in range(len(test)):
		# fit model and make forecast for history
		yhat = sarima_forecast(history, cfg)
		# store forecast in list of predictions
		################ FOR INTEGER VALUES ##################################
		# yhat = round(yhat)
		predictions.append(yhat) 
		#####################################################################
		# add actual observation to history for the next loop
		history.append(yhat) 
		expectations.append(test[i])
		RMSE.append(measure_rmse(expectations,predictions))
		
	print('The RMSEs for 1st, 2nd, 3rd and 4th weeks are:')
	print('%.3f %.3f %.3f %.3f' %(RMSE[6],RMSE[13],RMSE[20],RMSE[27]))
	end = time.time()
	print('Time taken for prediction is %.3f' %(end - start))

	# estimate prediction error
	error = measure_rmse(test, predictions)
	return error

# score a model, return None on failure
def score_model(data, n_test, cfg, debug=False):
	result = None
	# convert config to a key
	key = str(cfg)
	# show all warnings and fail on exception if debugging
	if debug:
		result = walk_forward_validation(data, n_test, cfg)
	else:
		# one failure during model validation suggests an unstable config
		try:
			# never show warnings when grid searching, too noisy
			with catch_warnings():
				filterwarnings("ignore")
				result = walk_forward_validation(data, n_test, cfg)
		except:
			error = None
	# check for an interesting result
	if result is not None:
		print(' > Model[%s] %.3f' % (key, result))
	return (key, result)

# grid search configs
def grid_search(data, cfg_list, n_test, parallel=True):
	scores = None
	if parallel:
		# execute configs in parallel
		executor = Parallel(n_jobs=cpu_count(), backend='multiprocessing')
		tasks = (delayed(score_model)(data, n_test, cfg) for cfg in cfg_list)
		scores = executor(tasks)
	else:
		scores = [score_model(data, n_test, cfg) for cfg in cfg_list]
	# remove empty results
	scores = [r for r in scores if r[1] != None]
	# sort configs by error, asc
	scores.sort(key=lambda tup: tup[1])
	return scores

# create a set of sarima configs to try
def sarima_configs(seasonal=[0]):
	models = list()
	# define config lists
	p_params = [1]
	d_params = [0]
	q_params = [0]
	t_params = ['ct']
	P_params = [2]
	D_params = [1]
	Q_params = [1]
	m_params = seasonal
	# create config instances
	for p in p_params:
		for d in d_params:
			for q in q_params:
				for t in t_params:
					for P in P_params:
						for D in D_params:
							for Q in Q_params:
								for m in m_params:
									cfg = [(p,d,q), (P,D,Q,m), t]
									models.append(cfg)
	return models

if __name__ == '__main__':
	data = X
	print(data.shape)
	# data split
	n_test = test_size
	# model configs
	cfg_list = sarima_configs(seasonal=[7])
	# grid search
	scores = grid_search(data, cfg_list, n_test)
	print('done')
	# list top 3 configs
	for cfg, error in scores[:3]:
		print(cfg, error)

