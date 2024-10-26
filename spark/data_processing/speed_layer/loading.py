import os
from kafka import KafkaProducer
from utils import logger
from speed_layer.processing import process


SPARK_VOLUME_PATH = os.environ.get("SPARK_VOLUME_PATH")
BROKER1 = os.environ.get("BROKER1")
PORT1 = os.environ.get("PORT1")
TOPIC_METRICS = os.environ.get("TOPIC_METRICS")

producer = KafkaProducer(bootstrap_servers= [f'{BROKER1}:{PORT1}'])

def streaming(df):
    """Streams data using Spark Structured Streaming."""
    try:

        # df = df.withWatermark('ExtractionDatetime', '4 minutes')
        
        logger.info("Streaming has started...")
        # Write metrics to Kafka
        df.writeStream \
            .trigger(processingTime='5 seconds') \
            .outputMode('update') \
            .foreachBatch(process) \
            .start() \
            .awaitTermination()
        
        logger.info("Streaming query has terminated successfully.")
        
    except Exception as e:
        logger.error(f"Error in processing the Spark stream: {e}")
