FROM apache/airflow:2.6.0-python3.9

ARG SPARK_SYSTEM_PASSWORD

USER root

RUN echo 'airflow ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/spark

COPY config/ssh_config /home/airflow/.ssh/config

USER airflow

RUN sudo apt-get update && \
sudo apt-get install -y sshpass

COPY requirements.txt /opt/airflow/requirements.txt
RUN  pip install -r /opt/airflow/requirements.txt