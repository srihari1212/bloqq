def compute_cost(number_of_days,variable_names,token_names,composit_data,idx,filecoin_data):
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
                #print(A)
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