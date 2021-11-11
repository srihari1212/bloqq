import xlrd
import numpy as np
import pickle
def getDataFromXL(fileName,sheetIndex):
    try:
        contexts=[]
        #print(fileName)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        #Open excel workbook and first sheet
        wb = xlrd.open_workbook(fileName)
        sh = wb.sheet_by_index(sheetIndex)
        #Read rows containing labels and units
        rows=sh.nrows; cols=sh.ncols
        #print("Rows|",sh.nrows," Columns|",sh.ncols)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        contexts = [None] * (cols)
        #read column by column and store in list
        for colnum in range(cols):
            tempArray = sh.col_values(colnum, start_rowx=0, end_rowx=None)
            #print(tempArray)
            T=[]
            for item in tempArray:
                T.append(str(item))

            contexts[colnum] = T
            #print("............................................")
            #print("Column:",colnum,"\n",T)
        ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        return(contexts,rows,cols)
    except:
        print("Problem in getDataFromXL",traceback.print_exc())
        return("failure")
###########################################################################################################################
# Reading data Filecoin
filecoin_price,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",0)
filecoin_fees,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",1)
filecoin_blocktime,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",2)
filecoin_fcas,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",3)
filecoin_transection_volume,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",4)
filecoin_exchange_volume,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",5)
filecoin_bandwidth,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",6)
filecoin_storage,_,_=getDataFromXL("Dataset/Filecoin_New.xlsx",7)
# Reading data Filecoin
genaro_price,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",0)
genaro_fees,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",1)
genaro_blocktime,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",2)
genaro_fcas,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",3)
genaro_transection_volume,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",4)
genaro_exchange_volume,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",5)
genaro_bandwidth,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",6)
genaro_storage,_,_=getDataFromXL("Dataset/Genaro_New.xlsx",7)
# Reading data Filecoin
sia_price,_,_=getDataFromXL("Dataset/Sia_New.xlsx",0)
sia_fees,_,_=getDataFromXL("Dataset/Sia_New.xlsx",1)
sia_blocktime,_,_=getDataFromXL("Dataset/Sia_New.xlsx",2)
sia_fcas,_,_=getDataFromXL("Dataset/Sia_New.xlsx",3)
sia_transection_volume,_,_=getDataFromXL("Dataset/Sia_New.xlsx",4)
sia_exchange_volume,_,_=getDataFromXL("Dataset/Sia_New.xlsx",5)
sia_bandwidth,_,_=getDataFromXL("Dataset/Sia_New.xlsx",6)
sia_storage,_,_=getDataFromXL("Dataset/Sia_New.xlsx",7)
# Reading data Filecoin
storj_price,_,_=getDataFromXL("Dataset/Storj_New.xlsx",0)
storj_fees,_,_=getDataFromXL("Dataset/Storj_New.xlsx",1)
storj_blocktime,_,_=getDataFromXL("Dataset/Storj_New.xlsx",2)
storj_fcas,_,_=getDataFromXL("Dataset/Storj_New.xlsx",3)
storj_transection_volume,_,_=getDataFromXL("Dataset/Storj_New.xlsx",4)
storj_exchange_volume,_,_=getDataFromXL("Dataset/Storj_New.xlsx",5)
storj_bandwidth,_,_=getDataFromXL("Dataset/Storj_New.xlsx",6)
storj_storage,_,_=getDataFromXL("Dataset/Storj_New.xlsx",7)

# storing data in a pickle
filecoin_data=[filecoin_price,filecoin_fees,filecoin_blocktime,filecoin_fcas,filecoin_transection_volume,filecoin_exchange_volume,filecoin_bandwidth,filecoin_storage]
genaro_data=[genaro_price,genaro_fees,genaro_blocktime,genaro_fcas,genaro_transection_volume,genaro_exchange_volume,genaro_bandwidth,genaro_storage]
sia_data=[sia_price,sia_fees,sia_blocktime,sia_fcas,sia_transection_volume,sia_exchange_volume,sia_bandwidth,sia_storage]
storj_data=[storj_price,storj_fees,storj_blocktime,storj_fcas,storj_transection_volume,storj_exchange_volume,storj_bandwidth,storj_storage]

dataset=[filecoin_data,genaro_data,sia_data,storj_data]


