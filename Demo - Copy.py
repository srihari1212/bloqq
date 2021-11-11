from flask import Flask, request, Response,render_template
import traceback
import os
import xlrd
import pickle
import numpy as np
###########################################################################################################################
# Initialize the Flask Application
app = Flask(__name__)
given_date="";number_of_days=-1;selection_table="";estimation_table=""
given_storage=-1;given_budget=-1
###########################################################################################################################
UPLOAD_FOLDER = os.path.basename('/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
###########################################################################################################################
#load pickle
with open('Dataset/dataset.pkl', 'rb') as f:
    datset=pickle.load(f)
filecoin_data,genaro_data,sia_data,storj_data=datset
###########################################################################################################################
def min_max_norm(min_a,max_a,a):
    try:
        new_max=1;new_min=0
        new_a=((a-min_a)/(max_a-min_a))*(new_max-new_min)+new_min
        return new_a
    except:
        print("Problem in min_max_norm")
###########################################################################################################################
@app.route("/")
def hello():
    return render_template('index.html')
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
    #return "Flask Server is On..."
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
    token_images=["static/images/flipcoin.jpg","static/images/genaro.png","static/images/Siacoin.png","static/images/storj.png"]
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
        try:
            given_storage=int(request.form.get("given_storage"))
        except:
            given_storage=-1
        try:
            given_budget=int(request.form.get("given_budget"))
        except:
            given_budget=-1
        
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
        try:
            idx=filecoin_data[0].index(given_date)
            print("Number of days:",int(number_of_days))
        except:
            idx=-1;number_of_days=-1
                 
        # Optimization Module
        points=[];selection_table="";estimation_table="";balance=given_budget;servive_days=0
        composit_data=[filecoin_data,genaro_data,sia_data,storj_data]
        filecoin_score=0;genaro_score=0;sia_score=0;storj_score=0;predicted_cost=0
        if number_of_days!=-1 and idx!=-1:
            for i in range(int(number_of_days)):
                # Loop for every variable 
                for j in range(1,len(variable_names)):
                    A=[]
                    # Run over each token 
                    for k in range(0,len(token_names)):                                   
                        try:
                            A.append(float(composit_data[k][j][idx+i]))
                        except:
                            A.append(-1)
                    T=A.copy()
                    T=[item for item in A if item!=-1]
                    #print(A)
                    max_a=max(A);min_a=min(T)
                    normalized_A=[]
                    if j==1 or j==2 or j==3:
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
                    #print(filecoin_score,genaro_score,sia_score,storj_score)
                # Cost Vector
                Temp=[filecoin_score,genaro_score,sia_score,storj_score]
                
                # Maximum Likelihood
                max_indx=Temp.index(max(Temp))
                points.append(max_indx)
                print(filecoin_data[0][idx+i]," Scores:",Temp," Choice:",token_names[max_indx])
                selection_table=selection_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(token_names[max_indx])+"</td><td>"+str(max(Temp))+"</td></tr>"
                print("-----------------------------------------------------------------------------------------")

            scores=np.array([[0,points.count(0)],[1,points.count(1)],[2,points.count(2)],[3,points.count(3)]])
            print(scores)
            sored_indx=scores[scores[:, 1].argsort()]
            #print(sored_indx)
            selected_data=composit_data[sored_indx[3][0]]
            for i in range(int(number_of_days)):
                # ############################### computing cost per day #############################
                if given_storage!=-1 and given_budget!=-1:
                    price_cost=0
                    try:
                        # print(selected_data[1][idx+i])
                        price_cost=price_cost+float(selected_data[1][idx+i])
                    except:
                        pass
                    try:
                        # print(selected_data[2][idx+i])
                        price_cost=price_cost+float(selected_data[2][idx+i])
                    except:
                        pass
                    balance=balance-price_cost*given_storage
                    print("Balance:",balance)
                    if balance>0:
                        servive_days=servive_days+1
                        estimation_table=estimation_table+"<tr><td>"+filecoin_data[0][idx+i]+"</td><td>"+str(price_cost*given_storage)+"</td><td>"+str(balance)+"</td></tr>"
                # ############################### computing cost per day (Given only storage) #############################
                if given_storage!=-1 and given_budget==-1:
                    price_cost=0
                    try:
                        # print(selected_data[1][idx+i])
                        price_cost=price_cost+float(selected_data[1][idx+i])
                    except:
                        pass
                    try:
                        # print(selected_data[2][idx+i])
                        price_cost=price_cost+float(selected_data[2][idx+i])
                    except:
                        pass
                    predicted_cost=predicted_cost+price_cost*given_storage
                    print("Cost:",price_cost*given_storage)
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
if __name__ == "__main__":
    app.debug=True
    app.run(host="0.0.0.0",use_reloader=True, port=5000,threaded=True)
