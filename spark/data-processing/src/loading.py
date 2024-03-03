from .utils import logger

def streaming(df):
    """"Write the stream from spark to console"""
    try:
        # query = df.writeStream\
        # .format("console")\
        # .outputMode("append") \
        # .start()
        
        # logger.info("Streaming query has started.")
        # query.awaitTermination()
        df.show(2, truncate=False)
        logger.info("Streaming query has terminated successfully.")
        
    except Exception as e:
        logger.error(f"Error in writing the spark stream to the console : {e}")