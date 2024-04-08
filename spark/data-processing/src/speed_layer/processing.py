from src.utils import logger
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, TimestampType
from pyspark.sql.functions import from_json,col


def calculate_metrics_sql(df, spark_session):
    """
    Calculates metrics using Spark SQL
    Returns a df contining the metrics in each column
    """

    # Register DataFrame as a temporary view
    df.createOrReplaceTempView("bike_points")

    # Calculate the metrics and convert them to string
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



def process(df, spark_session):
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

    # Calculate metrics using SQL
    metrics_df = calculate_metrics_sql(df, spark_session)

    # Serialize the df to write into kafka topic
    metrics_df = metrics_df.selectExpr("to_json(struct(*)) AS value")

    return metrics_df
