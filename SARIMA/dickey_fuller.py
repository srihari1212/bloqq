####################### IMPORT LIBRARIES #################################
import numpy as np
import pandas as pd
import matplotlib.pylab
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 20,16

import warnings
import itertools
warnings.filterwarnings('ignore') # specify to ignore warning messages

from pandas import ExcelFile, read_excel
from pandas import datetime
from matplotlib import pyplot
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_pacf
from sklearn.metrics import mean_squared_error
from math import sqrt

import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

##################### DIFFERENT COIN FILES ###############################
coin_file = '1_SNM.xlsx'
# coin_file = '2_DCP.xlsx' # transaction, exchange
# coin_file = '3_GNT.xlsx' # all
# coin_file = '4_RLC.xlsx'

####################### READ EXCEL FILE ##################################
xls = ExcelFile(coin_file)


def function(attribute, variable):
####################### TIME SERIES DATA RETRIEVE #####################
    ###################### DATE PARSER #######################################
    def parser(x):
        try:
            return datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S')
        except:
            return datetime.strptime(str(x),'%Y-%m-%d')
    df = pd.read_excel(xls, attribute, header = 0, parse_dates =[0], index_col = 0, squeeze = True, date_parser = parser)
    df = df.fillna(0)
    df = df.to_frame()

    ######################## PARSE DATA ##########################################
    print(df.head(5))
    print(df.info())

    ########################### DATA VISUALIZE ###################################
    fig, ax = plt.subplots()
    df.plot(y=attribute, ax = ax, title=attribute, fontsize = 20)
    ax.set_xlabel('Time')
    ax.set_ylabel(attribute)
    ax.xaxis.label.set_size(20)
    ax.yaxis.label.set_size(20)
    ax.legend(fontsize = 8)

    plt.show()

    ############################ GRAPHICALLY TEST STATIONARITY ######################
    def TestStationaryPlot(ts):
        rol_mean = ts.rolling(window = 12, center = False).mean()
        rol_std = ts.rolling(window = 12, center = False).std()
        
        plt.plot(ts, color = 'blue',label = 'Original Data')
        plt.plot(rol_mean, color = 'red', label = 'Rolling Mean')
        plt.plot(rol_std, color ='black', label = 'Rolling Std')
        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)
        
        plt.xlabel('Time', fontsize = 25)
        plt.ylabel(attribute, fontsize = 25)
        plt.legend(loc='best', fontsize = 25)
        plt.title('Rolling Mean & Standard Deviation', fontsize = 25)
        plt.show(block= True)

    ######################## TEST STATIONARITY DICKEY FULLER ###################

    def TestStationaryAdfuller(ts, cutoff = 0.01):
        ts_test = adfuller(ts, autolag = 'AIC')
        ts_test_output = pd.Series(ts_test[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
        
        for key,value in ts_test[4].items():
            ts_test_output['Critical Value (%s)'%key] = value
        print(ts_test_output)
        
        if ts_test[1] <= cutoff:
            print("Strong evidence against the null hypothesis, reject the null hypothesis. Data has no unit root, hence it is stationary")
        else:
            print("Weak evidence against null hypothesis, time series has a unit root, indicating it is non-stationary ")


    TestStationaryPlot(df)
    TestStationaryAdfuller(df[attribute])

    ############################## TRANSFORM THE DATASET TO STATIONARY ##############
    mte = df[attribute]
    ############################### 1. MOVING AVERAGE and DICKEY FULLER TEST ########
    moving_avg = mte.rolling(12).mean()
    plt.plot(mte)
    plt.plot(moving_avg, color='red')
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.xlabel('Time', fontsize = 25)
    plt.ylabel(attribute, fontsize = 25)
    plt.title(variable, fontsize = 25)
    plt.show()

    mte_moving_avg_diff = mte - moving_avg
    mte_moving_avg_diff.head(13)

    mte_moving_avg_diff.dropna(inplace=True)
    TestStationaryPlot(mte_moving_avg_diff)

    TestStationaryAdfuller(mte_moving_avg_diff)

    ############################# 2. DIFFERENCING ############################
    mte_first_difference = mte - mte.shift(1)  
    TestStationaryPlot(mte_first_difference.dropna(inplace=False))
    TestStationaryAdfuller(mte_first_difference.dropna(inplace=False))

    # Seasonal differencing
    mte_seasonal_difference = mte - mte.shift(7)  
    TestStationaryPlot(mte_seasonal_difference.dropna(inplace=False))
    TestStationaryAdfuller(mte_seasonal_difference.dropna(inplace=False))

    mte_seasonal_first_difference = mte_first_difference - mte_first_difference.shift(7)  
    TestStationaryPlot(mte_seasonal_first_difference.dropna(inplace=False))

    TestStationaryAdfuller(mte_seasonal_first_difference.dropna(inplace=False))

    ########################### DECOMPOSING ######################################
    from statsmodels.tsa.seasonal import seasonal_decompose
    decomposition = seasonal_decompose(mte)

    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    plt.subplot(411)
    plt.plot(mte, label='Original')
    plt.legend(loc='best')
    plt.subplot(412)
    plt.plot(trend, label='Trend')
    plt.legend(loc='best')
    plt.subplot(413)
    plt.plot(seasonal,label='Seasonality')
    plt.legend(loc='best')
    plt.subplot(414)
    plt.plot(residual, label='Residuals')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()

    mte_decompose = residual
    mte_decompose.dropna(inplace=True)
    TestStationaryPlot(mte_decompose)
    TestStationaryAdfuller(mte_decompose)

    ###################################### ACF AND PACF ################################
    fig = plt.figure(figsize=(12,8))
    ax1 = fig.add_subplot(211)
    fig = sm.graphics.tsa.plot_acf(mte_seasonal_first_difference.iloc[13:], lags=40, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(mte_seasonal_first_difference.iloc[13:], lags=40, ax=ax2)
    plt.show()

function('deals','SNM')