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
# Reading data SNM
SNM_deals,_,_=getDataFromXL("1_SNM.xlsx",0)
SNM_price,_,_=getDataFromXL("1_SNM.xlsx",1)
SNM_instancesize,_,_=getDataFromXL("1_SNM.xlsx",2)
SNM_gpu,_,_=getDataFromXL("1_SNM.xlsx",3)
SNM_fcas,_,_=getDataFromXL("1_SNM.xlsx",4)
SNM_blocktime,_,_=getDataFromXL("1_SNM.xlsx",5)
SNM_transaction,_,_=getDataFromXL("1_SNM.xlsx",6)
SNM_exchange,_,_=getDataFromXL("1_SNM.xlsx",7)
# Reading data DCP
DCP_deals,_,_=getDataFromXL("2_DCP.xlsx",0)
DCP_price,_,_=getDataFromXL("2_DCP.xlsx",1)
DCP_instancesize,_,_=getDataFromXL("2_DCP.xlsx",2)
DCP_gpu,_,_=getDataFromXL("2_DCP.xlsx",3)
DCP_fcas,_,_=getDataFromXL("2_DCP.xlsx",4)
DCP_blocktime,_,_=getDataFromXL("2_DCP.xlsx",5)
# Reading data GNT
GNT_deals,_,_=getDataFromXL("3_GNT.xlsx",0)
GNT_price,_,_=getDataFromXL("3_GNT.xlsx",1)
GNT_instancesize,_,_=getDataFromXL("3_GNT.xlsx",2)
GNT_gpu,_,_=getDataFromXL("3_GNT.xlsx",3)
GNT_fcas,_,_=getDataFromXL("3_GNT.xlsx",4)
GNT_blocktime,_,_=getDataFromXL("3_GNT.xlsx",5)
GNT_transaction,_,_=getDataFromXL("3_GNT.xlsx",6)
GNT_exchange,_,_=getDataFromXL("3_GNT.xlsx",7)
# Reading data RLC
RLC_deals,_,_=getDataFromXL("4_RLC.xlsx",0)
RLC_price,_,_=getDataFromXL("4_RLC.xlsx",1)
RLC_instancesize,_,_=getDataFromXL("4_RLC.xlsx",2)
RLC_gpu,_,_=getDataFromXL("4_RLC.xlsx",3)
RLC_fcas,_,_=getDataFromXL("4_RLC.xlsx",4)
RLC_blocktime,_,_=getDataFromXL("4_RLC.xlsx",5)
RLC_transaction,_,_=getDataFromXL("4_RLC.xlsx",6)
RLC_exchange,_,_=getDataFromXL("4_RLC.xlsx",7)

#### DICTIONARY SNM ###################
snm_deals = {}
for i in range(1,len(SNM_deals[0])):
    snm_deals[SNM_deals[0][i]] = SNM_deals[1][i]

snm_price = {}
for i in range(1,len(SNM_price[0])):
    snm_price[SNM_price[0][i]] = SNM_price[1][i]

snm_instancesize = {}
for i in range(1,len(SNM_instancesize[0])):
    snm_instancesize[SNM_instancesize[0][i]] = SNM_instancesize[1][i]

snm_gpu = {}
for i in range(1,len(SNM_gpu[0])):
    snm_gpu[SNM_gpu[0][i]] = SNM_gpu[1][i]

snm_fcas = {}
for i in range(1,len(SNM_fcas[0])):
    snm_fcas[SNM_fcas[0][i]] = SNM_fcas[1][i]

snm_blocktime = {}
for i in range(1,len(SNM_blocktime[0])):
    snm_blocktime[SNM_blocktime[0][i]] = SNM_blocktime[1][i]

snm_transaction = {}
for i in range(1,len(SNM_transaction[0])):
    snm_transaction[SNM_transaction[0][i]] = SNM_transaction[1][i]

snm_exchange = {}
for i in range(1,len(SNM_exchange[0])):
    snm_exchange[SNM_exchange[0][i]] = SNM_exchange[1][i]

SNM_data=[snm_price,snm_blocktime,snm_fcas,snm_transaction,snm_exchange,snm_deals,snm_instancesize,snm_gpu]

############ DICTIONARY DCP ##########################################
dcp_deals = {}
for i in range(1,len(DCP_deals[0])):
    dcp_deals[DCP_deals[0][i]] = DCP_deals[1][i]

dcp_price = {}
for i in range(1,len(DCP_price[0])):
    dcp_price[DCP_price[0][i]] = DCP_price[1][i]

dcp_instancesize = {}
for i in range(1,len(DCP_instancesize[0])):
    dcp_instancesize[DCP_instancesize[0][i]] = DCP_instancesize[1][i]

