from utils import logger
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, TimestampType
from pyspark.sql.functions import from_json, col

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
                id,
                MAX_BY(NbBikes, extraction_datetime) AS latest_NbBikes,
                MAX_BY(NbEBikes, extraction_datetime) AS latest_NbEBikes,
                MAX_BY(NbDocks, extraction_datetime) AS latest_NbDocks,
                MAX_BY(NbEmptyDocks, extraction_datetime) AS latest_NbEmptyDocks,
                MAX_BY(NbBrokenDocks, extraction_datetime) AS latest_NbBrokenDocks,
                MAX(extraction_datetime) AS extraction_datetime
            FROM bike_points
            GROUP BY id
        )
        SELECT 
            COALESCE(MIN(extraction_datetime), to_date('2000-01-01')) AS min_extraction_datetime,
            COALESCE(MAX(extraction_datetime), to_date('2000-01-01')) AS max_extraction_datetime,
            SUM(latest_NbBikes) AS nb_available_bikes,
            ROUND(100 * SUM(latest_NbBikes) / SUM(latest_NbDocks), 2) AS percentage_available_bikes,
            SUM(latest_NbEBikes) AS nb_available_ebikes,
            ROUND(100 * SUM(latest_NbEBikes) / SUM(latest_NbDocks), 2) AS percentage_available_ebikes,
            SUM(latest_NbEmptyDocks) AS nb_in_use_bikes,
            ROUND(100 * SUM(latest_NbEmptyDocks) / SUM(latest_NbDocks), 2) AS percentage_in_use_bikes,
            SUM(latest_NbBrokenDocks) AS nb_broken_docks,
            ROUND(100 * SUM(latest_NbBrokenDocks) / SUM(latest_NbDocks), 2) AS percentage_broken_docks
        FROM latest_bikepoints
    """
    
    metrics_df = df.sparkSession.sql(sql_query)

    return metrics_df


def process(df, batch_id):
    """Process data received from kafka"""

    # create the schema
    schema = StructType([
                StructField("id", StringType()),
                StructField("common_name", StringType()),
                StructField("lat", StringType()),
                StructField("lon", StringType()),
                StructField("Installed", StringType()),
                StructField("Locked", StringType()),
                StructField("NbBikes", IntegerType()),
                StructField("NbEmptyDocks", IntegerType()),
                StructField("NbDocks", IntegerType()),
                StructField("NbBrokenDocks", IntegerType()),
                StructField("NbEBikes", IntegerType()),
                StructField("extraction_datetime", TimestampType())
    ])

    # select the columns received from kafka
    df = df.selectExpr("CAST(value AS STRING)")\
        .select( from_json( col("value"), schema ).alias("bp") )\
        .select(
          col("bp.id"),
          col("bp.NbBikes").alias("NbBikes"),
          col("bp.NbEmptyDocks").alias("NbEmptyDocks"),
          col("bp.NbDocks").alias("NbDocks"),
          col("bp.NbEBikes").alias("NbEBikes"),
          (col("bp.NbDocks") - (col("bp.NbBikes") + col("bp.NbEmptyDocks")) ).alias("NbBrokenDocks"),
          col("bp.extraction_datetime")
    )

    df = df.withWatermark('extraction_datetime', '4 minutes')

    # Calculate metrics using SQL
    metrics_df = calculate_metrics_sql(df)

    # Write the metrics in a row to the cassandra table
    metrics_df.write \
        .format("org.apache.spark.sql.cassandra") \
        .options(
            keyspace="transportation",
            table="metrics",
            ttl="86400"  # Setting the TTL to 24 hours
        ) \
        .mode("append") \
        .save()
    
    logger.info("A record has been inserted into the near-real-time metrics table.")