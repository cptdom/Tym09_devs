# -*- coding: utf-8 -*-
"""
Created on Sun May  9 14:01:19 2021

@author: ZZ03MG668
"""

import json
import pickle
import pandas as pd
import numpy as np
import argparse
import re

CREATE_TEST_JSON = False
DEBUG = False

if CREATE_TEST_JSON:
    test_json = {'tracker_1': 
                 { 'city': 'Praha',
                  'district': 'Praha 3',
                  'email': 'dummy@dummy.praha3',
                  'name': 'Malé byty',
                  'propHigh': '2+1',
                  'propLow': '1+kk',
                  'schedule': 1
                  }, 'tracker_2': 
                 { 'city': 'Praha',
                  'district': 'Praha 4',
                  'email': 'dummy@dummy.praha4',
                  'name': 'Velké byty',
                  'propHigh': '3+1',
                  'propLow': '3+kk',
                  'schedule': 1
                  }, 'tracker_3': 
                 { 'city': 'Praha',
                  'district': 'Praha 1',
                  'email': 'dummy@dummy.praha1',
                  'name': 'Střední byty',
                  'propHigh': '3+1',
                  'propLow': '2+kk',
                  'schedule': 1
                  }
                 }
    
    with open('test_json.json', 'w') as f:
        json.dump(test_json, f)

if DEBUG is not True:
# Create the parser
    my_parser = argparse.ArgumentParser(description='Please list files to use')
    
    # Add the arguments
    my_parser.add_argument('-t',
                          '--Tracker',
                           metavar = '',
                           type=str,
                           help='Specify name/path of tracker json file')
    
    my_parser.add_argument('-m',
                           '--Model',
                           metavar = '',
                           type=str,
                           help='Specify name/path of trained models pickle file')
    
    my_parser.add_argument('-d',
                           '--Database',
                           metavar = '',
                           type=str,
                           help='Specify name/path of database of scraped flats')
    
    args = my_parser.parse_args()
    
    trackers = args.Tracker
    models = args.Model
    database = args.Database
     
# LOAD DATA

if DEBUG:
    trackers = 'test_json.json'
    models = 'all_models_dict_v2.pickle'
    database = 'processed_dataset.csv'

with open(trackers, 'r') as f:
    trackers = json.load(f)
    
with open(models, 'rb') as f:
    model_dict = pickle.load(f)
    
df = pd.read_csv(database, index_col = 0)


def predict(model_dict, model_type, data):
    
    '''
    predicts price of a single flat based on trained model
    
    model_dict = loaded dictionary of pretrained models for each flat size small/medium/large
    model_type = what model to use? small/medium/large
    data = row of features to predict price for (a single flat)
    
    '''
    return ((0.35 * model_dict[model_type]['stacker'].predict(data)) +
            (0.25 * model_dict[model_type]['XGBRegressor'].predict(data)) +
            (0.15 * model_dict[model_type]['BaggingRegressor'].predict(data)) +  
            (0.25 * model_dict[model_type]['LGBMRegressor'].predict(data)))
    
# PREDICT PRICES

def extract_room_size_as_string(row):
    
    '''
    returns a string of 'low', 'medium' or 'large' based on amount of rooms of a flat 
    is meant to be used as df.apply(<this func>)
    
    row = row of dataframe
    
    '''
    
    if '2' in str(row):
        row = 'medium'
    elif '3' in str(row) or '4' in str(row):
        row = 'large'
    elif '1' in str(row):
        row = 'small'
    else:
        row = pd.NA
    return row

def predict_prices_for_all_flats(df, model_dict):
    
    '''
    predicts prices for all flats in specified file based on trained dictionary of models (a blender of 4 models,
                                                                                           for each size (small, medium, large))
    
    df = scraped dataset of all flats, preprocessed
    model_dict = dictionary with trained models (keys for small, medium and large model blenders)
    
    '''

    df['rooms_string'] = df['rooms'].apply(extract_room_size_as_string)
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

def return_size_from_input_json(dictionary):
    
    '''
    returns size required by customer specified in tracker (based on high and low interval)
    
    dictionary = dictionary for each tracker (works based on looping through json with tracker IDs)
    
    '''

    low = re.search(r'\d+', dictionary['propLow'])
    low = int(low.group(0) if low is not None else None)
    
    high = re.search(r'\d+', dictionary['propHigh'])
    high = int(high.group(0) if high is not None else None)
    
    if high == low:
        if high == 1:
            size = ['small']
        elif high == 2:
            size = ['medium']
        else:
            size = ['large']
            
    elif high > 2 and low == 2:
        size = ['medium' ,'large']
    
    elif high == 2 and low == 1:
        size = ['small', 'medium']
        
    else:
        size =''
        print('Error in determining size: please make sure high >= low')
    return size

def filter_underpriced_flats(df):
    
    '''
    filters all flats and returns only the underpriced ones
    
    df = dataset of all scraped flats
    
    '''
    
    underpriced_df = predict_prices_for_all_flats(df, model_dict)
    
    underpriced_df = underpriced_df[underpriced_df['price'] < underpriced_df['predicted']]
    
    underpriced_df['difference'] = underpriced_df['predicted'] - underpriced_df['price']
    
    return underpriced_df

def generate_recommendations_for_each_tracker(dataset, request, number_of_flats = 10):
    
    '''
    generates recommendations for each tracker id based on conditions set in that tracker
    
    dataset = file with all scraped flats to be filtered and predicted
    request = json file with tracker IDs and conditions 
    number_of_flats = how many flats to recommend (default 10)
    
    '''
    
    recommendations = {}
    
    underpriced_flats = filter_underpriced_flats(dataset)
    
    for tracker, data in request.items():
    
        tracker_id = tracker
        size = return_size_from_input_json(data)
        district = data['district']
        email = data['email']
        
        flats_temp = underpriced_flats[underpriced_flats['rooms_string'].isin(size) & \
                                underpriced_flats['district'].eq(district)].sort_values('difference', ascending = False)
            
        recommendations[tracker_id] = {'links': list(flats_temp[:number_of_flats].index),
                                       'email': email,
                                       'district': district}
    
    return recommendations

recommendations = generate_recommendations_for_each_tracker(df, trackers, 10)

with open('recommendations.json', 'w') as out:
    json.dump(recommendations, out)
