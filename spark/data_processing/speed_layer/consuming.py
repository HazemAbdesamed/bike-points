import os
from utils import logger

TOPIC_DATA = os.environ.get("TOPIC_DATA")
BROKER1=os.environ.get("BROKER1")
PORT1=os.environ.get("PORT1")

def consume(spark_session):
    """Reads data from kafka and create a datafarame"""
    try:
        df = spark_session.readStream\
                .format("kafka")\
                .option("kafka.bootstrap.servers", f"{BROKER1}:{PORT1}")\
                .option("subscribe", TOPIC_DATA)\
                .option("startingOffsets", "latest")\
                .load()
        logger.info("Data consumed from kafka successfully")
        return df
    
    except Exception as e:
        logger.error(f"Error in consumption from kafka : {e}")