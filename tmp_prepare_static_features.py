#%%
import io

import pandas as pd
import re
import requests
from pymongo import MongoClient

user='jachymDvorak'
pao='*'

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
        extra_features[column] = extra_features[column].str.replace(',', '.')
        extra_features[column] = extra_features[column].str.replace(' ', '')
        extra_features[column] = extra_features[column].apply(pd.to_numeric, errors='coerce')

extra_features.dropna(inplace=True)
extra_features.reset_index(drop=True, inplace=True)

def normalize_extra_features(df):
    cols_to_normalize = ['pocet_cizincu', 'materske_skoly', 'zakladni_skoly', 'kulturni_zarizeni', 'detska_hriste']

    all_cols = {}
    for column in list(df.columns):
        values = []
        if column in cols_to_normalize:
            for i, item in df[column].iteritems():
                if re.search(r'\d', str(df['city_part_number'][i])) is not None:
                    norm_coef = df['pocet_obyv'][i]
                    values.append(item / norm_coef)
            all_cols[column] = values

        elif column == 'parky':
            for i, item in df[column].iteritems():
                if re.search(r'\d', str(df['city_part_number'][i])) is not None:
                    norm_coef = df['rozloha'][i]
                    values.append(item / norm_coef)
            all_cols[column] = values

        else:
            for i, item in df[column].iteritems():
                if re.search(r'\d', str(df['city_part_number'][i])) is not None:
                    values.append(item)
            all_cols[column] = values

    return pd.DataFrame(all_cols).set_index('city_part_number')


extra_features = normalize_extra_features(extra_features).drop(columns=['rozloha', 'pocet_obyv'])
extra_features.dropna(inplace=True)
extra_features.reset_index(inplace=True)

docs = extra_features.to_dict('records')

username = '*'
password = '*'
client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.mtfak.mongodb.net/myFirstDatabase')


client.reality.extrafeatures.delete_many(filter={}) # dump existing data
client.reality.extrafeatures.insert_many(docs)