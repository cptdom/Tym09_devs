
from dags.utils.send_email import send_email_recommendations
from dags.utils.predictions import run_apart_predictions
from dags.utils.preprocess import prepare_data


default_args = {
    'owner': 'airflow',
    'mongo_master_collection': 'masterdata',
    'mongo_current_collection': 'currentdata',
    'mongo_extrafeatures_collection': 'extrafeatures',
    'mongo_trackers_collection': 'trackers',
    'mongo_dbname': 'reality',
    'mongo_trackers_dbname': 'user_requests'
}

data = prepare_data(default_args)
recc = run_apart_predictions(data, default_args)
send_email_recommendations(recc)