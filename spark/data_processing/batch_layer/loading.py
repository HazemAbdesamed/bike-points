import utils

logger = utils.logger

def load(df):
    """Streams data using Spark Structured Streaming."""
    try:

        df.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(keyspace="transportation", table="bike_points") \
        .mode("append") \
        .save()
        
        logger.info("Batch has been successfully written to the historical table.")
        
    except Exception as e:
        logger.error(f"Error in writing the batch to the historical table: {e}")
