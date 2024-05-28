import utils
import os

logger = utils.logger
SPARK_VOLUME_PATH = os.getenv("SPARK_VOLUME_PATH")

def load(df):
    """Streams data using Spark Structured Streaming."""
    try:

        df.write \
        .format("org.apache.spark.sql.cassandra") \
        .options( keyspace="transportation", table="bike_points") \
        .option("checkpointLocation", SPARK_VOLUME_PATH) \
        .mode("append") \
        .save()
        
        logger.info("Batch has been successfully written to Cassandra.")
        
    except Exception as e:
        logger.error(f"Error in writing the batch to Cassandra: {e}")
