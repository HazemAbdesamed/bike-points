# In your Airflow DAG file
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta



default_args = {
'owner': 'hazem',
'start_date': datetime(2024, 5, 31),
}

def process_and_produce_to_kafka():
    import produce_to_kafka.main
    return produce_to_kafka.main


dag = DAG(
    dag_id="stage",
    default_args=default_args,
    catchup=False,
    schedule_interval=timedelta(minutes=3),  # Run every 3 minutes
) 


stage_task = BashOperator(
    dag=dag,
    task_id="stage_task",
    bash_command='python /opt/airflow/produce_to_kafka/main.py',
)