#%%
import pandas as pd
from pymongo import MongoClient

username = 'cerm20'
password = 'cerm20MNGDB'
client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.mtfak.mongodb.net/myFirstDatabase')
db = client.reality
data = pd.DataFrame(list(db.debugcurrentdata.find()))