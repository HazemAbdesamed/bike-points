import os
from kafka import KafkaProducer
from utils import logger
from speed_layer.processing import process


SPARK_VOLUME_PATH = os.environ.get("SPARK_VOLUME_PATH")
BROKER1 = os.environ.get("BROKER1")
PORT1 = os.environ.get("PORT1")
TOPIC_METRICS = os.environ.get("TOPIC_METRICS")


producer = KafkaProducer(bootstrap_servers= [f'{BROKER1}:{PORT1}'])

def write_to_kafka(df, batch_id):
    df.show(truncate=False)


def streaming(df):
    """Streams data using Spark Structured Streaming."""
    try:

        logger.info("Streaming has started...")


        # Write metrics to Kafka
        df.writeStream \
            .outputMode('complete') \
            .foreachBatch(write_to_kafka) \
            .start() \
            .awaitTermination()
        
        logger.info("Streaming query has terminated successfully.")
        
    except Exception as e:
        logger.error(f"Error in processing the Spark stream: {e}")
