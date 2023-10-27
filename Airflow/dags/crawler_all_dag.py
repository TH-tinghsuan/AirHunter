from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from modules.crawler import scrape_and_upload_s3, get_lifeTour_raw_data, get_ezFly_raw_data, get_ezTravel_raw_data, get_richmond_raw_data
from modules.transfer import insert_to_main_table
from modules.price_compare import get_old_price_history_data, insert_to_price_history, compare_price_difference, send_notification, compare_price_by_date
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
    compare_price_by_date_task_id = "compare_price_by_date"
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
                                python_callable=scrape_and_upload_s3,
                                on_failure_callback=notify_on_failure,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date, "total_dates": 20, "fun_name":get_lifeTour_raw_data, "agent_name": "lifeTour"})
    
    lifeTour_crawl_task_2 = PythonOperator(task_id=TaskID.lf_crawler_task_2_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=20), "total_dates": 20, "fun_name":get_lifeTour_raw_data, "agent_name": "lifeTour"})
    
    lifeTour_crawl_task_3 = PythonOperator(task_id=TaskID.lf_crawler_task_3_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=40), "total_dates": 21, "fun_name":get_lifeTour_raw_data, "agent_name": "lifeTour"})
    
    richmond_crawl_task_1 = PythonOperator(task_id=TaskID.rh_crawler_task_1_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 20, "fun_name":get_richmond_raw_data, "agent_name": "richmond"})
    
    richmond_crawl_task_2 = PythonOperator(task_id=TaskID.rh_crawler_task_2_id,
                                python_callable=scrape_and_upload_s3,
                                on_failure_callback=notify_on_failure,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date + timedelta(days=20), "total_dates": 20, "fun_name":get_richmond_raw_data, "agent_name": "richmond"})
    
    richmond_crawl_task_3 = PythonOperator(task_id=TaskID.rh_crawler_task_3_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=40), "total_dates": 21, "fun_name":get_richmond_raw_data, "agent_name": "richmond"})
    
    ezTravel_crawl_task_1 = PythonOperator(task_id=TaskID.ezT_crawler_task_1_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 60, "fun_name":get_ezTravel_raw_data, "agent_name": "ezTravel"})
   
    ezFly_crawl_task_1 = PythonOperator(task_id=TaskID.ezF_crawler_task_1_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date, "total_dates": 20, "fun_name":get_ezFly_raw_data, "agent_name": "ezFly"})
    
    ezFly_crawl_task_2 = PythonOperator(task_id=TaskID.ezF_crawler_task_2_id,
                                python_callable=scrape_and_upload_s3,
                                on_failure_callback=notify_on_failure,
                                provide_context=True, 
                                op_kwargs = {"start_date": current_date + timedelta(days=20), "total_dates": 20, "fun_name":get_ezFly_raw_data, "agent_name": "ezFly"})
    
    ezFly_crawl_task_3 = PythonOperator(task_id=TaskID.ezF_crawler_task_3_id,
                                python_callable=scrape_and_upload_s3, 
                                on_failure_callback=notify_on_failure,
                                provide_context=True,
                                op_kwargs = {"start_date": current_date + timedelta(days=40), "total_dates": 21, "fun_name":get_ezFly_raw_data, "agent_name": "ezFly"})

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

    end_task = EmptyOperator(task_id=TaskID.end_task_id)

    start_task >> get_search_date_task >> end_task

    start_task >> get_search_date_task >> [lifeTour_crawl_task_1, lifeTour_crawl_task_2, lifeTour_crawl_task_3,
                   richmond_crawl_task_1, richmond_crawl_task_2, richmond_crawl_task_3,
                   ezTravel_crawl_task_1, 
                   ezFly_crawl_task_1, ezFly_crawl_task_2, ezFly_crawl_task_3] >> insert_to_main_table_task >> get_old_price_history_task >> insert_to_price_history_task >> compare_price_diff_task >>  compare_price_by_date_task >> send_price_notification_task>> end_task
    
create_dag = crawler_dag_all_test()

