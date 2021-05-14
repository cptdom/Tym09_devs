from airflow.utils.dates import days_ago
from airflow.decorators import dag, task

from utils.send_email import send_email_recommendations
from utils.predictions import run_apart_predictions
from utils.preprocess import prepare_data

# TODO import default args from util to make them global across all dags
default_args = {
  'owner': 'airflow',
  'mongo_master_collection': 'masterdata',
  'mongo_current_collection': 'currentdata',
  'mongo_extrafeatures_collection': 'extrafeatures',
  'mongo_trackers_collection': 'trackers',
  'mongo_dbname': 'reality',
  'mongo_trackers_dbname': 'user_requests'
}

@dag(default_args=default_args, schedule_interval=None, start_date=days_ago(2), tags=['model', 'mongo', 'prediction'])
def run_predictions():
  @task()
  def prepare_model_data(default_args):
    return prepare_data(default_args)

  @task()
  def predict(data, default_args):
    return run_apart_predictions(data, default_args)

  @task()
  def send_emails(recc):
    send_email_recommendations(recc)

  data = prepare_model_data(default_args)
  recc = predict(data, default_args)
  send_emails(recc)

run_predictions_taskflow = run_predictions()
