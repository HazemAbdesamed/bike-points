from utils import get_postgres_jdbc_url, get_postgres_properties, logger

def load(df):
    """Streams data using Spark Structured Streaming."""
    try:

        jdbc_url = get_postgres_jdbc_url()
        jdbc_properties = get_postgres_properties() # user, password, driver
        
        TABLE_NAME = 'stg_bike_points'

        df.write \
         .format("jdbc") \
         .option("url", jdbc_url) \
         .option("dbtable", TABLE_NAME) \
         .options(**jdbc_properties) \
         .mode("overwrite") \
         .save()
        
        logger.info("Batch has been successfully written to the historical table.")
        
    except Exception as e:
        logger.error(f"Error in writing the batch to the historical table: {e}")
