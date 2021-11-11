import xlrd
import numpy as np
import pickle
# def getDataFromXL(fileName,sheetIndex):
#     try:
#         contexts=[]
#         #print(fileName)
#         ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#         #Open excel workbook and first sheet
#         wb = xlrd.open_workbook(fileName)
#         sh = wb.sheet_by_index(sheetIndex)
#         #Read rows containing labels and units
#         rows=sh.nrows; cols=sh.ncols
#         #print("Rows|",sh.nrows," Columns|",sh.ncols)
#         ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#         contexts = [None] * (cols)
#         #read column by column and store in list
#         for colnum in range(cols):
#             tempArray = sh.col_values(colnum, start_rowx=0, end_rowx=None)
#             #print(tempArray)
#             T=[]
#             for item in tempArray:
#                 T.append(str(item))

#             contexts[colnum] = T
#             #print("............................................")
#             #print("Column:",colnum,"\n",T)
#         ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#         return(contexts,rows,cols)
#     except:
#         print("Problem in getDataFromXL",traceback.print_exc())
#         return("failure")
# ###########################################################################################################################
# # Reading data SNM
# SNM_deals,_,_=getDataFromXL("1_SNM.xlsx",0)
# SNM_price,_,_=getDataFromXL("1_SNM.xlsx",1)
# SNM_instancesize,_,_=getDataFromXL("1_SNM.xlsx",2)
# SNM_gpu,_,_=getDataFromXL("1_SNM.xlsx",3)
# SNM_fcas,_,_=getDataFromXL("1_SNM.xlsx",4)
# SNM_blocktime,_,_=getDataFromXL("1_SNM.xlsx",5)
# SNM_transaction,_,_=getDataFromXL("1_SNM.xlsx",6)
# SNM_exchange,_,_=getDataFromXL("1_SNM.xlsx",7)
# # Reading data DCP
# DCP_deals,_,_=getDataFromXL("2_DCP.xlsx",0)
# DCP_price,_,_=getDataFromXL("2_DCP.xlsx",1)
# DCP_instancesize,_,_=getDataFromXL("2_DCP.xlsx",2)
# DCP_gpu,_,_=getDataFromXL("2_DCP.xlsx",3)
# DCP_fcas,_,_=getDataFromXL("2_DCP.xlsx",4)
# DCP_blocktime,_,_=getDataFromXL("2_DCP.xlsx",5)
# # Reading data GNT
# GNT_deals,_,_=getDataFromXL("3_GNT.xlsx",0)
# GNT_price,_,_=getDataFromXL("3_GNT.xlsx",1)
# GNT_instancesize,_,_=getDataFromXL("3_GNT.xlsx",2)
# GNT_gpu,_,_=getDataFromXL("3_GNT.xlsx",3)
# GNT_fcas,_,_=getDataFromXL("3_GNT.xlsx",4)
# GNT_blocktime,_,_=getDataFromXL("3_GNT.xlsx",5)
# GNT_transaction,_,_=getDataFromXL("3_GNT.xlsx",6)
# GNT_exchange,_,_=getDataFromXL("3_GNT.xlsx",7)
# # Reading data RLC
# RLC_deals,_,_=getDataFromXL("4_RLC.xlsx",0)
# RLC_price,_,_=getDataFromXL("4_RLC.xlsx",1)
# RLC_instancesize,_,_=getDataFromXL("4_RLC.xlsx",2)
# RLC_gpu,_,_=getDataFromXL("4_RLC.xlsx",3)
# RLC_fcas,_,_=getDataFromXL("4_RLC.xlsx",4)
# RLC_blocktime,_,_=getDataFromXL("4_RLC.xlsx",5)
# RLC_transaction,_,_=getDataFromXL("4_RLC.xlsx",6)
# RLC_exchange,_,_=getDataFromXL("4_RLC.xlsx",7)

# ## date,price, blocktime, fcas, transaction, exchange, deals, instancesize, gpu
# #### LIST
# SNM_data=[SNM_price[0],SNM_price[1],SNM_blocktime[1],SNM_fcas[1],SNM_transaction[1],SNM_exchange[1],SNM_deals[1],SNM_instancesize[1],SNM_gpu[1]]
# DCP_data=[DCP_price[0],DCP_price[1],DCP_blocktime[1],DCP_fcas[1],SNM_transaction[1],SNM_exchange[1],DCP_deals[1],DCP_instancesize[1],DCP_gpu[1]]
# GNT_data=[GNT_price[0],GNT_price[1],GNT_blocktime[1],GNT_fcas[1],GNT_transaction[1],GNT_exchange[1],GNT_deals[1],GNT_instancesize[1],GNT_gpu[1]]
# RLC_data=[RLC_price[0],RLC_price[1],RLC_blocktime[1],RLC_fcas[1],RLC_transaction[1],RLC_exchange[1],RLC_deals[1],RLC_instancesize[1],RLC_gpu[1]]

# composite_dataset=[SNM_data,DCP_data,GNT_data,RLC_data]

# with open('compute_dataset_start_end_same.pkl', 'wb') as f:
#     pickle.dump(composite_dataset,f)

# load pickle
with open('compute_dataset_start_end_same.pkl', 'rb') as f:
    datset=pickle.load(f)

print(datset[0][1])
