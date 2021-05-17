# -*- coding: utf-8 -*-
"""
Created on Mon May 17 11:01:40 2021

@author: ZZ03MG668
"""

import pandas as pd
import re

def normalize_extra_features(df):
    
    cols_to_normalize = ['pocet_cizincu', 'materske_skoly', 'zakladni_skoly', 'kulturni_zarizeni', 'detska_hriste']

    all_cols = {}
    for column in list(df.columns):
        values = []
        if column in cols_to_normalize:
            for i, item in df[column].iteritems():
                if re.search(r'\d', str(df['city_part_number'][i])) is not None: 
                    norm_coef = df['pocet_obyv'][i]
                    values.append(item/norm_coef)
            all_cols[column] = values
        
        elif column == 'parky':
            for i, item in df[column].iteritems():
                if re.search(r'\d', str(df['city_part_number'][i])) is not None: 
                    norm_coef = df['rozloha'][i]
                    values.append(item/norm_coef)
            all_cols[column] = values
            
        else:
            for i, item in df[column].iteritems():
                if re.search(r'\d', str(df['city_part_number'][i])) is not None:
                    values.append(item)
            all_cols[column] = values
    
    return pd.DataFrame(all_cols).set_index('city_part_number')


extra_features = pd.read_csv('ExtraFeaturesPraha.csv', encoding = 'l2', delimiter = ',', decimal = ',', error_bad_lines=False)
extra_features.rename(columns = {'Unnamed: 0': 'city_part_number'}, inplace = True)

# set columns to numeric
for column in list(extra_features.columns)[1:]:
    if isinstance(extra_features[column][0], str):
        extra_features[column] = extra_features[column].str.replace(',','.')
        extra_features[column] = extra_features[column].str.replace(' ','')
        extra_features[column] = extra_features[column].apply(pd.to_numeric, errors = 'coerce')
        
extra_features.dropna(inplace = True)
extra_features.reset_index(drop = True, inplace = True)

extra_features = normalize_extra_features(extra_features).drop(columns = ['rozloha', 'pocet_obyv'])
extra_features.dropna(inplace = True)

extra_features.to_csv('ExtraFeaturesPraha.csv')


