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
  def remax_task(dummy):
    return remax_scrape()

  @task()
  def prazskereality_task(dummy):
    return prazskereality_scrape()

  @task()
  def bezrealitky_task(dummy):
    return bezrealitky_scrape()

  @task()
  def idnes_task(dummy):
    return idnes_scrape()

  @task()
  def sreality_task(dummy):
    return sreality_scrape()

  @task()
  def mongo_prepare():
    mongo = MongoHook(conn_id='mongo_reality')
    # truncate 'current' collection and insert current data
    mongo.delete_many(
      filter_doc={},
      mongo_collection=default_args['mongo_current_collection'],
      mongo_db=default_args['mongo_dbname']
    )
    return True

  @task()
  def mongo_push(data):
    data['date_updated'] = pd.to_datetime('today').normalize()
    data.rename(columns={'link': '_id'}, inplace=True)  # use 'link' as unique id
    docs = data.to_dict('records')

    if docs:
      mongo = MongoHook(conn_id='mongo_reality')
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

      mongo.insert_many(
        docs=docs,
        mongo_collection=default_args['mongo_current_collection'],
        mongo_db=default_args['mongo_dbname']
      )

  data = {
    'remax': remax_task,
    'prazskereality': prazskereality_task,
    'bezrealitky': bezrealitky_task,
    'idnes': idnes_task,
    'sreality': sreality_task
  }

  res = mongo_prepare()
  for name,fn in data.items():
    mongo_push(fn(res))

scrape_dag_taskflow = scrape_taskflow()
