from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
from datetime import datetime, timedelta
from modules.crawler import lifetour_scraper, richmond_crawler, ezTravel_crawler, ezFly_crawler
from modules.transfer import insert_to_main_table, get_old_price_history_data, insert_to_price_history, compare_price_difference, send_notification
from modules.notification import send_noti_email

class TaskID:
    start_task_id = "start_task"
    end_task_id = "end_task"
    get_search_date_task_id = "get_search_date_task"
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
    insert_to_main_table_task_id = "insert_to_main_table"
    get_old_price_history_task_id = "get_old_price_history"
    insert_to_price_history_task_id = "insert_to_price_history"
    compare_price_diff_task_id = "compare_price_difference"
    send_price_notification_task_id = "send_price_notification"

def get_utc_8_date(**kwargs):
    utc_date = datetime.utcnow()
    utc_8_date = utc_date + timedelta(hours=8)
    formatted_date = utc_8_date.strftime('%Y-%m-%d')
    Variable.set("search_date_key", formatted_date)

def notify_on_failure(context):
    ti = context['ti']
    task_id = ti.task_id
    dag_id = ti.dag_id
    execution_date = ti.execution_date
    email_content = f"""Hi, 
                        Task ID {task_id} has error. Please check.
                        executed date: {execution_date}
                        dag ID: {dag_id}
                        Thank You."""
    email_subject = f"Airflow notification-task_id: {task_id} error occur."
    send_noti_email(email_subject, email_content, "tinghsuan1998@gmail.com")

def notify_on_success(context):
    ti = context['ti']
    task_id = ti.task_id
    dag_id = ti.dag_id
    execution_date = ti.execution_date
    email_content = f"""Hi, 
                        Task ID {task_id} has successfully executed.
                        executed date: {execution_date}
                        dag ID: {dag_id}
                        Thank You."""
    email_subject = f"Airflow notification-task_id: {task_id} job done."
    send_noti_email(email_subject, email_content, "tinghsuan1998@gmail.com")
    

utc_date = datetime.utcnow()
utc_8_date = utc_date + timedelta(hours=8)
current_date = utc_8_date.date() + timedelta(days=1)
    
@dag(start_date=datetime(2023, 10, 1), catchup=False, schedule_interval=timedelta(hours=8), tags=['data_pipeline'])
def crawler_dag_all_test():
    start_task = EmptyOperator(task_id=TaskID.start_task_id)

    get_search_date_task = PythonOperator(task_id=TaskID.get_search_date_task_id,
                                python_callable=get_utc_8_date, 
                                provide_context=True)
    
    lifeTour_crawl_task_1 = PythonOperator(task_id=TaskID.lf_crawler_task_1_id,
                                python_callable=lifetour_scraper,
                                on_failure_callback=notify_on_failure,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date, "total_dates": 20})
    
    lifeTour_crawl_task_2 = PythonOperator(task_id=TaskID.lf_crawler_task_2_id,
                                python_callable=lifetour_scraper, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=20), "total_dates": 20})
    
    lifeTour_crawl_task_3 = PythonOperator(task_id=TaskID.lf_crawler_task_3_id,
                                python_callable=lifetour_scraper, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=40), "total_dates": 21})
    
    richmond_crawl_task_1 = PythonOperator(task_id=TaskID.rh_crawler_task_1_id,
                                python_callable=richmond_crawler, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 20})
    
    richmond_crawl_task_2 = PythonOperator(task_id=TaskID.rh_crawler_task_2_id,
                                python_callable=richmond_crawler,
                                on_failure_callback=notify_on_failure,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date + timedelta(days=20), "total_dates": 20})
    
    richmond_crawl_task_3 = PythonOperator(task_id=TaskID.rh_crawler_task_3_id,
                                python_callable=richmond_crawler, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=40), "total_dates": 21})
    
    ezTravel_crawl_task_1 = PythonOperator(task_id=TaskID.ezT_crawler_task_1_id,
                                python_callable=ezTravel_crawler, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 60})
   
    ezFly_crawl_task_1 = PythonOperator(task_id=TaskID.ezF_crawler_task_1_id,
                                python_callable=ezFly_crawler, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 20})
    
    ezFly_crawl_task_2 = PythonOperator(task_id=TaskID.ezF_crawler_task_2_id,
                                python_callable=ezFly_crawler,
                                on_failure_callback=notify_on_failure,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date + timedelta(days=20), "total_dates": 20})
    
    ezFly_crawl_task_3 = PythonOperator(task_id=TaskID.ezF_crawler_task_3_id,
                                python_callable=ezFly_crawler, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=40), "total_dates": 21})

    insert_to_main_table_task = PythonOperator(task_id=TaskID.insert_to_main_table_task_id,
                                python_callable=insert_to_main_table,
                                on_failure_callback=notify_on_failure,
                                retries=3,
                                retry_delay=timedelta(minutes=1))

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

    send_price_notification_task = PythonOperator(task_id=TaskID.send_price_notification_task_id,
                                python_callable=send_notification,
                                provide_context=True,
                                on_failure_callback=notify_on_failure,
                                on_success_callback=notify_on_success,
                                retries=3,
                                retry_delay=timedelta(minutes=1))

    end_task = EmptyOperator(task_id=TaskID.end_task_id)

    start_task >> get_search_date_task >> [lifeTour_crawl_task_1, lifeTour_crawl_task_2, lifeTour_crawl_task_3,
                   richmond_crawl_task_1, richmond_crawl_task_2, richmond_crawl_task_3,
                   ezTravel_crawl_task_1, 
                   ezFly_crawl_task_1, ezFly_crawl_task_2, ezFly_crawl_task_3] >> insert_to_main_table_task >> get_old_price_history_task >> insert_to_price_history_task >> compare_price_diff_task >>  send_price_notification_task>> end_task
    
create_dag = crawler_dag_all_test()
