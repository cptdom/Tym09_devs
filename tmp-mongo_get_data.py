#%%
import pandas as pd
from pymongo import MongoClient

username = 'xxx'
password = 'xxx'
client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.mtfak.mongodb.net/myFirstDatabase')
db = client.reality
data = pd.DataFrame(list(db.masterdata.find()))