dcp_gpu = {}
for i in range(1,len(DCP_gpu[0])):
    dcp_gpu[DCP_gpu[0][i]] = DCP_gpu[1][i]

dcp_fcas = {}
for i in range(1,len(DCP_fcas[0])):
    dcp_fcas[DCP_fcas[0][i]] = DCP_fcas[1][i]

dcp_blocktime = {}
for i in range(1,len(DCP_blocktime[0])):
    dcp_blocktime[DCP_blocktime[0][i]] = DCP_blocktime[1][i]

dcp_transaction = {}
for i in range(1,len(SNM_transaction[0])):
    dcp_transaction[SNM_transaction[0][i]] = SNM_transaction[1][i]

dcp_exchange = {}
for i in range(1,len(SNM_exchange[0])):
    dcp_exchange[SNM_exchange[0][i]] = SNM_exchange[1][i]

DCP_data=[dcp_price,dcp_blocktime,dcp_fcas,snm_transaction,snm_exchange,dcp_deals,dcp_instancesize,dcp_gpu]

############################ DICTIONARY GNT ###############################
gnt_deals = {}
for i in range(1,len(GNT_deals[0])):
    gnt_deals[GNT_deals[0][i]] = GNT_deals[1][i]

gnt_price = {}
for i in range(1,len(GNT_price[0])):
    gnt_price[GNT_price[0][i]] = GNT_price[1][i]

gnt_instancesize = {}
for i in range(1,len(GNT_instancesize[0])):
    gnt_instancesize[GNT_instancesize[0][i]] = GNT_instancesize[1][i]

gnt_gpu = {}
for i in range(1,len(GNT_gpu[0])):
    gnt_gpu[GNT_gpu[0][i]] = GNT_gpu[1][i]

gnt_fcas = {}
for i in range(1,len(GNT_fcas[0])):
    gnt_fcas[GNT_fcas[0][i]] = GNT_fcas[1][i]

gnt_blocktime = {}
for i in range(1,len(GNT_blocktime[0])):
    gnt_blocktime[GNT_blocktime[0][i]] = GNT_blocktime[1][i]

gnt_transaction = {}
for i in range(1,len(GNT_transaction[0])):
    gnt_transaction[GNT_transaction[0][i]] = GNT_transaction[1][i]

gnt_exchange = {}
for i in range(1,len(GNT_exchange[0])):
    gnt_exchange[GNT_exchange[0][i]] = GNT_exchange[1][i]

GNT_data=[gnt_price,gnt_blocktime,gnt_fcas,gnt_transaction,gnt_exchange,gnt_deals,gnt_instancesize,gnt_gpu]

################################# DICTIONARY RLC #################################
rlc_deals = {}
for i in range(1,len(RLC_deals[0])):
    rlc_deals[RLC_deals[0][i]] = RLC_deals[1][i]

rlc_price = {}
for i in range(1,len(RLC_price[0])):
    rlc_price[RLC_price[0][i]] = RLC_price[1][i]

rlc_instancesize = {}
for i in range(1,len(RLC_instancesize[0])):
    rlc_instancesize[RLC_instancesize[0][i]] = RLC_instancesize[1][i]

rlc_gpu = {}
for i in range(1,len(RLC_gpu[0])):
    rlc_gpu[RLC_gpu[0][i]] = RLC_gpu[1][i]

rlc_fcas = {}
for i in range(1,len(RLC_fcas[0])):
    rlc_fcas[RLC_fcas[0][i]] = RLC_fcas[1][i]

rlc_blocktime = {}
for i in range(1,len(RLC_blocktime[0])):
    rlc_blocktime[RLC_blocktime[0][i]] = RLC_blocktime[1][i]

rlc_transaction = {}
for i in range(1,len(RLC_transaction[0])):
    rlc_transaction[RLC_transaction[0][i]] = RLC_transaction[1][i]

rlc_exchange = {}
for i in range(1,len(RLC_exchange[0])):
    rlc_exchange[RLC_exchange[0][i]] = RLC_exchange[1][i]

RLC_data=[rlc_price,rlc_blocktime,rlc_fcas,rlc_transaction,rlc_exchange,rlc_deals,rlc_instancesize,rlc_gpu]


########################### COMPOSITE DATASET ###############################
composite_dataset=[SNM_data,DCP_data,GNT_data,RLC_data]

with open('compute_dataset_dictionary_start_end_same.pkl', 'wb') as f:
    pickle.dump(composite_dataset,f)

############################## CHECK #########################
# cnt = 0
# for i in rlc_gpu:
#     print(i)
#     cnt+=1
#     if cnt > 3:
#         break
# print(rlc_gpu['2019-01-21'])
# print(rlc_gpu)