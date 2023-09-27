from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
from datetime import datetime, timedelta
from modules.crawler import lifetour_scraper, richmond_crawler, ezTravel_crawler, ezFly_crawler
from modules.transfer import gernerate_batch_version

class TaskID:
    start_task_id = "start_task"
    end_task_id = "end_task"
    batch_version_id = "batch_version_task"
    lf_crawler_task_1_id = "lifeTour_crawler_task_1"
    lf_crawler_task_2_id = "lifeTour_crawler_task_2"
    lf_crawler_task_3_id = "lifeTour_crawler_task_3"
    rh_crawler_task_1_id = "richmond_crawler_task_1"
    rh_crawler_task_2_id = "richmond_crawler_task_2"
    rh_crawler_task_3_id = "richmond_crawler_task_3"
    ezT_crawler_task_1_id = "ezTravel_crawler_task_1"
    ezF_crawler_task_1_id = "ezFly_crawler_task_1"
    ezF_crawler_task_2_id = "ezFly_crawler_task_2"
    ezF_crawler_task_3_id = "ezFly_crawler_task_3"



def generate_version(**kwargs):
    batch_version = gernerate_batch_version("domestic")
    Variable.set("batch_version_key", batch_version)
    

current_date = datetime(2023, 11, 1).date()
    
@dag(start_date=datetime.today(), schedule_interval=timedelta(minutes=20), tags=['data_pipeline'])
def crawler_dag():
    start_task = EmptyOperator(task_id=TaskID.start_task_id)

    batch_version = PythonOperator(task_id=TaskID.batch_version_id,
                                python_callable=generate_version, 
                                provide_context=True)

    lifeTour_crawl_task_1 = PythonOperator(task_id=TaskID.lf_crawler_task_1_id,
                                python_callable=lifetour_scraper,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date, "total_dates": 10})
    
    lifeTour_crawl_task_2 = PythonOperator(task_id=TaskID.lf_crawler_task_2_id,
                                python_callable=lifetour_scraper, 
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=9), "total_dates": 10})
    
    lifeTour_crawl_task_3 = PythonOperator(task_id=TaskID.lf_crawler_task_3_id,
                                python_callable=lifetour_scraper, 
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=18), "total_dates": 10})
    
    richmond_crawl_task_1 = PythonOperator(task_id=TaskID.rh_crawler_task_1_id,
                                python_callable=richmond_crawler, 
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 20})
    
    richmond_crawl_task_2 = PythonOperator(task_id=TaskID.rh_crawler_task_2_id,
                                python_callable=richmond_crawler,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date + timedelta(days=19), "total_dates": 20})
    
    richmond_crawl_task_3 = PythonOperator(task_id=TaskID.rh_crawler_task_3_id,
                                python_callable=richmond_crawler, 
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=38), "total_dates": 20})
    
    ezTravel_crawl_task_1 = PythonOperator(task_id=TaskID.ezT_crawler_task_1_id,
                                python_callable=ezTravel_crawler, 
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 60})
   
    ezFly_crawl_task_1 = PythonOperator(task_id=TaskID.ezF_crawler_task_1_id,
                                python_callable=ezFly_crawler, 
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 20})
    
    ezFly_crawl_task_2 = PythonOperator(task_id=TaskID.ezF_crawler_task_2_id,
                                python_callable=ezFly_crawler,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date + timedelta(days=19), "total_dates": 20})
    
    ezFly_crawl_task_3 = PythonOperator(task_id=TaskID.ezF_crawler_task_3_id,
                                python_callable=ezFly_crawler, 
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=38), "total_dates": 20})
    
    end_task = EmptyOperator(task_id=TaskID.end_task_id)

    start_task >> batch_version >> [lifeTour_crawl_task_1, lifeTour_crawl_task_2, lifeTour_crawl_task_3,
                   richmond_crawl_task_1, richmond_crawl_task_2, richmond_crawl_task_3,
                   ezTravel_crawl_task_1, ezFly_crawl_task_1, ezFly_crawl_task_2, ezFly_crawl_task_3] >> end_task
    
create_dag = crawler_dag()
