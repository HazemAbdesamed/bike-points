import os
import json
from kafka import KafkaProducer
from ..utils import logger
from .realtime_metrics import *


TOPIC_METRICS = os.environ.get("TOPIC_METRICS")
BROKER1=os.environ.get("BROKER1")
PORT1=os.environ.get("PORT1")


producer = KafkaProducer(bootstrap_servers=[f'{BROKER1}:{PORT1}'])

def load_stream(df, batch_id):
    try:
        metrics = {
            "nb_available_bikes": nb_available_bikes(df),
            "percentage_available_bikes": percentage_available_bikes(df),
            "nb_InUse_bikes": nb_InUse_bikes(df),
            "percentage_InUse_bikes": percentage_InUse_bikes(df),
            "nb_broken_docks": nb_broken_docks(df),
            "percentage_broken_docks": percentage_broken_docks(df)
        }

        # producer.send(topic=TOPIC_METRICS, value=json.dumps(metrics).encode('utf-8'))
        # producer.close()
        print("Calculated Metrics:")
        for metric, value in metrics.items():
            print(f"metric :  {metric}: {value}")
    except Exception as e:
        print(f"Error in calculating metrics: {e}")

def streaming(df, spark_session):
    """Write the stream data from spark to kafka"""
    try:

        df.writeStream \
        .foreachBatch(load_stream) \
        .start() \
        .awaitTermination()

        logger.info("Streaming query has terminated successfully.")
        
    except Exception as e:
        logger.error(f"Error in writing the spark stream to the console : {e}")