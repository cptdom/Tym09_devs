from airflow.utils.dates import days_ago
from airflow.decorators import dag, task

from utils.send_email import send_email_recommendations
from utils.predictions import run_apart_predictions
from utils.preprocess import prepare_data
from utils.vars import DEFAULT_ARGS

@dag(default_args=DEFAULT_ARGS, schedule_interval=None, start_date=days_ago(2), tags=['model', 'mongo', 'prediction'])
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

  data = prepare_model_data(DEFAULT_ARGS)
  recc = predict(data, DEFAULT_ARGS)
  send_emails(recc)

run_predictions_taskflow = run_predictions()
