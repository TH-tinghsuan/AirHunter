from datetime import datetime, timedelta, timezone

from airflow.decorators import dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.models import Variable
from airflow.models import DagRun
from airflow import settings
from airflow import models

   
def get_utc_8_date(**kwargs):
    utc_date = datetime.utcnow()
    utc_8_date = utc_date + timedelta(hours=8)
    formatted_date = utc_8_date.strftime('%Y-%m-%d')
    Variable.set("search_date_key", formatted_date)

def get_execution_date(dt, **kwargs):
    session = settings.Session()
    dr = session.query(DagRun)\
        .filter(DagRun.dag_id == kwargs['task'].external_dag_id)\
        .order_by(DagRun.execution_date.desc())\
        .first()
    return dr.execution_date

dag_ids = ["ezFly_pipeline", "ezTravel_pipeline", "lifeTour_pipeline", "richmond_pipeline"]

@dag(start_date=datetime(2023, 10, 1), catchup=False, schedule_interval=timedelta(hours=24), tags=['data_pipeline_v0'])
def main_dag():

    set_search_date_task = PythonOperator(task_id="set_search_date_task",
                                python_callable=get_utc_8_date, 
                                provide_context=True)

    trigger_ETL_tasks = []
    ETL_tasks_sensors = []
    for dag_id in dag_ids:
        # trigger ETL tasks
        ETL_task = TriggerDagRunOperator(
            task_id=f"{dag_id}_task",
            trigger_dag_id=dag_id)
        trigger_ETL_tasks.append(ETL_task)
        # ETL tasks sensor
        wait_sensor_task = ExternalTaskSensor(
            task_id=f'wait_sensor_{dag_id}',
            external_dag_id=dag_id,
            poke_interval=timedelta(minutes=30),
            timeout=timedelta(hours=4),
            mode='reschedule',
            allowed_states=['success', 'failed'],
            execution_date_fn=get_execution_date)
        ETL_tasks_sensors.append(wait_sensor_task)

    bridge = EmptyOperator(task_id="empty_task")
    
    trigger_price_check_task = TriggerDagRunOperator(
                            task_id="price_check_task",
                            trigger_dag_id="price_check_dag")

    set_search_date_task >> trigger_ETL_tasks  # 將設置日期任務與觸發任務相連
    trigger_ETL_tasks >> bridge  # 將觸發任務與第一個感應器任務相連
    bridge >> ETL_tasks_sensors
    ETL_tasks_sensors >> trigger_price_check_task 

create_dag = main_dag()
