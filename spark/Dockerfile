FROM bitnami/spark:3.5.0

ARG SPARK_SYSTEM_PASSWORD

USER root

# Install dependencies
RUN apt-get update && \
    apt-get install -y openssh-server sudo

RUN adduser --uid 1001 --home /home/spark --shell /bin/bash --ingroup sudo spark && \
    echo "spark:${SPARK_SYSTEM_PASSWORD}" | chpasswd

COPY ./config/spark_ssh.conf /etc/ssh/sshd_config.d/spark_ssh.conf

RUN echo 'spark ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/spark

USER spark
ENV HOME /home/spark

COPY requirements.txt /opt/bitnami/spark/requirements.txt

RUN pip install --user -r /opt/bitnami/spark/requirements.txt
