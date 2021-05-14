import json
import pickle
import pandas as pd
import numpy as np
import argparse
import re

from airflow.providers.mongo.hooks.mongo import MongoHook

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
    df = df.dropna(subset=['rooms_string'])

    predictions = []

    df_with_predictions = df.copy()

    from tqdm import tqdm

    for i, row in tqdm(df[df.columns[~df.columns.isin(['price', 'district'])]].iterrows()):
        s = row['rooms_string']
        flat = np.array(row[:-1]).reshape(1, -1)

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
        size = ['medium', 'large']

    elif high == 2 and low == 1:
        size = ['small', 'medium']

    elif high > 3 and low == 1:
        size = ['small', 'medium', 'large']

    else:
        size = ['']
        print('\nError in determining size: please make sure high >= low')
    return size


def filter_underpriced_flats(df, model_dict):
    '''
    filters all flats and returns only the underpriced ones
    
    df = dataset of all scraped flats
    
    '''

    underpriced_df = predict_prices_for_all_flats(df, model_dict)

    underpriced_df = underpriced_df[underpriced_df['price'] < underpriced_df['predicted']]

    underpriced_df['difference'] = underpriced_df['predicted'] - underpriced_df['price']

    return underpriced_df


def generate_recommendations_for_each_tracker(dataset, request, model_dict, number_of_flats=10):
    '''
    generates recommendations for each tracker id based on conditions set in that tracker
    
    dataset = file with all scraped flats to be filtered and predicted
    request = json file with tracker IDs and conditions 
    number_of_flats = how many flats to recommend (default 10)
    
    '''

    print('GENERATING RECOMMENDATIONS...')
    recommendations = {}

    underpriced_flats = filter_underpriced_flats(dataset, model_dict)
    # with open('./underpriced.pickle', 'rb') as f:
    #     underpriced_flats = pickle.load(f)

    for tracker, data in request.items():
        tracker_id = tracker
        size = return_size_from_input_json(data)
        district = data['district']
        email = data['email']

        flats_temp = underpriced_flats[underpriced_flats['rooms_string'].isin(size) & \
                                       underpriced_flats['district'].eq(district)].sort_values('difference',
                                                                                               ascending=False)

        recommendations[tracker_id] = {'links': list(flats_temp[:number_of_flats].index),
                                       'email': email,
                                       'district': district,
                                       'difference': list(flats_temp.iloc[:number_of_flats]['difference']),
                                       'predicted_price': list(flats_temp.iloc[:number_of_flats]['predicted']),
                                       'actual_price': list(flats_temp.iloc[:number_of_flats]['price'])}

    return recommendations


def get_all_underpriced_flats(recommendations, to_excel=False):
    l = []
    p = []
    a = []
    d = []

    for tracker, values in recommendations.items():
        # underpriced_flats['tracker'].append(tracker)
        for li in values['links']:
            l.append(li)
        for pr in values['predicted_price']:
            p.append(pr)
        for ac in values['actual_price']:
            a.append(ac)
        for di in values['difference']:
            d.append(di)

    underpriced_flats = pd.DataFrame({'links': l, 'predicted_price': p, 'actual_price': a, 'difference': d})

    if to_excel:
        underpriced_flats.to_excel('podcenene_byty.xlsx')

    return underpriced_flats


def run_apart_predictions(df_processed, default_args, n_predictions=5):
    print('EVALUATING APARTMENT PRICES...')

    # load pickled models
    with open('./all_models_dict_v2.pickle', 'rb') as f:
        model_dict = pickle.load(f)

    mongo = MongoHook(conn_id='mongo_reality')
    trackers_list = list(mongo.find(
        mongo_collection=default_args['mongo_trackers_collection'],
        query={},
        mongo_db=default_args['mongo_trackers_dbname']
    ))
    trackers = {str(x['_id']): x for x in trackers_list}

    return generate_recommendations_for_each_tracker(df_processed, trackers, model_dict, n_predictions)