import os
from kafka import KafkaProducer
from src.utils import logger


TOPIC_METRICS = os.environ.get("TOPIC_METRICS")
BROKER1 = os.environ.get("BROKER1")
PORT1 = os.environ.get("PORT1")
SPARK_VOLUME_PATH = os.environ.get("SPARK_VOLUME_PATH")


producer = KafkaProducer(bootstrap_servers= [f'{BROKER1}:{PORT1}'])

def streaming(df):
    """Streams data using Spark Structured Streaming."""
    try:

        logger.info("Streaming has started...")
        # Write metrics to Kafka
        df.writeStream \
            .format('kafka') \
            .option("kafka.bootstrap.servers", f"{BROKER1}:{PORT1}") \
            .option("topic", TOPIC_METRICS) \
            .option('checkpointLocation', SPARK_VOLUME_PATH) \
            .outputMode('update') \
            .start() \
            .awaitTermination()
        
        logger.info("Streaming query has terminated successfully.")
        
    except Exception as e:
        logger.error(f"Error in processing the Spark stream: {e}")
