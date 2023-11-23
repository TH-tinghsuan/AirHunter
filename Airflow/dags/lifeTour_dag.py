from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from modules.crawler import get_lifeTour_raw_data, scrape_and_upload_s3
from modules.transfer import clean_data_lifetour
from modules.notification import notify_on_failure


class TaskID:
    lifeTour_crawler_task_1_id = "crawler_task_1"
    lifeTour_crawler_task_2_id = "crawler_task_2"
    lifeTour_crawler_task_3_id = "crawler_task_3"
    lifeTour_clean_task_id = "clean_and_load_task"

SEARCH_DATE = Variable.get("search_date_key")
date_obj = datetime.strptime(SEARCH_DATE, '%Y-%m-%d')
current_date = date_obj.date() + timedelta(days=1)

@dag(start_date=datetime(2023, 10, 1), catchup=False, schedule_interval=None, tags=['data_pipeline_v0'])
def lifeTour_pipeline():
    crawl_task_1 = PythonOperator(task_id=TaskID.lifeTour_crawler_task_1_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 20, "fun_name":get_lifeTour_raw_data, "agent_name": "lifeTour"})
    
    crawl_task_2 = PythonOperator(task_id=TaskID.lifeTour_crawler_task_2_id,
                                python_callable=scrape_and_upload_s3,
                                on_failure_callback=notify_on_failure,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date + timedelta(days=20), "total_dates": 20, "fun_name":get_lifeTour_raw_data, "agent_name": "lifeTour"})
    
    crawl_task_3 = PythonOperator(task_id=TaskID.lifeTour_crawler_task_3_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=40), "total_dates": 21, "fun_name":get_lifeTour_raw_data, "agent_name": "lifeTour"})
    
    clean_and_load_task = PythonOperator(task_id=TaskID.lifeTour_clean_task_id,
                                python_callable=clean_data_lifetour, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True)

    [crawl_task_1,  crawl_task_2,  crawl_task_3] >> clean_and_load_task

create_dag = lifeTour_pipeline()
