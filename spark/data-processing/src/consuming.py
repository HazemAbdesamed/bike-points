from src.utils import logger

def consume(spark_session):
    """Reads data from kafka and create a datafarame"""
    try:
        df = spark_session.readStream\
                .format("kafka")\
                .option("kafka.bootstrap.servers", "kafka1:9092")\
                .option("subscribe", "bike-points")\
                .option("startingOffsets", "earliest") \
                .load()
        logger.info("Data consumed from kafka successfully")
        return df
    
    except Exception as e:
        logger.error(f"Error in consumption from kafka : {e}")