filecoin_price,filecoin_fees,filecoin_blocktime,filecoin_fcas,filecoin_transection_volume,filecoin_exchange_volume,filecoin_bandwidth,filecoin_storage=dataset[0]
p=max(len(filecoin_price[0]),len(filecoin_fees[0]),len(filecoin_blocktime[0]),len(filecoin_fcas[0]),len(filecoin_transection_volume[0]),len(filecoin_exchange_volume[0]),len(filecoin_bandwidth[0]),len(filecoin_storage[0]))
q=max(len(genaro_price[0]),len(genaro_fees[0]),len(genaro_blocktime[0]),len(genaro_fcas[0]),len(genaro_transection_volume[0]),len(genaro_exchange_volume[0]),len(genaro_bandwidth[0]),len(genaro_storage[0]))
r=max(len(sia_price[0]),len(sia_fees[0]),len(sia_blocktime[0]),len(sia_fcas[0]),len(sia_transection_volume[0]),len(sia_exchange_volume[0]),len(sia_bandwidth[0]),len(sia_storage[0]))
s=max(len(storj_price[0]),len(storj_fees[0]),len(storj_blocktime[0]),len(storj_fcas[0]),len(storj_transection_volume[0]),len(storj_exchange_volume[0]),len(storj_bandwidth[0]),len(storj_storage[0]))
print(p,q,r,s)
print(len(filecoin_price[0]),len(filecoin_fees[0]),len(filecoin_blocktime[0]),len(filecoin_fcas[0]),len(filecoin_transection_volume[0]),len(filecoin_exchange_volume[0]),len(filecoin_bandwidth[0]),len(filecoin_storage[0]))
print(len(genaro_price[0]),len(genaro_fees[0]),len(genaro_blocktime[0]),len(genaro_fcas[0]),len(genaro_transection_volume[0]),len(genaro_exchange_volume[0]),len(genaro_bandwidth[0]),len(genaro_storage[0]))
print(len(sia_price[0]),len(sia_fees[0]),len(sia_blocktime[0]),len(sia_fcas[0]),len(sia_transection_volume[0]),len(sia_exchange_volume[0]),len(sia_bandwidth[0]),len(sia_storage[0]))
print(len(storj_price[0]),len(storj_fees[0]),len(storj_blocktime[0]),len(storj_fcas[0]),len(storj_transection_volume[0]),len(storj_exchange_volume[0]),len(storj_bandwidth[0]),len(storj_storage[0]))

# filecoin_data=[];genaro_data=[];sia_data=[];storj_data=[]
# for i in range(0,len(filecoin_price[0])):
#     filecoin_data.append([filecoin_price[0][i],filecoin_price[1][i],filecoin_fees[1][i],filecoin_blocktime[1][i],filecoin_fcas[1][i],filecoin_transection_volume[1][i],filecoin_exchange_volume[1][i],filecoin_bandwidth[1][i],filecoin_bandwidth[2][i],filecoin_storage[1][i]])
#     genaro_data.append([genaro_price[0][i],genaro_price[1][i],genaro_fees[1][i],genaro_blocktime[1][i],genaro_fcas[1][i],genaro_transection_volume[1][i],genaro_exchange_volume[1][i],genaro_bandwidth[1][i],genaro_bandwidth[2][i],genaro_storage[1][i]])
#     sia_data.append()
#     storj_data.append()

filecoin_data=[filecoin_price[0],filecoin_price[1],filecoin_fees[1],filecoin_blocktime[1],filecoin_fcas[1],filecoin_transection_volume[1],filecoin_exchange_volume[1],filecoin_bandwidth[1],filecoin_bandwidth[2],filecoin_storage[1]]
genaro_data=[genaro_price[0],genaro_price[1],genaro_fees[1],genaro_blocktime[1],genaro_fcas[1],genaro_transection_volume[1],genaro_exchange_volume[1],genaro_bandwidth[1],genaro_bandwidth[2],genaro_storage[1]]
sia_data=[sia_price[0],sia_price[1],sia_fees[1],sia_blocktime[1],sia_fcas[1],sia_transection_volume[1],sia_exchange_volume[1],sia_bandwidth[1],sia_bandwidth[2],sia_storage[1]]
storj_data=[storj_price[0],storj_price[1],storj_fees[1],storj_blocktime[1],storj_fcas[1],storj_transection_volume[1],storj_exchange_volume[1],storj_bandwidth[1],storj_bandwidth[2],storj_storage[1]]


composite_dataset=[filecoin_data,genaro_data,sia_data,storj_data]
with open('dataset.pkl', 'wb') as f:
    pickle.dump(composite_dataset,f)

#load pickle
with open('dataset.pkl', 'rb') as f:
    datset=pickle.load(f)

# for i in range(0,len(filecoin_data[0])):
#     for j in range(0,10):
#         print(filecoin_data[i][j],genaro_data[i][j],sia_data[i][j],storj_data[i][j])