import os
from utils import logger
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, TimestampType
from pyspark.sql.functions import from_json, col

BROKER1 = os.environ.get("BROKER1")
PORT1 = os.environ.get("PORT1")
TOPIC_METRICS = os.environ.get("TOPIC_METRICS")

def calculate_metrics_sql(df):
    """
    Calculates metrics using Spark SQL
    Returns a df contining the metrics in each column
    """
    
    df.createOrReplaceTempView("bike_points")

    # select the latest values within the batch and then perform the aggregations
    sql_query = """
        WITH latest_bikepoints AS ( 
            SELECT 
                ID,
                MAX_BY(NbBikes, ExtractionDatetime) AS latest_NbBikes,
                MAX_BY(NbEBikes, ExtractionDatetime) AS latest_NbEBikes,
                MAX_BY(NbDocks, ExtractionDatetime) AS latest_NbDocks,
                MAX_BY(NbEmptyDocks, ExtractionDatetime) AS latest_NbEmptyDocks,
                MAX_BY(NbBrokenDocks, ExtractionDatetime) AS latest_NbBrokenDocks,
                MAX(ExtractionDatetime) AS ExtractionDatetime
            FROM bike_points
            GROUP BY ID
        )
        SELECT 
            MIN(ExtractionDatetime) AS min_extraction_datetime,
            MAX(ExtractionDatetime) AS max_extraction_datetime,
            SUM(latest_NbBikes) AS nb_available_bikes,
            CAST(ROUND(100 * SUM(latest_NbBikes) / SUM(latest_NbDocks), 2) AS STRING) AS percentage_available_bikes,
            SUM(latest_NbEBikes) AS nb_available_Ebikes,
            CAST(ROUND(100 * SUM(latest_NbEBikes) / SUM(latest_NbDocks), 2) AS STRING) AS percentage_available_Ebikes,
            SUM(latest_NbEmptyDocks) AS nb_in_use_bikes,
            CAST(ROUND(100 * SUM(latest_NbEmptyDocks) / SUM(latest_NbDocks), 2) AS STRING) AS percentage_in_use_bikes,
            SUM(latest_NbBrokenDocks) AS nb_broken_docks,
            CAST(ROUND(100 * SUM(latest_NbBrokenDocks) / SUM(latest_NbDocks), 2) AS STRING) AS percentage_broken_docks
        FROM latest_bikepoints
    """
    
    metrics_df = df.sparkSession.sql(sql_query)

    return metrics_df


def process(df, batch_id):
    """Process data received from kafka"""

    # create the schema
    schema = StructType([
                StructField("Id", StringType()),
                StructField("CommonName", StringType()),
                StructField("Lat", StringType()),
                StructField("Lon", StringType()),
                StructField("Installed", StringType()),
                StructField("Locked", StringType()),
                StructField("NbBikes", IntegerType()),
                StructField("NbEmptyDocks", IntegerType()),
                StructField("NbDocks", IntegerType()),
                StructField("NbBrokenDocks", IntegerType()),
                StructField("NbEBikes", IntegerType()),
                StructField("ExtractionDatetime", TimestampType())
    ])

    # select the columns received from kafka
    df = df.selectExpr("CAST(value AS STRING)")\
        .select( from_json( col("value"), schema ).alias("bp") )\
        .select(
        col("bp.Id"),
        col("bp.CommonName"),
        col("bp.Lat"),
        col("bp.Lon"),
        col("bp.Installed"),
        col("bp.Locked"),
        col("bp.NbBikes").alias("NbBikes"),
        col("bp.NbEmptyDocks").alias("NbEmptyDocks"),
        col("bp.NbDocks").alias("NbDocks"),
        col("bp.NbEBikes").alias("NbEBikes"),
        (col("bp.NbDocks") - (col("bp.NbBikes") + col("bp.NbEmptyDocks")) ).alias("NbBrokenDocks"),
        col("bp.ExtractionDatetime")
    )

    df = df.withWatermark('ExtractionDatetime', '4 minutes')

    # Calculate metrics using SQL
    metrics_df = calculate_metrics_sql(df)

    # Serialize the df to write into kafka topic
    metrics_df = metrics_df.selectExpr("to_json(struct(*)) AS value")

    metrics_df.write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", f"{BROKER1}:{PORT1}") \
        .option("topic", TOPIC_METRICS) \
        .save()
    
    logger.info("A record has been inserted into the near-real-time metrics topic.")