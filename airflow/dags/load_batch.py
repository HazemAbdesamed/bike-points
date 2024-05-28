# In your Airflow DAG file
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from datetime import datetime, timedelta

command = """
source /tmp/set_env_vars.sh &&

cd /opt/bitnami/spark/data_processing &&

/opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 batch_main.py

"""

default_args = {
'owner': 'hazem',
'start_date': datetime(2024, 1, 1)
}

dag = DAG(
'load_batch',
default_args=default_args,
schedule='@daily',
catchup=False,
)

load_batch_task = SSHOperator(
task_id='load_batch_task',
ssh_conn_id='ssh_spark_conn',
command=command,
dag=dag,
cmd_timeout=None,
)

load_batch_task