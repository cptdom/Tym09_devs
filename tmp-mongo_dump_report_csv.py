#%%
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import category_encoders as ce
from astronomer.dags.utils import preprocess

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
        row = row.replace(',', '.')
    return row


def set_lower_and_strip(row):
    if isinstance(row, str):
        row = row.strip().lower()
    return row


username = 'cerm20'
password = 'cerm20MNGDB'
client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.mtfak.mongodb.net/myFirstDatabase')
db = client.reality
df = pd.DataFrame(list(db.masterdata.find()))

# set index as link
df.set_index('_id', inplace=True)
# normalize and get prague part number
df['address'] = df['address'].apply(normalize_unicode)
df['city_part_number'] = df.address.apply(get_prague_part_number)
df['city_part_number'].replace({'Praha ': np.nan, 'Prana\n': np.nan}, inplace=True)
# convert size to rooms & kitchen
df.dropna(subset=['size'], inplace=True)
df['rooms'] = df['size'].apply(get_number_of_rooms)
df['kitchen'] = df['size'].apply(lambda x: False if 'kk' in str(x) else True)
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
    df[column].fillna(False, inplace=True)
df['penb'].fillna('G', inplace=True)
# clean penb
df['penb'] = df['penb'].apply(lambda x: str(x)[:1])
# get floor number
df['floor'] = df['floor'].apply(get_floor_number)
# convert True/False to 1/0
df['price'] = df['price'].apply(set_comma_to_dot)
df = df.replace('null', np.nan, regex=True)

for column in ['rooms', 'price', 'floor']:
    df = df[~df[column].str.contains('[^0-9]', na=False)] # remove rows that does not contain number in col
    df[column] = df[column].astype(np.float32)

# combination of bool,string,nans
for column in ['balcony', 'basement', 'elevator', 'terrace']:
    df[column] = df[column].str.lower()
    df[column].replace('ne', np.nan, inplace=True)
    df[column] = df[column].isna()

# some area wrongly empty string value
df['area'] = df['area'].replace('', np.nan, regex=True)

df.to_csv('masterdata.csv', sep=';')

# merge and keep links as indices
# df = df.reset_index().merge(extra_features, how='left', left_on='city_part_number',
#                             right_on='city_part_number').set_index('_id')

