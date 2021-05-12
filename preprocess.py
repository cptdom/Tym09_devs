# -*- coding: utf-8 -*-
"""
Created on Sun May  9 14:30:10 2021

@author: ZZ03MG668
"""

import pandas as pd
import numpy as np
from pymongo import MongoClient
import requests
import io
import re
from sklearn.impute import SimpleImputer
import category_encoders as ce

username = '*'
password = '*'
client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.mtfak.mongodb.net/myFirstDatabase')
db = client.reality
df = pd.DataFrame(list(db.masterdata.find()))

cols_to_drop = ['floor_area', 
 'locality', 
 'building_state', 
 'garage', 
 'parking', 
 'obcanska_vybavenost', 
 'odpad', 
 'voda', 
 'doprava', 
 'umistneni_objektu', 
 'loggia', 
 'gas', 
 'annual_electricity', 
 'electricity', 
 'heating', 
 'internet', 
 'floor_max', 
 'date_updated', 
 'barrier_free', 
 'equipment', 
 'updated',
 'address',
 'title',
 'city',
 'size',
 'street',
 'description']

### helper functions
# normalize unicode characters
def normalize_unicode(row):
    import unicodedata
    return unicodedata.normalize('NFKD', row)

# ziskej část prahy (1, 12, 20, 4...)
def get_prague_part_number(row):
    import re
    prague = re.search(r'(Praha)(\s)()(\d*)', row)
    if prague is not None:
        prague = prague.group(0)
    return prague

# pocet pokoju
def get_number_of_rooms(row):
    if 'Garsoniéra' in str(row):
        n_rooms = 1
    elif 'Ostatní' in str(row):
        n_rooms = np.nan
    else:
        n_rooms = str(row)[:1]
    return n_rooms

# get floor number
def get_floor_number(row):
    import re
    floor = re.search(r'([-\d]+)', str(row))
    if floor is not None:
        floor = floor[0]
    return floor  

# set commas to dots
def set_comma_to_dot(row):
    if isinstance(row, str):
        row = row.replace(',','.')
    return row

def set_lower_and_strip(row):
    if isinstance(row, str):
        row = row.strip().lower()
    return row

# set index as link
df.set_index('_id', inplace = True)

#normalize and get prague part number
df['address'] = df['address'].apply(normalize_unicode)
df['city_part_number'] = df.address.apply(get_prague_part_number)
df['city_part_number'].replace({'Praha ': np.nan, 'Prana\n': np.nan}, inplace = True)

# convert size to rooms & kitchen
df.dropna(subset = ['size'], inplace = True)
df['rooms'] = df['size'].apply(get_number_of_rooms)
df['kitchen'] = df['size'].apply(lambda x: False if 'kk' in str(x) else True)

df = df.drop(columns = cols_to_drop)

# rename categories, lower etc.
df['building_type'] = df['building_type'].replace({'Cihla': 'cihlová',
                                                    'Cihlová': 'cihlová',
                                                    'Panel': 'panelová',
                                                    'Panelová': 'panelová',
                                                    'Smíšená': 'smíšená',
                                                    'Skeletová': 'skeletová',
                                                    'Kamenná': 'kamenná',
                                                    'Montovaná': 'montovaná'})

df['state'] = df['state'].apply(set_lower_and_strip)
df['state'] = df['state'].replace({'udržovaný': 'dobrý',
                                                    'dobrý stav': 'dobrý',
                                                    've výstavbě (hrubá stavba)': 've výstavbě'})

# fill nans
for column in ['basement', 'elevator', 'balcony', 'terrace']:
    df[column].fillna(False, inplace = True)
df['penb'].fillna('G', inplace = True)

# clean penb
df['penb'] = df['penb'].apply(lambda x: str(x)[:1])

# get floor number
df['floor'] = df['floor'].apply(get_floor_number)
          
# convert True/False to 1/0 
df['price'] = df['price'].apply(set_comma_to_dot)

df = df.replace('null', np.nan, regex = True)

for column in ['balcony', 'basement', 'elevator', 'terrace', 'kitchen', 'rooms', 'price', 'floor']:
    df[column] = df[column].astype(np.float32)

# remove flats more expensive than 30 mil
df = df[df['price'].lt(30_000_000)]

# some area wrongly empty string value 
df['area'] = df['area'].replace('', np.nan, regex = True)


#####################################################################################################################
###########EXTRA FEATURES############################################################################################
#####################################################################################################################

user='jachymDvorak'
pao='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'

github_session = requests.Session()
github_session.auth = (user, pao)

    # providing raw url to download csv from github
csv_url = 'https://raw.githubusercontent.com/ToVic/Tym09_devs/main/ExtraFeaturesPraha.csv'

download = github_session.get(csv_url).content
extra_features = pd.read_csv(io.StringIO(download.decode('latin2')), delimiter = ';', decimal = ',', error_bad_lines=False)

extra_features.rename(columns = {'Unnamed: 0': 'city_part_number'}, inplace = True)

# set columns to numeric
for column in list(extra_features.columns)[1:]:
    if isinstance(extra_features[column][0], str):
        extra_features[column] = extra_features[column].str.replace(',','.')
        extra_features[column] = extra_features[column].str.replace(' ','')
        extra_features[column] = extra_features[column].apply(pd.to_numeric, errors = 'coerce')
        
extra_features.dropna(inplace = True)
extra_features.reset_index(drop = True, inplace = True)

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

extra_features = normalize_extra_features(extra_features).drop(columns = ['rozloha', 'pocet_obyv'])
extra_features.dropna(inplace = True)

df = df.merge(extra_features, how = 'left', left_on = 'city_part_number', right_index = True)
#df.drop(columns = 'city_part_number', inplace = True)

#####################################################################################################################
###########preprocessing############################################################################################
#####################################################################################################################

numerical_cols = ['area', 
                  'rooms', 
                 'floor',
                 'rooms',
                 'pocet_cizincu',
                 'materske_skoly',
                 'zakladni_skoly',
                 'hustota_zalidneni',
                 'index_stari',
                 'kulturni_zarizeni',
                 'rekreacni_plochy',
                 'sportovni_plochy',
                 'detska_hriste',
                 'lesy_lesoparky',
                 'parky',
                 'znecisteni_ovzdusi',
                 'obyv_nocni_hluk',
                 'podil_zastavenych_ploch']

numeric_imputer = SimpleImputer(strategy='mean')

categorical_cols = ['owner', 
                    'building_type', 
                    'penb', 
                    'state',
                    'city_part']
    
encoder = ce.TargetEncoder(return_df = True, cols = categorical_cols, verbose = 1, min_samples_leaf = 10)
categorical_imputer = SimpleImputer(strategy='most_frequent')

df_city_part = df.pop('city_part_number')
y = df.pop('price').astype(float)
X = df

X = encoder.fit_transform(X, y)
X = categorical_imputer.fit_transform(X)
X = numeric_imputer.fit_transform(X)

processed_dataset = pd.DataFrame(X, columns = list(df.columns), index = df.index)
processed_dataset['price'] = y.values
processed_dataset['district'] = df_city_part

processed_dataset.to_csv('processed_dataset.csv', index = True)
