from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from modules.price_compare import get_old_price_history_data, insert_to_price_history, compare_price_difference, send_notification, compare_price_by_date
from modules.notification import notify_on_failure, notify_on_success


class TaskID:
    get_old_price_history_task_id = "get_old_price_history"
    insert_to_price_history_task_id = "insert_to_price_history"
    compare_price_diff_task_id = "compare_price_difference"
    compare_price_by_date_task_id = "compare_price_by_date"
    send_price_notification_task_id = "send_price_notification" 

@dag(start_date=datetime(2023, 10, 1), catchup=False, schedule_interval=None, tags=['data_pipeline_v0'])
def price_check_dag():
    get_old_price_history_task = PythonOperator(task_id=TaskID.get_old_price_history_task_id,
                                python_callable=get_old_price_history_data,
                                provide_context=True,
                                on_failure_callback=notify_on_failure,
                                retries=3,
                                retry_delay=timedelta(minutes=1))

    insert_to_price_history_task = PythonOperator(task_id=TaskID.insert_to_price_history_task_id,
                                python_callable=insert_to_price_history,
                                provide_context=True,
                                on_failure_callback=notify_on_failure,
                                retries=3,
                                retry_delay=timedelta(minutes=1))

    compare_price_diff_task = PythonOperator(task_id=TaskID.compare_price_diff_task_id,
                                python_callable=compare_price_difference,
                                provide_context=True,
                                on_failure_callback=notify_on_failure,
                                retries=3,
                                retry_delay=timedelta(minutes=1))
    
    compare_price_by_date_task = PythonOperator(task_id=TaskID.compare_price_by_date_task_id,
                                python_callable=compare_price_by_date,
                                provide_context=True,
                                on_failure_callback=notify_on_failure,
                                retries=3,
                                retry_delay=timedelta(minutes=1))

    send_price_notification_task = PythonOperator(task_id=TaskID.send_price_notification_task_id,
                                python_callable=send_notification,
                                provide_context=True,
                                on_failure_callback=notify_on_failure,
                                on_success_callback=notify_on_success,
                                retries=3,
                                retry_delay=timedelta(minutes=1))

    get_old_price_history_task >> insert_to_price_history_task >> compare_price_diff_task >>  compare_price_by_date_task >> send_price_notification_task

create_dag = price_check_dag()
