#%%
import pandas as pd
from pandas_profiling import ProfileReport
from pymongo import MongoClient

username = '*'
password = '*'
client = MongoClient(f'mongodb+srv://{username}:{password}@cluster0.mtfak.mongodb.net/myFirstDatabase')
db = client.reality
df = pd.DataFrame(list(db.masterdata.find()))

profile = ProfileReport(df, title="Data Report")
profile.to_file("masterdata_2021_05_14.html")