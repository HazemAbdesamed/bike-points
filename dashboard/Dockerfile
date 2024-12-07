FROM apache/superset:4.0.2

USER root

RUN pip install trino

ENV ADMIN_USERNAME admin
ENV ADMIN_EMAIL admin@email.com
ENV ADMIN_PASSWORD admin

COPY ./config/superset_init.sh /app/superset_init.sh


COPY ./config/superset_config.py /app/
ENV SUPERSET_CONFIG_PATH /app/superset_config.py

USER superset
ENTRYPOINT [ "/app/superset_init.sh" ]