FROM apache/airflow:2.6.0-python3.9 

COPY entrypoint.sh /opt/airflow/script/entrypoint.sh

USER root
RUN chmod +x /opt/airflow/script/entrypoint.sh

USER airflow

ENTRYPOINT ["/opt/airflow/script/entrypoint.sh"]