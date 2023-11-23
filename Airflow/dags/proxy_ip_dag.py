from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

import ssl
import requests
from datetime import datetime, timedelta
import json

from modules.crawler import set_proxy_ip_list

class TaskID:
    start_task_id = "set_proxy_ip_task"
    end_task_id ="end_task"


@dag(start_date=datetime(2023, 10, 1), catchup=False, schedule_interval=timedelta(hours=1))
def proxy_ip_dag():
    start_task = PythonOperator(task_id=TaskID.start_task_id,
                                python_callable=set_proxy_ip_list)
    endt_task= EmptyOperator(task_id=TaskID.end_task_id)

    
    start_task >> endt_task

my_dag = proxy_ip_dag()

