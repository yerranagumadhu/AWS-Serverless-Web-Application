import pandas as pd
import numpy as np
import wikipedia
import pickle
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy  import process
import boto3
from json.decoder import JSONDecodeError
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier 



def lambda_handler(event, context):
    
    r = json.dumps(event)
    loaded_r = json.loads(r)
    
    
    if (loaded_r['context']['http-method'] == 'POST'):
        
        print(loaded_r['context']['http-method'])
        
        wines = pd.read_csv("https://happi2learn.s3.us-east-2.amazonaws.com/winequalityN.csv")
        
        wines_bad_q = wines[wines['quality'].isin(['3','4','5'])]
        wines_bad_q['quality'] = 3
        
        wines_good_q = wines[wines['quality'] == 6]
        
        wines_best_q = wines[wines['quality'].isin([7,8,9])]
        
        wines_best_q['quality'] = 9
        
        wines_balance_df =  pd.concat([wines_bad_q,wines_good_q,wines_best_q], ignore_index = True)
        wines_balance_df = wines_balance_df.replace({'type' : {'white' :0, 'red':1 }})
        wines_balance_df['quality'] = pd.Categorical(wines_balance_df['quality'])
        
        features = [ft for ft in list(wines_balance_df) if ft not in ['quality']]
        np.where(np.isnan(wines_balance_df['type']))
        wines_balance_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
        
        features = [i for i in list(wines_balance_df) if i not in ['quality']]
        wines_balance_df['quality'] = pd.Categorical(wines_balance_df['quality'])
        wines_balance_df['quality_class'] = wines_balance_df['quality'].cat.codes
        outcome = 'quality_class'
        outcome_buckets = len(set(wines_balance_df['quality_class']))
        
        
        x_train, x_test, y_train, y_test = train_test_split(wines_balance_df[features], wines_balance_df[outcome], test_size=0.2, random_state=1 )
        
        x_train = x_train.fillna(x_train.mean())
        x_test = x_test.fillna(x_test.mean())
        
        
    
        gb_model = GradientBoostingClassifier(random_state=10, learning_rate=0.1, max_depth=10)
        gb_model.fit(x_train[features],y_train)
        
        
        print(event)
        #r = json.dumps(event) #json.dumps() will convert the json object to string
        #print(r)
        #print(r['body-json'])
        
        #print(event["body"])
        #print(json.loads(event["body"]))
        
        #print(event["httpMethod"])
        
        load_r = json.loads(json.dumps(loaded_r["body"]))
        
        #print(json.loads(r["body"]))
        #loaded_r = json.loads(r) #json.loads() will convert the string to dict object
        #print(load_r)
        
        #print("after converting one one body inside the body")
        
        load_r = json.loads(json.dumps(load_r["body"]))
        
        #print(load_r)
        
        
        type                =  load_r['type']
        fixed_acidity       =  load_r['fixed_acidity']
        volatile_acidity    =  load_r['volatile_acidity']
        citric_acid         =  load_r['citric_acid']
        residual_sugar      =  load_r['residual_sugar']
        chlorides           =  load_r['chlorides']
        free_sulfur_dioxide =  load_r['free_sulfur_dioxide']
        total_sulfur_dioxide=  load_r['total_sulfur_dioxide']
        density             =  load_r['density']
        pH                  =  load_r['pH']
        sulphates           =  load_r['sulphates']
        alcohol             =  load_r['alcohol']
        
        features = ['type', 'fixed acidity', 'volatile acidity', 'citric acid','residual sugar', 'chlorides', 'free sulfur dioxide', 'total sulfur dioxide', 'density', 'pH', 'sulphates', 'alcohol']
        x_test = pd.DataFrame([[type,fixed_acidity, volatile_acidity, citric_acid,  residual_sugar,  chlorides, free_sulfur_dioxide,  total_sulfur_dioxide,  density,  pH,  sulphates, alcohol]], columns = features)
        
        
        predicted_val       = gb_model.predict_proba(x_test[features])
        predicted_quality   = ['Bad Quality','Good Quality','Best Quality'][np.argmax(predicted_val)]
        image               = ['Bad_quality_wine.jpg','Good_quality_wine.jpg','Best_quality_wine.jpg'][np.argmax(predicted_val)]
        k = {'quality_prediction':0}
        
        print('predicted_quality: ', predicted_quality)
        print('image: ', image)
        
        k = {'predicted_quality':predicted_quality,'image':image}
        
    
        
        return {
            'statusCode': 200,
            'body': json.dumps(k)
        }
    else:
        
        #default_val = json.dumps("https://happi2learn.s3.us-east-2.amazonaws.com/static/data/default_val_fixed.json")
        #print(default_val)
        
        s3_obj =boto3.client('s3')

        s3_clientobj = s3_obj.get_object(Bucket='happi2learn', Key='default_val_fixed.json')
        s3_clientdata = s3_clientobj['Body'].read().decode('utf-8')
        
        s3clientlist=json.loads(s3_clientdata)
        
        print(s3clientlist)
        
        return {
            'statusCode': 200,
            'body': json.dumps(s3clientlist)
        }