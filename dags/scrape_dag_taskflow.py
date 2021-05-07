from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.utils.dates import days_ago
from airflow.decorators import dag, task
from pymongo.errors import BulkWriteError

from utils.prazskereality_scrape import prazskereality_scrape
from utils.remax_scrape import remax_scrape
from utils.bezrealitky_scrape import bezrealitky_scrape
from utils.sreality_scrape import sreality_scrape
from utils.idnes_scraper import idnes_scrape

import pandas as pd

default_args = {
  'owner': 'airflow',
  'mongo_master_collection': 'masterdata',
  'mongo_current_collection': 'currentdata',
  'mongo_dbname': 'reality'
}

@dag(default_args=default_args, schedule_interval=None, start_date=days_ago(2), tags=['scraper', 'mongo'])
def scrape_taskflow():
  @task()
  def remax_task():
    return remax_scrape(debug=True)

  @task()
  def prazskereality_task():
    return prazskereality_scrape()

  @task()
  def bezrealitky_task():
    return bezrealitky_scrape(debug=True)

  @task()
  def idnes_task():
    return idnes_scrape(debug=True)

  @task()
  def sreality_task():
    return sreality_scrape(debug=True)

  @task()
  def merge_mongo_push(data):
    df = pd.DataFrame()
    for s_name, s_df in data.items():
      print(f"MERGING {s_name}...")
      df = df.append(s_df)

    print(f"MERGED...")
    df['date_updated'] = pd.to_datetime('today').normalize()
    df.rename(columns={'link': '_id'}, inplace=True)  # use 'link' as unique id
    print(df)
    docs = df.to_dict('records')
    mongo = MongoHook(conn_id='mongo_reality')
    # insert into 'master' collection while ignoring duplicate errors
    try:
      mongo.insert_many(
        docs=docs,
        mongo_collection=default_args['mongo_master_collection'],
        mongo_db=default_args['mongo_dbname'],
        ordered=False
      )
    except BulkWriteError as bwe:
      print("Some duplicates were found and skipped.")
    except Exception as e:
      print({'error': str(e)})

    # truncate 'current' collection and insert current data
    mongo.delete_many(
      filter_doc={},
      mongo_collection=default_args['mongo_current_collection'],
      mongo_db=default_args['mongo_dbname']
    )
    mongo.insert_many(
      docs=docs,
      mongo_collection=default_args['mongo_current_collection'],
      mongo_db=default_args['mongo_dbname']
    )

  data = {
    'remax': remax_task(),
    'prazskereality': prazskereality_task(),
    'bezrealitky': bezrealitky_task(),
    'idnes': idnes_task(),
    'sreality': sreality_task()
  }
  merge_mongo_push(data)

scrape_dag_taskflow = scrape_taskflow()
