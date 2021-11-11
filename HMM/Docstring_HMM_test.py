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
def readfile(coin_file, attribute):
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
def train_test_split(X, fraction):
    ''' Function to split the data into training and test set '''
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
    hmm = GaussianHMM(n_components = n_comp, covariance_type = cov_type, n_iter = n_itr)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        hmm.fit(history)
    # Generate samples
    samples_test, _ = hmm.sample(num_samples_test)
    return samples_test 

###################### FUNCTION TO CALCULATE PREDICTIONS AND EXPECTATIONS #############
def pred_expect(test,variable, samples_test, pred, expect):
    ''' Function to calculate predictions and expectations '''
    # Loop over test data 
    for i in range(len(test)):
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
    return pred, expect

############################# FUNCTION TO CALCULATE RMSE ###############################
def rmse(coin_file, attribute,iterations,fraction,n_comp,cov_type,n_itr,var):
    ''' Function to calculate RMSE '''
    X = readfile(coin_file,attribute)
    train,test = train_test_split(X,fraction)
    rmse_test = list()          
    for j in range(iterations):	
        ######################## FOR FINAL RMSE ############################
        pred = list()
        expect = list()	
        num_samples_test = len(test) # number of samples to be generated
        samples_test = GaussHMM(n_comp,cov_type,n_itr,train,num_samples_test)
        pred,expect = pred_expect(test,var,samples_test, pred, expect)       
        rmse_test.append(sqrt(mean_squared_error(pred,expect)))
    return rmse_test

##################### PRINT AVERAGE RMSE FOR TEST DATA #####################
coin_file = '4_RLC.xlsx'    # Filename
attribute = 'exchange'         # attribute 
iterations = 30                 # number of iterations for averaging rmse
fraction = 0.80             # Train - test split
n_comp = 7                    # n_components for Gaussian HMM
cov_type = 'diag'                # covariance_type for Gaussian HMM
n_itr = 1000                  # n_iter for Gaussian HMM     
var = 'float'                 # Integer or Float valued attribute    

start = time.time()
rmse_test = rmse(coin_file, attribute,iterations,fraction,n_comp,cov_type,n_itr,var)
end = time.time()

print('The average RMSE over %d iterations is %.3f' %(iterations,np.array(rmse_test).mean()))
print('The time taken is %.3f seconds' %(end - start))

