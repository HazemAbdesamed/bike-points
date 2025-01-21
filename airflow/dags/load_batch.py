from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

import os

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")

command = """
source /tmp/set_env_vars.sh &&

cd /opt/bitnami/spark/data_processing &&

/opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0,org.postgresql:postgresql:42.7.4 batch_main.py

"""
# /opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 batch_main.py

default_args = {
'owner': 'hazem',
'start_date': datetime(2024, 1, 1)
}

dag = DAG(
'load_batch',
default_args=default_args,
schedule='@daily',
catchup=False,
template_searchpath=f"{AIRFLOW_HOME}/helpers",
)

truncate_staging_table_task = PostgresOperator(
dag=dag,
task_id='truncate_staging_table_task',
postgres_conn_id='postgres_historical_data_conn',
sql='TRUNCATE TABLE stg_bike_points;'
)

load_to_staging_table_task = SSHOperator(
dag=dag,
task_id='load_to_staging_table_task',
ssh_conn_id='ssh_spark_conn',
command=command,
cmd_timeout=None,
)

load_historical_table_task = PostgresOperator(
dag=dag,
task_id='load_historical_table_task',
postgres_conn_id='postgres_historical_data_conn',
sql='load_to_historical_data_table.sql'
)

refresh_materialized_views_task = PostgresOperator(
dag=dag,
task_id='refresh_materialized_views_task',
postgres_conn_id='postgres_historical_data_conn',
sql='mvw_refresh.sql'
)


truncate_staging_table_task >> load_to_staging_table_task >> load_historical_table_task >> refresh_materialized_views_task