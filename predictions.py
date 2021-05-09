# -*- coding: utf-8 -*-
"""
Created on Sun May  9 14:01:19 2021

@author: ZZ03MG668
"""

import json
import pickle
import pandas as pd
import numpy as np
import xgboost
 
CREATE_JSON = False

if CREATE_JSON:
    test_json = {'tracker_1': 
                 { 'city': 'Praha',
                  'district': 'Praha 3',
                  'email': 'dummy@dummy.cz',
                  'name': 'Malé byty',
                  'propHigh': '1+1',
                  'propLow': '1+kk',
                  'schedule': 1
                  }, 'tracker_2': 
                 { 'city': 'Praha',
                  'district': 'Praha 2',
                  'email': 'dummy@dummy.cz',
                  'name': 'Velké byty',
                  'propHigh': '3+1',
                  'propLow': '3+kk',
                  'schedule': 1
                  }
                 }
    
    with open('test_json.json', 'w') as f:
        json.dump(test_json, f)

# LOAD DATA

with open('test_json.json', 'r') as f:
    test_json = json.load(f)
    
with open('all_models_dict_v2.pickle', 'rb') as f:
    model_dict = pickle.load(f)
    
df = pd.read_csv('processed_dataset.csv', index_col = 0)


def predict(model_dict, model_type, data):
    return ((0.35 * model_dict[model_type]['stacker'].predict(data)) +
            (0.25 * model_dict[model_type]['XGBRegressor'].predict(data)) +
            (0.15 * model_dict[model_type]['BaggingRegressor'].predict(data)) +  
            (0.25 * model_dict[model_type]['LGBMRegressor'].predict(data)))
    

# PREDICT PRICES

def extract_size_string(row):
    
    if '2' in str(row):
        row = 'medium'
    elif '3' in str(row) or '4' in str(row):
        row = 'large'
    elif '1' in str(row):
        row = 'small'
    else:
        row = pd.NA
    return row

def predict_prices(df, model_dict):

    df['rooms_string'] = df['rooms'].apply(extract_size_string)
    df = df.dropna(subset = ['rooms_string'])    

    predictions = []

    df_with_predictions = df.copy()
        
    from tqdm import tqdm
    
    for i, row in tqdm(df[df.columns[~df.columns.isin(['price','district'])]].iterrows()):
        
        s = row['rooms_string']
        flat = np.array(row[:-1]).reshape(1, -1)
        
        if s == 'small':
            prediction = predict(model_dict, s, flat)
        elif s == 'medium':
            prediction = predict(model_dict, s, flat)    
        elif s == 'large':
            prediction = predict(model_dict, s, flat)   
    
        predictions.append(int(prediction))
    
    df_with_predictions['predicted'] = predictions
    
    return df_with_predictions

def return_size(dictionary):

    if 'malé' in dictionary['name'].lower():
        size = 'small'
    elif 'střední' in dictionary['name'].lower():
        size = 'medium'
    else:
        size = 'large'

    return size

def get_underpriced_flats(df):
    
    underpriced_df = predict_prices(df, model_dict)
    
    underpriced_df = underpriced_df[underpriced_df['price'] < underpriced_df['predicted']]
    
    underpriced_df['difference'] = underpriced_df['predicted'] - underpriced_df['price']
    
    return underpriced_df

def recommendation_generator(dataset, request, number_of_flats): 
    
    recommendations = {}
    
    flats_temp = get_underpriced_flats(dataset)
    
    for tracker, data in request.items():
    
        tracker_id = tracker
        size = return_size(data)
        district = data['district']
        email = data['email']
        
        flats_temp = flats_temp[flats_temp['rooms_string'].eq(size) & \
                                flats_temp['district'].eq(district)].sort_values('difference', ascending = False)
        recommendations[tracker_id] = {'links': list(flats_temp[:number_of_flats].index),
                                       'email': email,
                                       'district': district}
    
    return recommendations

recommendations = recommendation_generator(df, test_json, 15)

