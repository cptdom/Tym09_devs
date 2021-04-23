from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago

DAG_NAME = 'scrape_reality'

default_args = {
  'owner': 'airflow',
  'local_datafolder': '/tmp',
  'scrapers': {
    'prazskereality': {
      'script': 'prazskereality_scrape.py',
      'out_filename': 'bezrealitky_prague.csv'
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
      environment={'OUT_FILEPATH': f'/data/{v["out_filename"]}'},
      dag=dag
    )
  )


def merge_mongo_push():
  import pandas as pd
  from airflow.providers.mongo.hooks.mongo import MongoHook

  # todo merge all datasets based on scrapers definition
  a_df = pd.read_csv(f'{default_args["local_datafolder"]}/{default_args["scrapers"]["prazskereality"]["out_filename"]}')
  a_df.rename(columns={'link': '_id'}, inplace=True)  # use 'link' as unique id

  mongo = MongoHook(conn_id='mongo_reality')
  mongo.insert_many(mongo_collection='masterdata', docs=a_df.to_dict('records'), mongo_db='reality')


push_mongo_task = PythonOperator(
  task_id='merge_mongo_push',
  python_callable=merge_mongo_push,
  dag=dag
)

scraper_tasks >> push_mongo_task
