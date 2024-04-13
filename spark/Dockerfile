FROM bitnami/spark:3.5.0

COPY ./requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt