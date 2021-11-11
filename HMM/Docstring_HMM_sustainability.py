####################### IMPORT LIBRARIES ####################################
from pandas import ExcelFile, read_excel
from pandas import datetime
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt
import warnings
from hmmlearn.hmm import GaussianHMM
import numpy as np
import time


####################### FUNCTION TO READ FILE ################################
def readfile(coin_file,attribute):
    ''' Function to read and parse the data '''
    # Read excel file
    xls = ExcelFile(coin_file)
    # Date parser
    def parser(x):
        try:
            return datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S')
        except:
            return datetime.strptime(str(x),'%Y-%m-%d')
    series = read_excel(xls, attribute, header = 0, parse_dates =[0], index_col = 0, squeeze = True, date_parser = parser)
    series = series.fillna(0)
    # Store in array 
    X = series.values
    return X

###################### FUNCTION TO SPLIT THE DATA INTO TRAINING AND TEST SET #######
def train_test_split(X,fraction):
    ''' Function to split the data into training and test sets '''
    # Train test split
    size = int(len(X)*fraction)   	
    train,test = X[0:size], X[size:len(X)]
    return train,test

##################### FUNCTION TO DEFINE GAUSSIAN HIDDEN MARKOV MODEL ###############
def GaussHMM(n_comp,cov_type,n_itr,train,num_samples_test):
    ''' Function to define Gaussian Hidden Markov Model '''
    # Reshape training data
    history = train.reshape(-1,1)
    # Gaussian hidden markov model
    start = time.time()
    hmm = GaussianHMM(n_components = n_comp, covariance_type = cov_type, n_iter = n_itr)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        hmm.fit(history)
    end = time.time()
    print('Time taken for training is %.3f' %(end - start))
    # Generate samples
    samples_test, _ = hmm.sample(num_samples_test)
    return samples_test 

###################### FUNCTION TO CALCULATE RMSE ###############################
def pred_expect(num_samples,variable,samples_test,pred,expect,test,rmse):
    ''' Function to calculate rmse '''
    # Loop over test data 
    for i in range(num_samples):
        # Integer values
        if variable == 'int':
            if round(samples_test[i][0]) < 0:
                pred.append(0)
            else:
                pred.append(round(samples_test[i][0]))  
        # decimal values
        else:
            if samples_test[i][0] < 0:
                pred.append(0)
            else:
                pred.append(samples_test[i][0])
        expect.append(test[i])
        rmse.append(sqrt(mean_squared_error(pred,expect)))
    return rmse

############################# FUNCTION TO CALCULATE RMSE OVER ITERATIONS#############
def rmse(coin_file,attribute,num_samples,iterations,fraction,n_comp,cov_type,n_itr,var):
    ''' Function to calculate RMSE over iterations '''
    X = readfile(coin_file,attribute)
    train,test = train_test_split(X,fraction)
    rmse_sus = list()      #rmse for sustainability analysis    
    for j in range(iterations):	
        rmse = list()
        pred = list()
        expect = list()	
        num_samples_test = num_samples
        samples_test = GaussHMM(n_comp,cov_type,n_itr,train,num_samples_test)
        rmse = pred_expect(num_samples,var,samples_test,pred,expect,test,rmse)       
        rmse_sus.append((rmse[6],rmse[13],rmse[20],rmse[27]))
    return rmse_sus

##################### AVERAGE RMSE FOR 7th, 14th, 21st and 28th days ######
def rmse_avg(rmse_sus,iterations):
    ''' function to calculate RMSE for 7th, 14th, 21st and 28th days '''
    rmse_7 = 0; rmse_14 = 0; rmse_21 = 0; rmse_28 = 0
    for j in range(iterations):
	    rmse_7  += rmse_sus[j][0]/float(iterations)
	    rmse_14 += rmse_sus[j][1]/float(iterations)
	    rmse_21 += rmse_sus[j][2]/float(iterations)
	    rmse_28 += rmse_sus[j][3]/float(iterations)
    return rmse_7, rmse_14, rmse_21, rmse_28
##################### PRINT AVERAGE RMSE FOR TEST DATA #####################
coin_file = '4_RLC.xlsx'    # Filename
attribute = 'exchange'         # attribute 
iterations = 30            # number of iterations for averaging rmse
fraction = 0.80             # Train - test split
n_comp = 7                  # n_components for Gaussian HMM
cov_type = 'diag'           # covariance_type for Gaussian HMM
n_itr = 1000                # n_iter for Gaussian HMM     
var = 'float'               # Integer or Float valued attribute    
num_samples = 28            # Number of days to predict

start = time.time()
rmse_sus = rmse(coin_file,attribute,num_samples,iterations,fraction,n_comp,cov_type,n_itr,var)
rmse_7,rmse_14,rmse_21,rmse_28 = rmse_avg(rmse_sus,iterations)
end = time.time()

print('The RMSE for 7 days, 14 days, 21 days and 28 days over %d iterations is %.3f %.3f %.3f %.3f respectively' %(iterations,rmse_7,rmse_14,rmse_21,rmse_28))
print('The time taken is %.3f seconds' %(end - start))

