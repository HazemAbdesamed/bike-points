from utils import logger
from speed_layer.processing import process

def streaming(df):
    """Streams data using Spark Structured Streaming."""
    try:

        # df = df.withWatermark('ExtractionDatetime', '4 minutes')
        
        logger.info("Streaming has started...")
        # Write metrics to Kafka
        df.writeStream \
            .trigger(processingTime='3 seconds') \
            .outputMode('update') \
            .foreachBatch(process) \
            .start() \
            .awaitTermination()
        
        logger.info("Streaming query has terminated successfully.")
        
    except Exception as e:
        logger.error(f"Error in processing the Spark stream: {e}")
