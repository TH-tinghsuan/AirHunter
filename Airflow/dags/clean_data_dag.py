from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.amazon.aws.hooks.sqs import SqsHook
from airflow.models import XCom
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import os
from modules.transfer import (
    clean_data_lifetour, 
    clean_data_richmond, 
    clean_data_ezFly, 
    clean_data_ezTravel)

load_dotenv()

AWS_CONN_ID = os.getenv("AWS_CONN_ID")
queueUrl = os.getenv("QUEUE_URL")

class TaskID:
    start_task_id = "start_task"
    end_task_id = "end_task"
    get_sqs_id = "get_sqs_message"
    clean_to_db_id = "clean_and_insert_to_rds"

def get_sqs_message(**kwargs):
    conn = SqsHook(aws_conn_id=AWS_CONN_ID, region_name="ap-southeast-2")
    sqs_hook_client = conn.get_conn()
    response = sqs_hook_client.receive_message(
                            QueueUrl=queueUrl,
                            MaxNumberOfMessages=10,
                            WaitTimeSeconds=10)
    
    filename_list = []
    for message in response.get("Messages", []):
        message_body = message["Body"]
        json_data = json.loads(message_body)
        filename_list.append(json_data['Records'][0]['s3']['object']['key'])
        print(filename_list)    
        del_response=sqs_hook_client.delete_message(
                                QueueUrl=queueUrl,
                                ReceiptHandle=message['ReceiptHandle']
                    )
        print(del_response['ResponseMetadata']['HTTPStatusCode'])
        ti = kwargs['ti']
        ti.xcom_push(key='filename_list_key', value=filename_list)

def clean_and_insert_to_rds(**kwargs):
    ti = kwargs['ti']
    filename_list = ti.xcom_pull(key='filename_list_key')
    print(filename_list)
    if filename_list:
        for fn in filename_list:
            ag_name = fn.split("_")[2]
            if ag_name == "lifeTour":
                clean_data_lifetour(fn)
            elif ag_name == "richmond":
                clean_data_richmond(fn)
            elif ag_name == "ezTravel":
                clean_data_ezTravel(fn)
            elif ag_name == "ezFly":
                clean_data_ezFly(fn)
    else:
        print("No data to inset to RDS.")

@dag(start_date=datetime.today(), schedule_interval=timedelta(seconds=10), tags=['data_pipeline'])
def clean_dag():
    start_task = EmptyOperator(task_id=TaskID.start_task_id)

    get_sqs_task = PythonOperator(task_id=TaskID.get_sqs_id,
                                python_callable=get_sqs_message, 
                                provide_context=True)
    
    clean_to_db_task = PythonOperator(task_id=TaskID.clean_to_db_id,
                                python_callable=clean_and_insert_to_rds,
                                provide_context=True)

    end_task = EmptyOperator(task_id=TaskID.end_task_id)

    start_task >> get_sqs_task >> clean_to_db_task >> end_task

my_dag = clean_dag()
