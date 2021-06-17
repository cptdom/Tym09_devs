import pandas as pd
from airflow.providers.mongo.hooks.mongo import MongoHook
from pymongo.errors import BulkWriteError

from dags.utils.bezrealitky_scrape import bezrealitky_scrape
from dags.utils.vars import DEFAULT_ARGS


def mongo_push(data):
  data['date_updated'] = pd.to_datetime('today').strftime("%Y-%m-%d %H:%M")
  data.rename(columns={'link': '_id'}, inplace=True)  # use 'link' as unique id
  docs = data.to_dict('records')
  if docs:
    push_docs(docs, DEFAULT_ARGS['mongo_master_collection'])
    push_docs(docs, DEFAULT_ARGS['mongo_current_collection'])

def push_docs(docs, collection):
  mongo = MongoHook(conn_id='mongo_reality')
  try:
    mongo.insert_many(
      docs=docs,
      mongo_collection=collection,
      mongo_db=DEFAULT_ARGS['mongo_dbname'],
      ordered=False
    )
  except BulkWriteError as bwe:
    print("Some duplicates were found and skipped.")
  except Exception as e:
    print({'error': str(e)})
  return True

mongo_push(bezrealitky_scrape())