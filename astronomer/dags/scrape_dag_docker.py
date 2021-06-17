from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago
from pymongo.errors import BulkWriteError

DAG_NAME = 'scrape_reality'

default_args = {
  'owner': 'airflow',
  'mongo_master_collection': 'masterdata',
  'mongo_current_collection': 'currentdata',
  'mongo_dbname': 'reality',
  'local_datafolder': '/tmp',
  'scrapers': {
    'prazskereality': {
      'script': 'prazskereality_scrape.py',
      'out_filename': 'prazskereality.csv'
    },
    'idnes': {
      'script': 'idnes_scraper.py',
      'out_filename': 'idnes.csv'
    },
    'remax': {
      'script': 'remax_scrape.py',
      'out_filename': 'remax.csv'
    },
    'sreality': {
      'script': 'sreality_scrape.py',
      'out_filename': 'sreality.csv'
    }
  }
}

dag = DAG(
  DAG_NAME,
  default_args=default_args,
  description='Scrape reality to Mongo',
  schedule_interval=None,
  start_date=days_ago(2),
  tags=['scraper', 'mongo'],
)

scraper_tasks = []

# create scraper tasks using definition
for k, v in default_args['scrapers'].items():
  scraper_tasks.append(
    DockerOperator(
      api_version='auto',
      command=f'python3 {v["script"]}',
      image='scraper_base',
      network_mode='bridge',
      task_id=f'scraper_{k}',
      volumes=[f'{default_args["local_datafolder"]}:/data'],
      environment={'OUT_FILEPATH': f'/data/{v["out_filename"]}', 'DEBUG': 0},
      dag=dag
    )
  )


def merge_mongo_push():
  import pandas as pd
  from airflow.providers.mongo.hooks.mongo import MongoHook

  # merge all datasets based on scrapers definition
  df = pd.DataFrame()
  for sname,pars in default_args['scrapers'].items():
    df = df.append(pd.read_csv(f'{default_args["local_datafolder"]}/{pars["out_filename"]}'))

  df['date_updated'] = pd.to_datetime('today').normalize()
  df.rename(columns={'link': '_id'}, inplace=True)  # use 'link' as unique id
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

  # truncate 'current' collection
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

push_mongo_task = PythonOperator(
  task_id='merge_mongo_push',
  python_callable=merge_mongo_push,
  dag=dag
)

scraper_tasks >> push_mongo_task
