import os
import json
from kafka import KafkaProducer
from ..utils import logger
from pyspark.sql.functions import col


TOPIC_METRICS = os.environ.get("TOPIC_METRICS")
BROKER1 = os.environ.get("BROKER1")
PORT1 = os.environ.get("PORT1")
SPARK_VOLUME_PATH = os.environ.get("SPARK_VOLUME_PATH")



producer = KafkaProducer(bootstrap_servers= [f'{BROKER1}:{PORT1}'])


def calculate_metrics_sql(df, spark_session):
    """
    # Calculates metrics using Spark SQL.

    # Register DataFrame as a temporary view
    df.createOrReplaceTempView("bike_points")
    
    # Define SQL query to calculate metrics
    """

    # Register DataFrame as a temporary view
    df.createOrReplaceTempView("bike_points")

    sql_query = """ 
        SELECT 
            CAST(SUM(NbBikes) AS STRING) AS nb_available_bikes,
            CAST(ROUND(100 * SUM(NbBikes) / SUM(NbDocks), 2) AS STRING) AS percentage_available_bikes,
            CAST(SUM(NbEmptyDocks) AS STRING) AS nb_in_use_bikes,
            CAST(ROUND(100 * SUM(NbEmptyDocks) / SUM(NbDocks), 2) AS STRING)  AS percentage_in_use_bikes,
            CAST(SUM(NbBrokenDocks) AS STRING) AS nb_broken_docks,
            CAST(ROUND(100 * SUM(NbBrokenDocks) / SUM(NbDocks), 2) AS STRING)  AS percentage_broken_docks
        FROM bike_points
    """
    # Execute SQL query
    metrics_df = spark_session.sql(sql_query)
    
    return metrics_df

def print_df(df, batch_id):
    print(df.select("value").first()[0])

def streaming(df, spark_session):
    """Streams data using Spark Structured Streaming."""
    try:
        # Calculate metrics using SQL
        metrics_df = calculate_metrics_sql(df, spark_session)
        
        # for col_name in metrics_df.columns:
        #     metrics_df = metrics_df.withColumn(col_name, col(col_name).cast("string"))

        # Serialize the df to write into kafka topic
        metrics_df = metrics_df.selectExpr("to_json(struct(*)) AS value") 

    
        # Write metrics to Kafka
        metrics_df.writeStream \
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
