from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from modules.crawler import get_ezTravel_raw_data, scrape_and_upload_s3
from modules.transfer import clean_data_ezTravel
from modules.notification import notify_on_failure


class TaskID:
    ezT_crawler_task_id = "crawler_task"
    ezT_clean_task_id = "clean_and_load_task"

SEARCH_DATE = Variable.get("search_date_key")
date_obj = datetime.strptime(SEARCH_DATE, '%Y-%m-%d')
current_date = date_obj.date() + timedelta(days=1)

@dag(start_date=datetime(2023, 10, 1), catchup=False, schedule_interval=None, tags=['data_pipeline_v0'])
def ezTravel_pipeline():
    crawl_task = PythonOperator(task_id=TaskID.ezT_crawler_task_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 61, "fun_name":get_ezTravel_raw_data, "agent_name": "ezTravel"})
    
    clean_and_load_task = PythonOperator(task_id=TaskID.ezT_clean_task_id,
                                python_callable=clean_data_ezTravel, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True)

    crawl_task >> clean_and_load_task

create_dag = ezTravel_pipeline()
