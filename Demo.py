from flask import Flask, request, Response,render_template
import traceback
import os
import xlrd
import pickle
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
###########################################################################################################################
# Initialize the Flask Application
app = Flask(__name__)
given_date="";number_of_days=-1;selection_table="";estimation_table="";cost_estimation=""
given_storage=-1;given_budget=-1;composit_data=[]
###########################################################################################################################
UPLOAD_FOLDER = os.path.basename('/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
###########################################################################################################################
#load pickle
with open('Dataset/storage_dataset.pkl', 'rb') as f:
    datset=pickle.load(f)
filecoin_data,genaro_data,sia_data,storj_data=datset

# Reading Compute Dataset
pickle_file=open('Dataset/compute_dataset.pkl', 'rb')
composite_dataset=pickle.load(pickle_file)
# print(composite_dataset)
snm_array,gnt_array,rlc_array,dcp_array=composite_dataset
###########################################################################################################################
def arima_model(number_of_days,history):
    try:
        predictions = list()
        # print(number_of_days,type(number_of_days))
        ######################### FIT MODEL AND PREDICT ########################
        for t in range(number_of_days):
            model = ARIMA(history, order=(5,1,0))
            model_fit = model.fit(disp=0)
            output = model_fit.forecast()
            yhat = output[0]
            predictions.append(list(yhat)[0])
            #obs = test[t]
            obs=yhat
            history.append(obs)
            #print('predicted=%f, expected=%f' % (yhat, obs))
        return predictions
    except:
        predictions=[-1 for i in range(number_of_days)]
        print("Problem in arima_model",traceback.print_exc())
        return predictions
###########################################################################################################################
def get_arima_prediction(data,given_date,number_of_days,variable_names):
    try:
        token_names=['Filecoin','Genaro','Sia','Storj']
        # print(number_of_days,type(number_of_days))
        token_predictions=[]
        for token_id,token in enumerate(data):
            #print('Processing...',token_names[token_id])
            # Processing filecoin data
            variables=token[1:]
            vardate=token[0][1:]
            variable_predictions=[]
            for var_id,variable in enumerate(variables):
                # removing header
                variable=variable[1:]
                # Converting to float
                X=[]
                for item in variable:
                    try:
                        X.append(float(item))
                    except:
                        X.append(-1)
                #print("Predicting for...",variable_names[var_id+1])
                if given_date in vardate:
                    train= X[0:vardate.index(given_date)]
                    test = X[vardate.index(given_date):vardate.index(given_date)+number_of_days]
                    history = [x for x in train]
                    predictions=arima_model(number_of_days,history)
                    #print(predictions)
                    variable_predictions.append(predictions)
            token_predictions.append(variable_predictions)
        return token_predictions
    except:
        print("Problem in get_arima_prediction",traceback.print_exc())
###########################################################################################################################
def min_max_norm(min_a,max_a,a):
    try:
        if min_a==max_a:
            return a
        new_max=1;new_min=0
        new_a=((a-min_a)/(max_a-min_a))*(new_max-new_min)+new_min
        return new_a
    except:
        print("Problem in min_max_norm",traceback.print_exc())
###########################################################################################################################
def compute_cost(number_of_days,variable_names,token_names,composit_data,idx,filecoin_data,weight_vector):
    try:
        # print(number_of_days,variable_names,token_names,idx,weight_vector)
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0;predicted_cost=0
        selection_table="";points=[]
        for i in range(int(number_of_days)):
            # Loop for every variable 
            for j in range(1,len(variable_names)):
                A=[]
                # Run over each token 
                for k in range(0,len(token_names)):                                   
                    try: A.append(float(composit_data[k][j][idx+i]))
                    except: A.append(-1)
                T=A.copy()
                T=[item for item in A if item!=-1]

                max_a=max(A);min_a=min(T);normalized_A=[]
                if j==1 or j==2 or j==3:
                    # Apply reverse normalization
                    for item in A:
                        if item==-1: normalized_A.append(-1)
                        else: normalized_A.append(1-min_max_norm(min_a,max_a,item))
                else:
                    # Apply normalization
                    for item in A:
                        if item==-1: normalized_A.append(-1)
                        else: normalized_A.append(min_max_norm(min_a,max_a,item))

                print("Normalized",variable_names[j],":",normalized_A)
                # Cost Function
                filecoin_score=filecoin_score+weight_vector[j]*normalized_A[0];genaro_score=genaro_score+weight_vector[j]*normalized_A[1]
                sia_score=sia_score+weight_vector[j]*normalized_A[2];storj_score=storj_score+weight_vector[j]*normalized_A[3]
                #print(filecoin_score,genaro_score,sia_score,storj_score)
            # Cost Vector
            Temp=[filecoin_score,genaro_score,sia_score,storj_score]
                    
            # Maximum Likelihood
            max_indx=Temp.index(max(Temp))
            points.append(max_indx)
            print(filecoin_data[0][idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
            selection_table=selection_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
            print("-----------------------------------------------------------------------------------------")
        return(points,selection_table,predicted_cost)
    except:
        print("Problem in compute_cost",traceback.print_exc())
###########################################################################################################################   
###########################################################################################################################
def compute_cost_with_constraint(number_of_days,variable_names,token_names,composit_data,idx,filecoin_data,weight_vector,constraint_vector):
    try:
        # print(number_of_days,variable_names,token_names,idx,weight_vector)
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0;predicted_cost=0
        selection_table="";points=[]
        for i in range(int(number_of_days)):
            # Loop for every variable 
            for j in range(1,len(variable_names)):
                A=[]
                # Run over each token 
                for k in range(0,len(token_names)):                                   
                    try: A.append(float(composit_data[k][j][idx+i]))
                    except: A.append(-1)
                T=A.copy()
                T=[item for item in A if item!=-1]
                max_a=max(A);min_a=min(T);normalized_A=[]
                for item in A:
                    if item==-1: normalized_A.append(-1)
                    else:
                        if j==1:  normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                        elif j==2:
                            if constraint_vector[j]!=-1:
                                if item<=constraint_vector[j]:  normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                                else: normalized_A.append(-1000)
                            else:   normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                        elif j==3:
                            if constraint_vector[j]!=-1:
                                if item<=constraint_vector[j]:  normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                                else: normalized_A.append(-1000)    
                            else:   normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization                    
                        elif j>3:
                            if constraint_vector[j]!=-1:
                                if item>=constraint_vector[j]:  normalized_A.append(min_max_norm(min_a,max_a,item))  # Apply normalization
                                else: normalized_A.append(-1000)   
                            else:   normalized_A.append(min_max_norm(min_a,max_a,item))  # Apply reverse normalization                      

                print("Normalized",variable_names[j],":",normalized_A)
                # Cost Function
                filecoin_score=filecoin_score+weight_vector[j]*normalized_A[0];genaro_score=genaro_score+weight_vector[j]*normalized_A[1]
                sia_score=sia_score+weight_vector[j]*normalized_A[2];storj_score=storj_score+weight_vector[j]*normalized_A[3]
                #print(filecoin_score,genaro_score,sia_score,storj_score)
            # Cost Vector
            Temp=[filecoin_score,genaro_score,sia_score,storj_score]
            # print(Temp)        
            # Maximum Likelihood
            max_indx=Temp.index(max(Temp))
            points.append(max_indx)
            print(filecoin_data[0][idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
            selection_table=selection_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
            print("-----------------------------------------------------------------------------------------")
        return(points,selection_table,predicted_cost)
    except:
        print("Problem in compute_cost_with_constraint",traceback.print_exc())
###########################################################################################################################
def compute_cost_with_constraint_compute(number_of_days,variable_names,token_names,composit_data,idx,filecoin_data,weight_vector,constraint_vector):
    try:
        # print(number_of_days,variable_names,token_names,idx,weight_vector)
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0;predicted_cost=0
        selection_table="";points=[]
        for i in range(int(number_of_days)):
            # Loop for every variable 
            for j in range(1,len(variable_names)):
                A=[]
                # Run over each token 
                for k in range(0,len(token_names)):                                   
                    try: A.append(float(composit_data[k][j][idx+i]))
                    except: A.append(-1)
                T=A.copy()
                T=[item for item in A if item!=-1]
                max_a=max(A);min_a=min(T);normalized_A=[]
                for item in A:
                    if item==-1: normalized_A.append(-1)
                    else:
                        if j==1:  normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                        elif j==2:
                            if constraint_vector[j]!=-1:
                                if item<=constraint_vector[j]:  normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                                else: normalized_A.append(-1000)
                            else:   normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                        # elif j==3:
                        #     if constraint_vector[j]!=-1:
                        #         if item<=constraint_vector[j]:  normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                        #         else: normalized_A.append(-1000)    
                        #     else:   normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization                    
                        elif j>=3:
                            if constraint_vector[j]!=-1:
                                if item>=constraint_vector[j]:  normalized_A.append(min_max_norm(min_a,max_a,item))  # Apply normalization
                                else: normalized_A.append(-1000)   
                            else:   normalized_A.append(min_max_norm(min_a,max_a,item))  # Apply reverse normalization                      

                print("Normalized",variable_names[j],":",normalized_A)
                # Cost Function
                filecoin_score=filecoin_score+weight_vector[j]*normalized_A[0];genaro_score=genaro_score+weight_vector[j]*normalized_A[1]
                sia_score=sia_score+weight_vector[j]*normalized_A[2];storj_score=storj_score+weight_vector[j]*normalized_A[3]
                #print(filecoin_score,genaro_score,sia_score,storj_score)
            # Cost Vector
            Temp=[filecoin_score,genaro_score,sia_score,storj_score]
            # print(Temp)        
            # Maximum Likelihood
            max_indx=Temp.index(max(Temp))
            points.append(max_indx)
            print(filecoin_data[0][idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
            selection_table=selection_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
            print("-----------------------------------------------------------------------------------------")
        return(points,selection_table,predicted_cost)
    except:
        print("Problem in compute_cost_with_constraint",traceback.print_exc())
###########################################################################################################################
def compute_cost_with_constraint_with_prediction(number_of_days,variable_names,token_names,composit_data,idx,filecoin_data,weight_vector,constraint_vector,flag):
    try:
        # print(number_of_days,variable_names,token_names,idx,weight_vector)
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0;predicted_cost=0
        selection_table="";points=[]
        for i in range(int(number_of_days)):
            # Loop for every variable 
            #for j in range(1,len(variable_names)):
            for j in range(0,len(variable_names)):
                A=[]
                # Run over each token 
                for k in range(0,len(token_names)):                                   
                    try:
                        if flag==False:
                            A.append(float(composit_data[k][j][idx+i]))
                        else:
                            # For prediction
                            A.append(float(composit_data[k][j][i]))
                    except: A.append(-1)
                # print("Before Normalization...",A)
                T=A.copy()
                T=[item for item in A if item!=-1]
                if T!=[]:
                    max_a=max(A);min_a=min(T);normalized_A=[]
                    # print(max_a,min_a)
                    for item in A:
                        # print(j,item)
                        if item==-1:
                            normalized_A.append(-1)
                        else:
                            if j==0: # Price
                                # print(min_max_norm(min_a,max_a,item))
                                normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                            elif j==1: # Fee
                                if constraint_vector[j]!=-1:
                                    if item<=constraint_vector[j]:
                                        normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                                    else: 
                                        normalized_A.append(-1000)
                                else:   
                                    # print(min_max_norm(min_a,max_a,item))
                                    normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                            elif j==2: # Blocktime
                                if constraint_vector[j]!=-1:
                                    if item<=constraint_vector[j]:
                                        normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization
                                    else:
                                        normalized_A.append(-1000)    
                                else:   
                                    # print(min_max_norm(min_a,max_a,item))
                                    normalized_A.append(1-min_max_norm(min_a,max_a,item))  # Apply reverse normalization                    
                            elif j>2:
                                if constraint_vector[j]!=-1:
                                    if item>=constraint_vector[j]:
                                        normalized_A.append(min_max_norm(min_a,max_a,item))  # Apply normalization
                                    else:
                                        normalized_A.append(-1000)   
                                else:   
                                    # print(min_max_norm(min_a,max_a,item))
                                    normalized_A.append(min_max_norm(min_a,max_a,item))  # Apply reverse normalization                      

                else:
                    T=[-1,-1,-1,-1]
                print("Normalized",variable_names[j],":",normalized_A)
                # Cost Function
                filecoin_score=filecoin_score+weight_vector[j]*normalized_A[0];genaro_score=genaro_score+weight_vector[j]*normalized_A[1]
                sia_score=sia_score+weight_vector[j]*normalized_A[2];storj_score=storj_score+weight_vector[j]*normalized_A[3]
                #print(filecoin_score,genaro_score,sia_score,storj_score)
            # Cost Vector
            Temp=[filecoin_score,genaro_score,sia_score,storj_score]
            # print(Temp)        
            # Maximum Likelihood
            max_indx=Temp.index(max(Temp))
            points.append(max_indx)
            print(filecoin_data[0][idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
            selection_table=selection_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
            print("-----------------------------------------------------------------------------------------")
        return(points,selection_table,predicted_cost)
    except:
        print("Problem in compute_cost_with_constraint",traceback.print_exc())
###########################################################################################################################
@app.route("/")
def hello():
    return render_template('index.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route("/compute_engine")
def compute_engine():
    return render_template('compute_models.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route("/storage_engine")
def storage_engine():
    return render_template('storage_models.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route("/FirstModel")
def FirstModel():
    return render_template('model-1.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route("/FirstModelData")
def FirstModelData():
    global filecoin_data,genaro_data,sia_data,storj_data
    global given_date,number_of_days,selection_table,estimation_table;cost_estimation
    print("Given Date:",given_date)
    # Display Filecoin data
    filecoin="";genaro="";sia="";storj=""
    try:
        idx=filecoin_data[0].index(given_date)
    except:
        idx=-1
    print("Number of days:",number_of_days,"\t Index",idx)
    if number_of_days!=-1 and idx!=-1:
        for i in range(int(number_of_days)):
            filecoin=filecoin+"<tr>";genaro=genaro+"<tr>";sia=sia+"<tr>";storj=storj+"<tr>"
            # Make a loop for the columns
            for j in range(0,10):
                filecoin=filecoin+"<td>"+filecoin_data[j][idx+i]+"</td>";genaro=genaro+"<td>"+genaro_data[j][idx+i]+"</td>"
                sia=sia+"<td>"+sia_data[j][idx+i]+"</td>";storj=storj+"<td>"+storj_data[j][idx+i]+"</td>"
                # print(filecoin_data[j][idx+i],genaro_data[j][idx+i],sia_data[j][idx+i],storj_data[j][idx+i])
                # print("-----------------------------------------------------------------------------------------------")

            filecoin=filecoin+"</tr>";genaro=genaro+"</tr>";sia=sia+"</tr>";storj=storj+"</tr>"

    return render_template('data-3.html',cost_estimation=cost_estimation,estimation=estimation_table,table=selection_table,filecoin=filecoin,genaro=genaro,sia=sia,storj=storj, init=True,reload=True)
###########################################################################################################################
@app.route("/ThirdModelData")
def ThirdModelData():
    global filecoin_data,genaro_data,sia_data,storj_data
    global given_date,number_of_days,selection_table,estimation_table
    print("Given Date:",given_date)
    # Display Filecoin data
    filecoin="";genaro="";sia="";storj=""
    try:
        idx=filecoin_data[0].index(given_date)
    except:
        idx=-1
    print("Number of days:",number_of_days,"\t Index",idx)
    if number_of_days!=-1 and idx!=-1:
        for i in range(int(number_of_days)):
            filecoin=filecoin+"<tr>";genaro=genaro+"<tr>";sia=sia+"<tr>";storj=storj+"<tr>"
            # Make a loop for the columns
            for j in range(0,10):
                filecoin=filecoin+"<td>"+filecoin_data[j][idx+i]+"</td>";genaro=genaro+"<td>"+genaro_data[j][idx+i]+"</td>"
                sia=sia+"<td>"+sia_data[j][idx+i]+"</td>";storj=storj+"<td>"+storj_data[j][idx+i]+"</td>"
                # print(filecoin_data[j][idx+i],genaro_data[j][idx+i],sia_data[j][idx+i],storj_data[j][idx+i])
                # print("-----------------------------------------------------------------------------------------------")

            filecoin=filecoin+"</tr>";genaro=genaro+"</tr>";sia=sia+"</tr>";storj=storj+"</tr>"

    return render_template('data-1.html',estimation=estimation_table,table=selection_table,filecoin=filecoin,genaro=genaro,sia=sia,storj=storj, init=True,reload=True)
###########################################################################################################################
###########################################################################################################################
@app.route("/FourthModelData")
def FourthModelData():
    global filecoin_data,genaro_data,sia_data,storj_data;composit_data
    global given_date,number_of_days,selection_table,estimation_table;cost_estimation
    print("Given Date:",given_date)
    # Display Filecoin data
    filecoin="";genaro="";sia="";storj=""
    try:
        idx=filecoin_data[0].index(given_date)
    except:
        idx=-1
    print("Number of days:",number_of_days,"\t Index",idx)
    print(composit_data[0])
    if number_of_days!=-1:
        for i in range(int(number_of_days)):
            filecoin=filecoin+"<tr>";genaro=genaro+"<tr>";sia=sia+"<tr>";storj=storj+"<tr>"
            # Make a loop for the columns
            for j in range(0,10):
                if j==0:
                    # For date
                    filecoin=filecoin+"<td>"+str(filecoin_data[j][idx+i])+"</td>";genaro=genaro+"<td>"+str(filecoin_data[j][idx+i])+"</td>"
                    sia=sia+"<td>"+str(filecoin_data[j][idx+i])+"</td>";storj=storj+"<td>"+str(filecoin_data[j][idx+i])+"</td>"
                    continue
                else:
                    try:
                        filecoin=filecoin+"<td>"+str(composit_data[0][j-1][i])+"</td>";genaro=genaro+"<td>"+str(composit_data[1][j-1][i])+"</td>"
                        sia=sia+"<td>"+str(composit_data[2][j-1][i])+"</td>";storj=storj+"<td>"+str(composit_data[3][j-1][i])+"</td>"
                    except:
                        print(i,j,traceback.print_exc())
                # print(filecoin_data[j][idx+i],genaro_data[j][idx+i],sia_data[j][idx+i],storj_data[j][idx+i])
                # print("-----------------------------------------------------------------------------------------------")

            filecoin=filecoin+"</tr>";genaro=genaro+"</tr>";sia=sia+"</tr>";storj=storj+"</tr>"

    return render_template('data-3.html',cost_estimation=cost_estimation,estimation=estimation_table,table=selection_table,filecoin=filecoin,genaro=genaro,sia=sia,storj=storj, init=True,reload=True)
###########################################################################################################################
@app.route('/FirstModelResult', methods=['POST'])
def FirstModelResult():
    global filecoin_data,genaro_data,sia_data,storj_data
    global given_date,number_of_days,selection_table
    global filecoin_price,filecoin_fees,filecoin_blocktime,filecoin_fcas,filecoin_transection_volume,filecoin_exchange_volume,filecoin_bandwidth,filecoin_storage
    global genaro_price,genaro_fees,genaro_blocktime,genaro_fcas,genaro_transection_volume,genaro_exchange_volume,genaro_bandwidth,genaro_storage
    global sia_price,sia_fees,sia_blocktime,sia_fcas,sia_transection_volume,sia_exchange_volume,sia_bandwidth,sia_storage
    global storj_price,storj_fees,storj_blocktime,storj_fcas,storj_transection_volume,storj_exchange_volume,storj_bandwidth,storj_storage
    cost=-1;speed=-1;security=-1;health=-1;bandwidth=-1;storage=-1;
    choice_10="";choice_20="";choice_30=""
    token_images=["static/images/flipcoin.jpg","static/images/genaro.png","static/images/Siacoin.png","static/images/storj.png","static/images/invalid.png"]
    token_names=["Flipcoin","Genaro","Siacoin","Storj"]
    variable_names=["Date","Price","Fees","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Bandwidth_UP","Bandwidth_Down","Storage"]
    warning=""
    try:
        #########################################################################################################
        given_date=request.form.get("bday")
        print("Date:",given_date)
        number_of_days=request.form.get("days")
        print("Days Selected:",number_of_days)
        print("Weightage...")
        cost=int(request.form.get("cost"))
        print("Cost:",cost)
        speed=int(request.form.get("speed"))
        print("Speed:",speed)
        security=int(request.form.get("security"))
        print("Security:",security)
        health=int(request.form.get("health"))
        print("Health:",health)
        bandwidth=int(request.form.get("bandwidth"))
        print("Bandwidth:",bandwidth)
        storage=int(request.form.get("storage"))
        print("Storage:",storage)
        weight_vector=[-1,cost,cost,speed,security,health,health,bandwidth,bandwidth,storage]
        #########################################################################################################
        if number_of_days=="10":
            choice_10="checked"
        elif number_of_days=="10":
            choice_20="checked"
        elif number_of_days=="30":
            choice_30="checked"
        #########################################################################################################
        # Finding the date index
        try:
            idx=filecoin_data[0].index(given_date)
            print("Number of days:",int(number_of_days))
        except:
            idx=-1;number_of_days=-1
                 
        # Optimization Module
        points=[];selection_table=""
        composit_data=[filecoin_data,genaro_data,sia_data,storj_data]
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0
        if number_of_days!=-1 and idx!=-1:
            for i in range(int(number_of_days)):
                # Loop for every variable 
                for j in range(1,len(variable_names)):
                    A=[]
                    # Run over each token 
                    for k in range(0,len(token_names)):                                   
                        try:
                            T=composit_data[k][j]
                            A.append(float(T[idx+i]))
                        except:
                            A.append(-1)
                    T=A.copy()
                    T=[item for item in A if item!=-1]
                    # print(T)
                    max_a=max(A);min_a=min(T)
                    normalized_A=[]
                    if j==0 or j==1:
                        # Apply reverse normalization
                        for item in A:
                            if item==-1:
                                normalized_A.append(-1)
                            else:
                                normalized_A.append(1-min_max_norm(min_a,max_a,item))
                    else:
                        # Apply normalization
                        for item in A:
                            if item==-1:
                                normalized_A.append(-1)
                            else:
                                normalized_A.append(min_max_norm(min_a,max_a,item))

                    print("Normalized",variable_names[j],":",normalized_A)
                    # Cost Function
                    filecoin_score=filecoin_score+weight_vector[j]*normalized_A[0];genaro_score=genaro_score+weight_vector[j]*normalized_A[1]
                    sia_score=sia_score+weight_vector[j]*normalized_A[2];storj_score=storj_score+weight_vector[j]*normalized_A[3]
                # Cost Vector
                Temp=[filecoin_score,genaro_score,sia_score,storj_score]
                # Maximum Likelihood
                max_indx=Temp.index(max(Temp))
                points.append(max_indx)
                print(filecoin_data[0][idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
                selection_table=selection_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
                print("-----------------------------------------------------------------------------------------")
                # ############################### Price #############################
            #print(points)
            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sored_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            token_1=token_images[sored_indx[3][0]];token_2=token_images[sored_indx[2][0]];token_3=token_images[sored_indx[1][0]];token_4=token_images[sored_indx[0][0]]
        else:
            token_1=token_images[0];token_2=token_images[1];token_3=token_images[2];token_4=token_images[3]
            warning="Data Not available for the selected time period !"
        #########################################################################################################
        return render_template('result-1.html',warning=warning,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
    except:
        print("Error in Information Extraction|",traceback.print_exc())
        return render_template('result-1.html',token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
###########################################################################################################################
###########################################################################################################################
@app.route("/SecondModel")
def SecondModel():
    return render_template('model-2.html')
    #return "Flask Server is On..."
###########################################################################################################################
###########################################################################################################################
@app.route('/SecondModelResult', methods=['POST'])
def SecondModelResult():
    global filecoin_data,genaro_data,sia_data,storj_data
    global given_date,number_of_days,selection_table,estimation_table
    global filecoin_price,filecoin_fees,filecoin_blocktime,filecoin_fcas,filecoin_transection_volume,filecoin_exchange_volume,filecoin_bandwidth,filecoin_storage
    global genaro_price,genaro_fees,genaro_blocktime,genaro_fcas,genaro_transection_volume,genaro_exchange_volume,genaro_bandwidth,genaro_storage
    global sia_price,sia_fees,sia_blocktime,sia_fcas,sia_transection_volume,sia_exchange_volume,sia_bandwidth,sia_storage
    global storj_price,storj_fees,storj_blocktime,storj_fcas,storj_transection_volume,storj_exchange_volume,storj_bandwidth,storj_storage
    cost=-1;speed=-1;security=-1;health=-1;bandwidth=-1;storage=-1
    choice_10="";choice_20="";choice_30=""
    token_images=["static/images/flipcoin.jpg","static/images/genaro.png","static/images/Siacoin.png","static/images/storj.png"]
    token_names=["Flipcoin","Genaro","Siacoin","Storj"]
    variable_names=["Date","Price","Fees","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Bandwidth_UP","Bandwidth_Down","Storage"]
    warning=""
    try:
        print("#########################################################################################################")
        given_date=request.form.get("bday")
        number_of_days=request.form.get("days")
        print("Date:",given_date,"\t Days Selected:",number_of_days)
        ##########################################Preferences####################################################
        print("Weightage...")
        cost=int(request.form.get("cost"))
        speed=int(request.form.get("speed"))
        security=int(request.form.get("security"))
        health=int(request.form.get("health"))
        bandwidth=int(request.form.get("bandwidth"))
        storage=int(request.form.get("storage"))
        print("Cost:",cost,"Speed:",speed,"Security:",security,"Health:",health,"Bandwidth:",bandwidth,"Storage:",storage)
        ##########################################Parameter######################################################
        try: given_storage=int(request.form.get("given_storage")) 
        except: given_storage=-1
        try: given_budget=int(request.form.get("given_budget")) 
        except: given_budget=-1
        print("Given Storage:",given_storage,"\t Budget:",given_budget)
        weight_vector=[-1,cost,cost,speed,security,health,health,bandwidth,bandwidth,storage]
        print(weight_vector)
        #########################################################################################################
        if number_of_days=="10":
            choice_10="checked"
        elif number_of_days=="10":
            choice_20="checked"
        elif number_of_days=="30":
            choice_30="checked"
        #########################################################################################################
        # Finding the date index
        try: idx=filecoin_data[0].index(given_date);number_of_days=int(number_of_days)
        except: idx=-1;number_of_days=-1

        print("Number of days:",number_of_days)       
        # Optimization Module
        points=[];selection_table="";estimation_table="";balance=given_budget;servive_days=0
        composit_data=[filecoin_data,genaro_data,sia_data,storj_data];predicted_cost=0

        if number_of_days!=-1 and idx!=-1:
            points,selection_table,predicted_cost=compute_cost(number_of_days,variable_names,token_names,composit_data,idx,filecoin_data,weight_vector)
            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sored_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            selected_data=composit_data[sored_indx[3][0]]
            for i in range(int(number_of_days)):
                # ############################### computing cost per day #############################
                if given_storage!=-1 and given_budget!=-1:
                    price_cost=0
                    try: price_cost=price_cost+float(selected_data[1][idx+i])
                    except: pass
                    try: price_cost=price_cost+float(selected_data[2][idx+i])
                    except: pass
                    balance=balance-price_cost*given_storage
                    # print("Balance:",balance)
                    if balance>0:
                        servive_days=servive_days+1
                        estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(price_cost*given_storage)+"</td><td>"+str(balance)+"</td></tr>"
                # ############################### computing cost per day (Given only storage) #############################
                if given_storage!=-1 and given_budget==-1:
                    price_cost=0
                    try: price_cost=price_cost+float(selected_data[1][idx+i])
                    except: pass
                    try: price_cost=price_cost+float(selected_data[2][idx+i])
                    except: pass
                    predicted_cost=predicted_cost+price_cost*given_storage
                    # print("Cost:",price_cost*given_storage)
                    estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(price_cost*given_storage)+"</td><td>-</td></tr>"
                    servive_days=servive_days+1
            print("Number of Days:",servive_days," Cost:",predicted_cost)
            token_1=token_images[sored_indx[3][0]];token_2=token_images[sored_indx[2][0]];token_3=token_images[sored_indx[1][0]];token_4=token_images[sored_indx[0][0]]
        else:
            token_1=token_images[0];token_2=token_images[1];token_3=token_images[2];token_4=token_images[3]
            warning="Data Not available for the selected time period !"
        #########################################################################################################
        return render_template('result-2.html',predicted_cost=str(predicted_cost)[0:8],servive_days=servive_days,warning=warning,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
    except:
        print("Error in Information Extraction|",traceback.print_exc())
        return render_template('result-2.html',predicted_cost=str(predicted_cost)[0:8],servive_days=servive_days,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
###########################################################################################################################
###########################################################################################################################
@app.route("/ThirdModel")
def ThirdModel():
    return render_template('model-3.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route('/ThirdModelResult', methods=['POST'])
def ThirdModelResult():
    global filecoin_data,genaro_data,sia_data,storj_data
    global given_date,number_of_days,selection_table,estimation_table,cost_estimation
    global filecoin_price,filecoin_fees,filecoin_blocktime,filecoin_fcas,filecoin_transection_volume,filecoin_exchange_volume,filecoin_bandwidth,filecoin_storage
    global genaro_price,genaro_fees,genaro_blocktime,genaro_fcas,genaro_transection_volume,genaro_exchange_volume,genaro_bandwidth,genaro_storage
    global sia_price,sia_fees,sia_blocktime,sia_fcas,sia_transection_volume,sia_exchange_volume,sia_bandwidth,sia_storage
    global storj_price,storj_fees,storj_blocktime,storj_fcas,storj_transection_volume,storj_exchange_volume,storj_bandwidth,storj_storage
    cost=-1;speed=-1;security=-1;health=-1;bandwidth=-1;storage=-1
    choice_10="";choice_20="";choice_30=""
    token_images=["static/images/flipcoin.jpg","static/images/genaro.png","static/images/Siacoin.png","static/images/storj.png","static/images/invalid.png"]
    token_names=["Flipcoin","Genaro","Siacoin","Storj"]
    variable_names=["Date","Price","Fees","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Bandwidth_UP","Bandwidth_Down","Storage"]
    warning="";cost_estimation=""
    try:
        print("#########################################################################################################")
        given_date=request.form.get("bday")
        number_of_days=request.form.get("days")
        print("Date:",given_date,"\t Days Selected:",number_of_days)
        ##########################################Preferences####################################################
        print("Weightage...")
        cost=int(request.form.get("cost"))
        speed=int(request.form.get("speed"))
        security=int(request.form.get("security"))
        health=int(request.form.get("health"))
        bandwidth=int(request.form.get("bandwidth"))
        storage=int(request.form.get("storage"))
        print("Cost:",cost,"Speed:",speed,"Security:",security,"Health:",health,"Bandwidth:",bandwidth,"Storage:",storage)
        ##########################################Parameter######################################################
        try: given_storage=int(request.form.get("given_storage")) 
        except: given_storage=-1
        try: given_budget=int(request.form.get("given_budget")) 
        except: given_budget=-1
        print("Given Storage:",given_storage,"\t Budget:",given_budget)
        ##########################################Constraints####################################################
        try: cost_constraint=int(request.form.get("cost_constraint"))
        except: cost_constraint=-1
        try: speed_constraint=int(request.form.get("speed_constraint"))
        except: speed_constraint=-1
        try: security_constraint=int(request.form.get("security_constraint"))
        except: security_constraint=-1
        try: health_constraint=int(request.form.get("health_constraint"))
        except: health_constraint=-1
        try: bandwidth_constraint=int(request.form.get("bandwidth_constraint"))
        except: bandwidth_constraint=-1
        try: storage_constraint=int(request.form.get("storage_constraint"))
        except: storage_constraint=-1       
        # print("cost_constraint:",cost_constraint,"speed_constraint:",speed_constraint,"security_constraint:",security_constraint,
        # "health_constraint:",health_constraint,"bandwidth_constraint:",bandwidth_constraint,"storage_constraint:",storage_constraint)

        constraint_vector=[-1,cost_constraint,cost_constraint,speed_constraint,security_constraint,health_constraint,
                                        health_constraint,bandwidth_constraint,bandwidth_constraint,storage_constraint]
        weight_vector=[-1,cost,cost,speed,security,health,health,bandwidth,bandwidth,storage]
        print("Weight Vector: ",weight_vector)
        print("Constraint Vector: ",constraint_vector)
        print("#########################################################################################################")
        if number_of_days=="10":
            choice_10="checked"
        elif number_of_days=="10":
            choice_20="checked"
        elif number_of_days=="30":
            choice_30="checked"
        #########################################################################################################
        # Finding the date index
        try: idx=filecoin_data[0].index(given_date); print("Number of days:",int(number_of_days))
        except: idx=-1;number_of_days=-1
                 
        # Optimization Module
        points=[];selection_table="";estimation_table="";balance=given_budget;servive_days=0
        composit_data=[filecoin_data,genaro_data,sia_data,storj_data]
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0;predicted_cost=0
        total_second_cost=0;total_third_cost=0;total_fourth_cost=0
        if number_of_days!=-1 and idx!=-1:
            points,selection_table,predicted_cost=compute_cost_with_constraint(number_of_days,variable_names,token_names,composit_data,
                                                                                    idx,filecoin_data,weight_vector,constraint_vector)
            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sorted_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            sorted_names=[token_names[sorted_indx[3][0]],token_names[sorted_indx[2][0]],token_names[sorted_indx[1][0]],token_names[sorted_indx[0][0]]]
            selected_data=composit_data[sorted_indx[3][0]]
            for i in range(int(number_of_days)):
                # ############################### computing cost under constraint (Given only storage) #############################
                if given_storage!=-1 and given_budget==-1:
                    first_cost=0;second_cost=0;third_cost=0;fourth_cost=0
                    try: first_cost=first_cost+float(selected_data[1][idx+i])
                    except: pass
                    try: first_cost=first_cost+float(selected_data[2][idx+i])
                    except: pass
                    # Cost for Filecoin
                    try: second_cost=second_cost+float(composit_data[sorted_indx[2][0]][1][idx+i])
                    except: pass
                    try: second_cost=second_cost+float(composit_data[sorted_indx[2][0]][2][idx+i])
                    except: pass
                    # Cost for Genaro
                    try: third_cost=third_cost+float(composit_data[sorted_indx[1][0]][1][idx+i])
                    except: pass
                    try: third_cost=third_cost+float(composit_data[sorted_indx[1][0]][2][idx+i])
                    except: pass
                    # Cost for Sia
                    try: fourth_cost=fourth_cost+float(composit_data[sorted_indx[0][0]][1][idx+i])
                    except: pass
                    try: fourth_cost=fourth_cost+float(composit_data[sorted_indx[0][0]][2][idx+i])
                    except: pass

                    predicted_cost=predicted_cost+first_cost*given_storage
                    total_second_cost=total_second_cost+second_cost*given_storage;total_third_cost=total_third_cost+third_cost*given_storage
                    total_fourth_cost=total_fourth_cost+fourth_cost*given_storage
                    # print("Cost:",price_cost*given_storage)
                    estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(first_cost*given_storage)+"</td><td>-</td></tr>"
                    servive_days=servive_days+1
                # ############################### computing cost per day #############################
                if given_storage!=-1 and given_budget!=-1:
                    price_cost=0
                    try: price_cost=price_cost+float(selected_data[1][idx+i])
                    except: pass
                    try: price_cost=price_cost+float(selected_data[2][idx+i])
                    except: pass
                    balance=balance-price_cost*given_storage
                    # print("Balance:",balance)
                    if balance>0:
                        servive_days=servive_days+1
                        estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(price_cost*given_storage)+"</td><td>"+str(balance)+"</td></tr>"
                # # ############################### computing cost per day (Given only storage) #############################
                # if given_storage!=-1 and given_budget==-1 and cost_constraint==-1:
                #     minimum_cost=0
                #     try: minimum_cost=minimum_cost+float(selected_data[1][idx+i])
                #     except: pass
                #     try: minimum_cost=minimum_cost+float(selected_data[2][idx+i])
                #     except: pass
                #     predicted_cost=predicted_cost+minimum_cost*given_storage
                #     # print("Cost:",price_cost*given_storage)
                #     estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(minimum_cost*given_storage)+"</td><td>-</td></tr>"
                #     servive_days=servive_days+1
                ##############################################################################################################

            if cost_constraint!=-1:
                print("Eveluating constraint...")
                Temp=[predicted_cost,total_second_cost,total_third_cost,total_fourth_cost]
                # print(Temp)
                counter=0
                for index,item in enumerate(Temp):
                    if item<=cost_constraint:
                        predicted_cost=item
                        print(index,"Number of Days:",servive_days," Cost:",predicted_cost)
                        break
                    else:
                        counter=counter+1
                # print(index)
                if index==0:
                    token_1=token_images[sorted_indx[3][0]];token_2=token_images[sorted_indx[2][0]];token_3=token_images[sorted_indx[1][0]];token_4=token_images[sorted_indx[0][0]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>"
                if index==1:
                    token_1=token_images[sorted_indx[2][0]];token_2=token_images[sorted_indx[3][0]];token_3=token_images[sorted_indx[1][0]];token_4=token_images[sorted_indx[0][0]]
                    # sorted_names=[token_names[sorted_indx[2][0]],token_names[sorted_indx[1][0]],token_names[sorted_indx[0][0]],token_names[sorted_indx[3][0]]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>"
                if index==2:
                    token_1=token_images[sorted_indx[1][0]];token_2=token_images[sorted_indx[3][0]];token_3=token_images[sorted_indx[2][0]];token_4=token_images[sorted_indx[0][0]]
                    # sorted_names=[token_names[sorted_indx[1][0]],token_names[sorted_indx[0][0]],token_names[sorted_indx[3][0]],token_names[sorted_indx[2][0]]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>"
                if index==3:
                    token_1=token_images[sorted_indx[0][0]];token_2=token_images[sorted_indx[3][0]];token_3=token_images[sorted_indx[2][0]];token_4=token_images[sorted_indx[1][0]]
                    # sorted_names=[token_names[sorted_indx[0][0]],token_names[sorted_indx[1][0]],token_names[sorted_indx[2][0]],token_names[sorted_indx[3][0]]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>"


                if counter==4:
                    print("No token satisfies the constraint...")
                    token_1=token_images[4];token_2=token_images[4];token_3=token_images[4];token_4=token_images[4]
            else:
                print("Number of Days:",servive_days," Cost:",predicted_cost)
                Temp=[predicted_cost,total_second_cost,total_third_cost,total_fourth_cost]
                # print(Temp)
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(predicted_cost)+"</td></tr>"
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(total_second_cost)+"</td></tr>"
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(total_third_cost)+"</td></tr>"
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(total_fourth_cost)+"</td></tr>"
                token_1=token_images[sorted_indx[3][0]];token_2=token_images[sorted_indx[2][0]];token_3=token_images[sorted_indx[1][0]];token_4=token_images[sorted_indx[0][0]]

        else:
            token_1=token_images[0];token_2=token_images[1];token_3=token_images[2];token_4=token_images[3]
            warning="Data Not available for the selected time period !"
        #########################################################################################################
        return render_template('result-2.html',predicted_cost=str(predicted_cost)[0:8],servive_days=servive_days,warning=warning,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
    except:
        print("Error in Information Extraction|",traceback.print_exc())
        return render_template('result-2.html',predicted_cost=str(predicted_cost)[0:8],servive_days=servive_days,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
###########################################################################################################################
@app.route("/FourthModel")
def FourthModel():
    return render_template('model-4.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route('/FourthModelResult', methods=['POST'])
def FourthModelResult():
    global filecoin_data,genaro_data,sia_data,storj_data,composit_data
    global given_date,number_of_days,selection_table,estimation_table,cost_estimation
    global filecoin_price,filecoin_fees,filecoin_blocktime,filecoin_fcas,filecoin_transection_volume,filecoin_exchange_volume,filecoin_bandwidth,filecoin_storage
    global genaro_price,genaro_fees,genaro_blocktime,genaro_fcas,genaro_transection_volume,genaro_exchange_volume,genaro_bandwidth,genaro_storage
    global sia_price,sia_fees,sia_blocktime,sia_fcas,sia_transection_volume,sia_exchange_volume,sia_bandwidth,sia_storage
    global storj_price,storj_fees,storj_blocktime,storj_fcas,storj_transection_volume,storj_exchange_volume,storj_bandwidth,storj_storage
    cost=-1;speed=-1;security=-1;health=-1;bandwidth=-1;storage=-1
    choice_10="";choice_20="";choice_30=""
    token_images=["static/images/flipcoin.jpg","static/images/genaro.png","static/images/Siacoin.png","static/images/storj.png","static/images/invalid.png"]
    token_names=["Flipcoin","Genaro","Siacoin","Storj"]
    variable_names=["Date","Price","Fees","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Bandwidth_UP","Bandwidth_Down","Storage"]
    warning="";cost_estimation="";flag=True
    try:
        print("#########################################################################################################")
        given_date=request.form.get("bday")
        number_of_days=request.form.get("days")
        print("Date:",given_date,"\t Days Selected:",number_of_days)
        ##########################################Preferences####################################################
        print("Weightage...")
        cost=int(request.form.get("cost"))
        speed=int(request.form.get("speed"))
        security=int(request.form.get("security"))
        health=int(request.form.get("health"))
        bandwidth=int(request.form.get("bandwidth"))
        storage=int(request.form.get("storage"))
        print("Cost:",cost,"Speed:",speed,"Security:",security,"Health:",health,"Bandwidth:",bandwidth,"Storage:",storage)
        ##########################################Parameter######################################################
        try: given_storage=int(request.form.get("given_storage")) 
        except: given_storage=-1
        try: given_budget=int(request.form.get("given_budget")) 
        except: given_budget=-1
        print("Given Storage:",given_storage,"\t Budget:",given_budget)
        ##########################################Constraints####################################################
        try: cost_constraint=int(request.form.get("cost_constraint"))
        except: cost_constraint=-1
        try: speed_constraint=int(request.form.get("speed_constraint"))
        except: speed_constraint=-1
        try: security_constraint=int(request.form.get("security_constraint"))
        except: security_constraint=-1
        try: health_constraint=int(request.form.get("health_constraint"))
        except: health_constraint=-1
        try: bandwidth_constraint=int(request.form.get("bandwidth_constraint"))
        except: bandwidth_constraint=-1
        try: storage_constraint=int(request.form.get("storage_constraint"))
        except: storage_constraint=-1       
        # print("cost_constraint:",cost_constraint,"speed_constraint:",speed_constraint,"security_constraint:",security_constraint,
        # "health_constraint:",health_constraint,"bandwidth_constraint:",bandwidth_constraint,"storage_constraint:",storage_constraint)

        constraint_vector=[-1,cost_constraint,cost_constraint,speed_constraint,security_constraint,health_constraint,
                                        health_constraint,bandwidth_constraint,bandwidth_constraint,storage_constraint]
        weight_vector=[-1,cost,cost,speed,security,health,health,bandwidth,bandwidth,storage]
        print("Weight Vector: ",weight_vector)
        print("Constraint Vector: ",constraint_vector)
        print("#########################################################################################################")
        if number_of_days=="10":
            choice_10="checked"
        elif number_of_days=="10":
            choice_20="checked"
        elif number_of_days=="30":
            choice_30="checked"
        #########################################################################################################
        # Finding the date index
        try: idx=filecoin_data[0].index(given_date); number_of_days=int(number_of_days);print("Number of days:",number_of_days)
        except: idx=-1;number_of_days=-1
                 
        # Optimization Module
        points=[];selection_table="";estimation_table="";balance=given_budget;servive_days=0
        composit_data=[filecoin_data,genaro_data,sia_data,storj_data]
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0;predicted_cost=0
        total_second_cost=0;total_third_cost=0;total_fourth_cost=0
        if number_of_days!=-1 and idx!=-1:
            # Considering prediction data
            composit_data=get_arima_prediction(composit_data,given_date,number_of_days,variable_names)
            # print(a_composit_data)
            # for a in a_composit_data:
            #     for b in a:
            #         print(b)
            #     print("-------------------------")
            points,selection_table,predicted_cost=compute_cost_with_constraint_with_prediction(number_of_days,variable_names,token_names,composit_data,
                                                                                    idx,filecoin_data,weight_vector,constraint_vector,flag)
            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sorted_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            sorted_names=[token_names[sorted_indx[3][0]],token_names[sorted_indx[2][0]],token_names[sorted_indx[1][0]],token_names[sorted_indx[0][0]]]
            selected_data=composit_data[sorted_indx[3][0]]
            # print(selected_data)
            # print(len(selected_data))
            predicted_cost=0
            for i in range(int(number_of_days)):
                # ############################### computing cost under constraint (Given only storage) #############################
                if given_storage!=-1 and given_budget==-1:
                    first_cost=0;second_cost=0;third_cost=0;fourth_cost=0
                    try: first_cost=first_cost+float(selected_data[0][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    try: first_cost=first_cost+float(selected_data[1][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    # Cost for Filecoin
                    try: second_cost=second_cost+float(composit_data[sorted_indx[2][0]][0][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    try: second_cost=second_cost+float(composit_data[sorted_indx[2][0]][1][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    # Cost for Genaro
                    try: third_cost=third_cost+float(composit_data[sorted_indx[1][0]][0][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    try: third_cost=third_cost+float(composit_data[sorted_indx[1][0]][1][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    # Cost for Sia
                    try: fourth_cost=fourth_cost+float(composit_data[sorted_indx[0][0]][0][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    try: fourth_cost=fourth_cost+float(composit_data[sorted_indx[0][0]][1][i])
                    except:
                        print(traceback.print_exc())
                        pass
                    print(first_cost)
                    predicted_cost=predicted_cost+first_cost*given_storage
                    total_second_cost=total_second_cost+second_cost*given_storage;total_third_cost=total_third_cost+third_cost*given_storage
                    total_fourth_cost=total_fourth_cost+fourth_cost*given_storage
                    # print("Cost:",price_cost*given_storage)
                    estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(first_cost*given_storage)+"</td><td>-</td></tr>"
                    servive_days=servive_days+1
                # ############################### computing cost per day #############################
                if given_storage!=-1 and given_budget!=-1:
                    price_cost=0
                    try: price_cost=price_cost+float(selected_data[1][i])
                    except: pass
                    try: price_cost=price_cost+float(selected_data[2][i])
                    except: pass
                    balance=balance-price_cost*given_storage
                    # print("Balance:",balance)
                    if balance>0:
                        servive_days=servive_days+1
                        estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(price_cost*given_storage)+"</td><td>"+str(balance)+"</td></tr>"
                # # ############################### computing cost per day (Given only storage) #############################
                # if given_storage!=-1 and given_budget==-1 and cost_constraint==-1:
                #     minimum_cost=0
                #     try: minimum_cost=minimum_cost+float(selected_data[1][idx+i])
                #     except: pass
                #     try: minimum_cost=minimum_cost+float(selected_data[2][idx+i])
                #     except: pass
                #     predicted_cost=predicted_cost+minimum_cost*given_storage
                #     # print("Cost:",price_cost*given_storage)
                #     estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(minimum_cost*given_storage)+"</td><td>-</td></tr>"
                #     servive_days=servive_days+1
                ##############################################################################################################

            print("Number of Days:",number_of_days," Cost:",predicted_cost)
            if cost_constraint!=-1:
                print("Eveluating constraint...")
                Temp=[predicted_cost,total_second_cost,total_third_cost,total_fourth_cost]
                # print(Temp)
                counter=0
                for index,item in enumerate(Temp):
                    if item<=cost_constraint:
                        predicted_cost=item
                        print(index,"Number of Days:",servive_days," Cost:",predicted_cost)
                        break
                    else:
                        counter=counter+1
                # print(index)
                if index==0:
                    token_1=token_images[sorted_indx[3][0]];token_2=token_images[sorted_indx[2][0]];token_3=token_images[sorted_indx[1][0]];token_4=token_images[sorted_indx[0][0]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>"
                if index==1:
                    token_1=token_images[sorted_indx[2][0]];token_2=token_images[sorted_indx[3][0]];token_3=token_images[sorted_indx[1][0]];token_4=token_images[sorted_indx[0][0]]
                    # sorted_names=[token_names[sorted_indx[2][0]],token_names[sorted_indx[1][0]],token_names[sorted_indx[0][0]],token_names[sorted_indx[3][0]]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>"
                if index==2:
                    token_1=token_images[sorted_indx[1][0]];token_2=token_images[sorted_indx[3][0]];token_3=token_images[sorted_indx[2][0]];token_4=token_images[sorted_indx[0][0]]
                    # sorted_names=[token_names[sorted_indx[1][0]],token_names[sorted_indx[0][0]],token_names[sorted_indx[3][0]],token_names[sorted_indx[2][0]]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>"
                if index==3:
                    token_1=token_images[sorted_indx[0][0]];token_2=token_images[sorted_indx[3][0]];token_3=token_images[sorted_indx[2][0]];token_4=token_images[sorted_indx[1][0]]
                    # sorted_names=[token_names[sorted_indx[0][0]],token_names[sorted_indx[1][0]],token_names[sorted_indx[2][0]],token_names[sorted_indx[3][0]]]
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(Temp[3])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(Temp[0])+"</td></tr>"
                    cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(Temp[1])+"</td></tr>";cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(Temp[2])+"</td></tr>"


                if counter==4:
                    print("No token satisfies the constraint...")
                    token_1=token_images[4];token_2=token_images[4];token_3=token_images[4];token_4=token_images[4]
            else:
                print("Number of Days:",servive_days," Cost:",predicted_cost)
                Temp=[predicted_cost,total_second_cost,total_third_cost,total_fourth_cost]
                # print(Temp)
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[0]+"</td><td>"+str(predicted_cost)+"</td></tr>"
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[1]+"</td><td>"+str(total_second_cost)+"</td></tr>"
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[2]+"</td><td>"+str(total_third_cost)+"</td></tr>"
                cost_estimation=cost_estimation+"<tr><td>"+sorted_names[3]+"</td><td>"+str(total_fourth_cost)+"</td></tr>"
                token_1=token_images[sorted_indx[3][0]];token_2=token_images[sorted_indx[2][0]];token_3=token_images[sorted_indx[1][0]];token_4=token_images[sorted_indx[0][0]]

        else:
            token_1=token_images[0];token_2=token_images[1];token_3=token_images[2];token_4=token_images[3]
            warning="Data Not available for the selected time period !"
        #########################################################################################################
        return render_template('result-4.html',predicted_cost=str(predicted_cost)[0:8],servive_days=servive_days,warning=warning,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
    except:
        print("Error in Information Extraction|",traceback.print_exc())
        return render_template('result-4.html',predicted_cost=str(predicted_cost)[0:8],servive_days=servive_days,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=health,bandwidth=bandwidth,storage=storage, init=True)
###########################################################################################################################
###########################################################################################################################
@app.route("/first_compute_model")
def first_compute_model():
    return render_template('first_compute_model.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route('/compute_first_model_result', methods=['POST'])
def compute_first_model_result():
    global snm_array,gnt_array,rlc_array,dcp_array
    global given_date,number_of_days,selection_table,estimation_table
    snm_date,snm_price,blocktime_snm,fcas_snm,snm_transection_value,snm_exchange_value,snm_deal,snm_instance,snm_gpu=snm_array
    gnt_date,gnt_price,blocktime_gnt,fcas_gnt,gnt_transection_value,gnt_exchange_value,gnt_deal,gnt_instance,gnt_gpu=gnt_array
    rlc_date,rlc_price,blocktime_rlc,fcas_rlc,rlc_transection_value,rlc_exchange_value,rlc_deal,rlc_instance,rlc_gpu=rlc_array
    dcp_date,dcp_price,blocktime_dcp,fcas_dcp,dcp_transection_value,dcp_exchange_value,dcp_deal,dcp_instance,dcp_gpu=dcp_array
    cost=-1;speed=-1;security=-1;deals=-1;instance_size=-1;gpu=-1
    choice_10="";choice_20="";choice_30=""
    token_images=["static/images/GNT.png","static/images/iExec.jpg","static/images/sonm.png","static/images/DCP.png","static/images/invalid.png"]
    token_names=["GNT","RLC","SNM","DCP"]
    variable_names=["Date","Price","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Deals","Instance_Size","GPU"]
    warning=""
    try:
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #########################################################################################################
        given_date=request.form.get("selected_date")
        print("Date:",given_date)
        number_of_days=request.form.get("days")
        print("Days Selected:",number_of_days)
        print("Weightage...")
        cost=int(request.form.get("cost"))
        print("Cost:",cost)
        speed=int(request.form.get("speed"))
        print("Speed:",speed)
        security=int(request.form.get("security"))
        print("Security:",security)
        health=int(request.form.get("health"))
        print("Health:",health)
        deals=int(request.form.get("deals"))
        print("Deals:",deals)
        instance_size=int(request.form.get("instances"))
        print("Instance Size:",instance_size)
        gpu=int(request.form.get("gpu"))
        print("GPU:",gpu)
        weight_vector=[-1,cost,speed,security,health,health,deals,instance_size,gpu]
        #########################################################################################################
        if number_of_days=="10":
            choice_10="checked"
        elif number_of_days=="10":
            choice_20="checked"
        elif number_of_days=="30":
            choice_30="checked"
        #########################################################################################################
        # Finding the date index
        try:
            idx=snm_date.index(given_date)
            print("Number of days:",int(number_of_days))
        except:
            idx=-1;number_of_days=-1
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #########################################################################################################         
        # Optimization Module
        points=[];selection_table="";composit_data=[gnt_array,rlc_array,snm_array,dcp_array]
        gnt_score=0;rlc_score=0;snm_score=0;dcp_score=0
        if number_of_days!=-1 and idx!=-1:
            for i in range(int(number_of_days)):
                # Loop for every variable 
                for j in range(1,len(variable_names)):
                    A=[]
                    # Run over each token 
                    for k in range(0,len(token_names)):                                   
                        try:
                            T=composit_data[k][j]
                            A.append(float(T[idx+i]))
                        except:
                            A.append(-1)
                    T=A.copy()
                    T=[item for item in A if item!=-1]
                    # print(T)
                    max_a=max(A);min_a=min(T)
                    # print(T,min_a,max_a)
                    normalized_A=[]
                    if j==0 or j==1:
                        # Apply reverse normalization
                        for item in A:
                            if item==-1:
                                normalized_A.append(-1)
                            else:
                                normalized_A.append(1-min_max_norm(min_a,max_a,item))
                    else:
                        # Apply normalization
                        for item in A:
                            if item==-1:
                                normalized_A.append(-1)
                            else:
                                normalized_A.append(min_max_norm(min_a,max_a,item))

                    print("Normalized",variable_names[j],":",normalized_A)
                    # Cost Function
                    gnt_score=gnt_score+weight_vector[j]*normalized_A[0];rlc_score=rlc_score+weight_vector[j]*normalized_A[1]
                    snm_score=snm_score+weight_vector[j]*normalized_A[2];dcp_score=dcp_score+weight_vector[j]*normalized_A[3]
                # Cost Vector
                Temp=[gnt_score,rlc_score,snm_score,dcp_score]
                # Maximum Likelihood
                max_indx=Temp.index(max(Temp))
                points.append(max_indx)
                print(gnt_date[idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
                selection_table=selection_table+"<tr><td>"+gnt_date[idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
                print("-----------------------------------------------------------------------------------------")
                # ############################### Price #############################
            #print(points)
            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sored_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            token_1=token_images[sored_indx[3][0]];token_2=token_images[sored_indx[2][0]];token_3=token_images[sored_indx[1][0]];token_4=token_images[sored_indx[0][0]]
        else:
            token_1=token_images[0];token_2=token_images[1];token_3=token_images[2];token_4=token_images[3]
            warning="Data Not available for the selected time period !"
        #########################################################################################################
        return render_template('first_compute_model_result.html',warning=warning,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=deals,bandwidth=instance_size,storage=gpu, init=True)
    except:
        print("Error in Information Extraction|",traceback.print_exc())
        return render_template('first_compute_model_result.html',token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=deals,bandwidth=instance_size,storage=gpu, init=True)
###########################################################################################################################
@app.route("/first_compute_model_extended")
def first_compute_model_extended():
    return render_template('first_compute_model_extended.html')
    #return "Flask Server is On..."
###########################################################################################################################
@app.route('/compute_first_model_extended_result', methods=['POST'])
def compute_first_model_extended_result():
    global snm_array,gnt_array,rlc_array,dcp_array
    global given_date,number_of_days,selection_table,estimation_table
    snm_date,snm_price,blocktime_snm,fcas_snm,snm_transection_value,snm_exchange_value,snm_deal,snm_instance,snm_gpu=snm_array
    gnt_date,gnt_price,blocktime_gnt,fcas_gnt,gnt_transection_value,gnt_exchange_value,gnt_deal,gnt_instance,gnt_gpu=gnt_array
    rlc_date,rlc_price,blocktime_rlc,fcas_rlc,rlc_transection_value,rlc_exchange_value,rlc_deal,rlc_instance,rlc_gpu=rlc_array
    dcp_date,dcp_price,blocktime_dcp,fcas_dcp,dcp_transection_value,dcp_exchange_value,dcp_deal,dcp_instance,dcp_gpu=dcp_array
    cost=-1;speed=-1;security=-1;deals=-1;instance_size=-1;gpu=-1
    choice_10="";choice_20="";choice_30=""
    token_images=["static/images/GNT.png","static/images/iExec.jpg","static/images/sonm.png","static/images/DCP.png","static/images/invalid.png"]
    token_names=["GNT","RLC","SNM","DCP"]
    variable_names=["Date","Price","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Deals","Instance_Size","GPU"]
    warning=""
    try:
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #########################################################################################################
        given_date=request.form.get("selected_date")
        print("Date:",given_date)
        number_of_days=request.form.get("days")
        print("Days Selected:",number_of_days)
        print("Weightage...")
        cost=int(request.form.get("cost"))
        print("Cost:",cost)
        speed=int(request.form.get("speed"))
        print("Speed:",speed)
        security=int(request.form.get("security"))
        print("Security:",security)
        health=int(request.form.get("health"))
        print("Health:",health)
        deals=int(request.form.get("deals"))
        print("Deals:",deals)
        instance_size=int(request.form.get("instances"))
        print("Instance Size:",instance_size)
        gpu=int(request.form.get("gpu"))
        print("GPU:",gpu)
        weight_vector=[-1,cost,speed,security,health,health,deals,instance_size,gpu]
        #########################################################################################################
        if number_of_days=="10":
            choice_10="checked"
        elif number_of_days=="10":
            choice_20="checked"
        elif number_of_days=="30":
            choice_30="checked"
        #########################################################################################################
        # Finding the date index
        try:
            idx=snm_date.index(given_date)
            print("Number of days:",int(number_of_days))
        except:
            idx=-1;number_of_days=-1
        print("Date Index:",idx)
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #########################################################################################################         
        # Optimization Module
        points=[];selection_table="";composit_data=[gnt_array,rlc_array,snm_array,dcp_array]
        gnt_score=0;rlc_score=0;snm_score=0;dcp_score=0;reward=1000;penality=-100
        final_gnt_score=0;final_rlc_score=0;final_snm_score=0;final_dcp_score=0
        if number_of_days!=-1 and idx!=-1:
            for i in range(int(number_of_days)):
                # Loop for every variable 
                per_day_cost_gnt=0;per_day_cost_rlc=0;per_day_cost_snm=0;per_day_cost_dcp=0
                for j in range(1,len(variable_names)):
                    # Skip GPU from cost computations
                    if j==6:
                        all_costs=[per_day_cost_gnt,per_day_cost_rlc,per_day_cost_snm,per_day_cost_dcp]
                        # Apply constraint
                        if gpu==1:
                            Temp_Array=[]
                            for k in range(0,len(token_names)): 
                                if composit_data[k][j][idx+i]==1.0:
                                    Temp_Array.append(reward+all_costs[k])
                                else:
                                    Temp_Array.append(penality)
                            final_gnt_score=final_gnt_score+Temp_Array[0];final_rlc_score=final_rlc_score+Temp_Array[1]
                            final_snm_score=final_snm_score+Temp_Array[2];final_dcp_score=final_dcp_score+Temp_Array[3]
                        if gpu==0:
                            Temp_Array=[]
                            for k in range(0,len(token_names)): 
                                if composit_data[k][j][idx+i]==0.0:
                                    Temp_Array.append(reward+all_costs[k])
                                else:
                                    Temp_Array.append(penality)
                            final_gnt_score=final_gnt_score+Temp_Array[0];final_rlc_score=final_rlc_score+Temp_Array[1]
                            final_snm_score=final_snm_score+Temp_Array[2];final_dcp_score=final_dcp_score+Temp_Array[3]
                        if gpu==-1:
                            final_gnt_score=gnt_score;final_rlc_score=rlc_score
                            final_snm_score=snm_score;final_dcp_score=dcp_score

                    else:
                        # Without constraint
                        A=[]
                        # Run over each token 
                        for k in range(0,len(token_names)):                                   
                            try:
                                T=composit_data[k][j]
                                A.append(float(T[idx+i]))
                            except:
                                A.append(-1)
                        T=A.copy()
                        T=[item for item in A if item!=-1]
                        # print(T)
                        max_a=max(A);min_a=min(T)
                        # print(T,min_a,max_a)
                        normalized_A=[]
                        if j==0 or j==1:
                            # Apply reverse normalization
                            for item in A:
                                if item==-1:
                                    normalized_A.append(-1)
                                else:
                                    normalized_A.append(1-min_max_norm(min_a,max_a,item))
                        else:
                            # Apply normalization
                            for item in A:
                                if item==-1:
                                    normalized_A.append(-1)
                                else:
                                    normalized_A.append(min_max_norm(min_a,max_a,item))

                        print("Normalized",variable_names[j],":",normalized_A)
                        # Cost Function
                        gnt_score=gnt_score+weight_vector[j]*normalized_A[0];rlc_score=rlc_score+weight_vector[j]*normalized_A[1]
                        snm_score=snm_score+weight_vector[j]*normalized_A[2];dcp_score=dcp_score+weight_vector[j]*normalized_A[3]
                        # per day cost computation
                        per_day_cost_gnt=per_day_cost_gnt+weight_vector[j]*normalized_A[0];per_day_cost_rlc=per_day_cost_rlc+weight_vector[j]*normalized_A[1]
                        per_day_cost_snm=per_day_cost_snm+weight_vector[j]*normalized_A[2];per_day_cost_dcp=per_day_cost_dcp+weight_vector[j]*normalized_A[3]

                # Cost Vector
                Temp=[final_gnt_score,final_rlc_score,final_snm_score,final_dcp_score]
                # Maximum Likelihood
                max_indx=Temp.index(max(Temp))
                points.append(max_indx)
                print(gnt_date[idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
                selection_table=selection_table+"<tr><td>"+gnt_date[idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
                print("-----------------------------------------------------------------------------------------")
                # ############################### Price #############################
            #print(points)
            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sored_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            token_1=token_images[sored_indx[3][0]];token_2=token_images[sored_indx[2][0]];token_3=token_images[sored_indx[1][0]];token_4=token_images[sored_indx[0][0]]
        else:
            token_1=token_images[0];token_2=token_images[1];token_3=token_images[2];token_4=token_images[3]
            warning="Data Not available for the selected time period !"
        #########################################################################################################
        return render_template('first_compute_model_result.html',warning=warning,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=deals,bandwidth=instance_size,storage=gpu, init=True)
    except:
        print("Error in Information Extraction|",traceback.print_exc())
        return render_template('first_compute_model_result.html',token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=deals,bandwidth=instance_size,storage=gpu, init=True)
###########################################################################################################################
@app.route("/compute_first_model_data")
def compute_first_model_data():
    global snm_array,gnt_array,rlc_array,dcp_array
    global given_date,number_of_days,selection_table,estimation_table;cost_estimation
    snm_date,snm_price,blocktime_snm,fcas_snm,snm_transection_value,snm_exchange_value,snm_deal,snm_instance,snm_gpu=snm_array
    gnt_date,gnt_price,blocktime_gnt,fcas_gnt,gnt_transection_value,gnt_exchange_value,gnt_deal,gnt_instance,gnt_gpu=gnt_array
    rlc_date,rlc_price,blocktime_rlc,fcas_rlc,rlc_transection_value,rlc_exchange_value,rlc_deal,rlc_instance,rlc_gpu=rlc_array
    dcp_date,dcp_price,blocktime_dcp,fcas_dcp,dcp_transection_value,dcp_exchange_value,dcp_deal,dcp_instance,dcp_gpu=dcp_array
    variable_names=["Date","Price","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Deals","Instance_Size","GPU"]
    print("Given Date:",given_date)
    # Display Filecoin data
    gnt="";rlc="";snm="";dcp=""
    try:
        idx=snm_date.index(given_date)
    except:
        idx=-1
    print("Number of days:",number_of_days,"\t Index",idx)
    if number_of_days!=-1 and idx!=-1:
        for i in range(int(number_of_days)):
            gnt=gnt+"<tr>";rlc=rlc+"<tr>";snm=snm+"<tr>";dcp=dcp+"<tr>"
            # Make a loop for the columns
            for j in range(0,len(variable_names)):
                gnt=gnt+"<td>"+str(gnt_array[j][idx+i])+"</td>";rlc=rlc+"<td>"+str(rlc_array[j][idx+i])+"</td>"
                snm=snm+"<td>"+str(snm_array[j][idx+i])+"</td>";dcp=dcp+"<td>"+str(dcp_array[j][idx+i])+"</td>"
                # print(filecoin_data[j][idx+i],genaro_data[j][idx+i],sia_data[j][idx+i],storj_data[j][idx+i])
                # print("-----------------------------------------------------------------------------------------------")

            gnt=gnt+"</tr>";rlc=rlc+"</tr>";snm=snm+"</tr>";dcp=dcp+"</tr>"

    return render_template('first_compute_model_data.html',table=selection_table,filecoin=gnt,genaro=rlc,sia=snm,storj=dcp, init=True,reload=True)
###########################################################################################################################
@app.route("/second_compute_model")
def second_compute_model():
    return render_template('second_compute_model.html')
    #return "Flask Server is On..."

###############################################################################################################################
@app.route('/compute_second_model_result', methods=['POST'])
def compute_second_model_result():
    global snm_array,gnt_array,rlc_array,dcp_array
    global given_date,number_of_days,selection_table,estimation_table
    snm_date,snm_price,blocktime_snm,fcas_snm,snm_transection_value,snm_exchange_value,snm_deal,snm_instance,snm_gpu=snm_array
    gnt_date,gnt_price,blocktime_gnt,fcas_gnt,gnt_transection_value,gnt_exchange_value,gnt_deal,gnt_instance,gnt_gpu=gnt_array
    rlc_date,rlc_price,blocktime_rlc,fcas_rlc,rlc_transection_value,rlc_exchange_value,rlc_deal,rlc_instance,rlc_gpu=rlc_array
    dcp_date,dcp_price,blocktime_dcp,fcas_dcp,dcp_transection_value,dcp_exchange_value,dcp_deal,dcp_instance,dcp_gpu=dcp_array
    cost=-1;speed=-1;security=-1;deals=-1;instance_size=-1;gpu=-1
    choice_10="";choice_20="";choice_30=""
    token_images=["static/images/GNT.png","static/images/iExec.jpg","static/images/sonm.png","static/images/DCP.png","static/images/invalid.png"]
    token_names=["GNT","RLC","SNM","DCP"]
    variable_names=["Date","Price","Blocktime","FCAS","Transection_Volume","Exchange_Volume","Deals","Instance_Size","GPU"]
    warning=""
    try:
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #########################################################################################################
        given_date=request.form.get("selected_date")
        print("Date:",given_date)
        number_of_days=request.form.get("days")
        print("Days Selected:",number_of_days)
        print("Weightage...")
        cost=int(request.form.get("cost"))
        print("Cost:",cost)
        speed=int(request.form.get("speed"))
        print("Speed:",speed)
        security=int(request.form.get("security"))
        print("Security:",security)
        health=int(request.form.get("health"))
        print("Health:",health)
        deals=int(request.form.get("deals"))
        print("Deals:",deals)
        instance_size=int(request.form.get("instances"))
        print("Instance Size:",instance_size)
        gpu=int(request.form.get("gpu"))
        print("GPU:",gpu)
        
        #########################################################################################################
        try: cost_constraint=int(request.form.get("cost_constraint"))
        except: cost_constraint=-1
        try: speed_constraint=int(request.form.get("speed_constraint"))
        except: speed_constraint=-1
        try: security_constraint=int(request.form.get("security_constraint"))
        except: security_constraint=-1
        try: health_constraint=int(request.form.get("health_constraint"))
        except: health_constraint=-1
        try: deal_constraint=int(request.form.get("deal_constraint"))
        except: deal_constraint=-1
        try: instance_constraint=int(request.form.get("instance_constraint"))
        except: instance_constraint=-1  
        try: gpu_constraint=int(request.form.get("gpu_constraint"))
        except: gpu_constraint=-1       
        ##############################################################################################################
        weight_vector=[-1,cost,speed,security,health,health,deals,instance_size,gpu]
        constraint_vector=[-1,cost_constraint,speed_constraint,security_constraint,health_constraint,health_constraint,
                                        deal_constraint,instance_constraint,gpu]
        #############################################################################################################
        if number_of_days=="10":
            choice_10="checked"
        elif number_of_days=="10":
            choice_20="checked"
        elif number_of_days=="30":
            choice_30="checked"
        #########################################################################################################
        # Finding the date index
        try:
            idx=snm_date.index(given_date)
            print("Number of days:",int(number_of_days))
        except:
            idx=-1;number_of_days=-1
        print("Date Index:",idx)
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #########################################################################################################         
        # Optimization Module
        points=[];selection_table="";composit_data=[gnt_array,rlc_array,snm_array,dcp_array]
        gnt_score=0;rlc_score=0;snm_score=0;dcp_score=0;reward=1000;penality=-100
        final_gnt_score=0;final_rlc_score=0;final_snm_score=0;final_dcp_score=0
        if number_of_days!=-1 and idx!=-1:
            for i in range(int(number_of_days)):
                # Loop for every variable 
                per_day_cost_gnt=0;per_day_cost_rlc=0;per_day_cost_snm=0;per_day_cost_dcp=0
                for j in range(1,len(variable_names)):
                    # Skip GPU from cost computations
                    if j==6:
                        all_costs=[per_day_cost_gnt,per_day_cost_rlc,per_day_cost_snm,per_day_cost_dcp]
                        # Apply constraint
                        if gpu==1:
                            Temp_Array=[]
                            for k in range(0,len(token_names)): 
                                if composit_data[k][j][idx+i]==1.0:
                                    Temp_Array.append(reward+all_costs[k])
                                else:
                                    Temp_Array.append(penality)
                            final_gnt_score=final_gnt_score+Temp_Array[0];final_rlc_score=final_rlc_score+Temp_Array[1]
                            final_snm_score=final_snm_score+Temp_Array[2];final_dcp_score=final_dcp_score+Temp_Array[3]
                        if gpu==0:
                            Temp_Array=[]
                            for k in range(0,len(token_names)): 
                                if composit_data[k][j][idx+i]==0.0:
                                    Temp_Array.append(reward+all_costs[k])
                                else:
                                    Temp_Array.append(penality)
                            final_gnt_score=final_gnt_score+Temp_Array[0];final_rlc_score=final_rlc_score+Temp_Array[1]
                            final_snm_score=final_snm_score+Temp_Array[2];final_dcp_score=final_dcp_score+Temp_Array[3]
                        if gpu==-1:
                            final_gnt_score=gnt_score;final_rlc_score=rlc_score
                            final_snm_score=snm_score;final_dcp_score=dcp_score

                    else:
                        continue

            points,selection_table,predicted_cost=compute_cost_with_constraint_compute(number_of_days,variable_names,token_names,composit_data,
                                                                        idx,snm_array,weight_vector,constraint_vector)
            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sorted_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            sorted_names=[token_names[sorted_indx[3][0]],token_names[sorted_indx[2][0]],token_names[sorted_indx[1][0]],token_names[sorted_indx[0][0]]]
            token_1=token_images[sorted_indx[3][0]];token_2=token_images[sorted_indx[2][0]];token_3=token_images[sorted_indx[1][0]];token_4=token_images[sorted_indx[0][0]]
        else:
            token_1=token_images[0];token_2=token_images[1];token_3=token_images[2];token_4=token_images[3]
            warning="Data Not available for the selected time period !"
        #########################################################################################################
        return render_template('first_compute_model_result.html',warning=warning,token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=deals,bandwidth=instance_size,storage=gpu, init=True)
    except:
        print("Error in Information Extraction|",traceback.print_exc())
        return render_template('first_compute_model_result.html',token_1=token_1,token_2=token_2,token_3=token_3,token_4=token_4,choice_10=choice_10,choice_20=choice_20,choice_30=choice_30,given_date=given_date,number_of_days=number_of_days,cost=cost,speed=speed,security=security,health=deals,bandwidth=instance_size,storage=gpu, init=True)

   
#########################################################################################################################################################
if __name__ == "__main__":
    app.run(debug=True)
    #host="0.0.0.0",use_reloader=True, port=5006,threaded=True
