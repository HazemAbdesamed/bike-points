from utils import logger
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, TimestampType
from pyspark.sql.functions import from_json, col, sum, rank, window, max, first, last, desc, expr, max_by
from pyspark.sql.window import Window


def calculate_metrics_sql(df):
    """
    Calculates metrics using Spark SQL
    Returns a df contining the metrics in each column
    """

    df = df.withWatermark('ExtractionDatetime', '4 minutes')

    df = df.filter((col("Id") == "BikePoints_1") | (col("Id") == "BikePoints_2"))

    # Calculate latest values within the window
    df = df.groupBy("Id") \
           .agg(    
            max_by("NbBikes", "ExtractionDatetime").alias("latest_NbBikes")
           ,max_by("NbDocks", "ExtractionDatetime").alias("latest_NbDocks")
           ,max_by("NbEmptyDocks", "ExtractionDatetime").alias("latest_NbEmptyDocks")
           ,max_by("NbBrokenDocks", "ExtractionDatetime").alias("latest_NbBrokenDocks")
          )
    # # Register DataFrame as a temporary view
    # df.createOrReplaceTempView("bike_points")
    sql_query = """
        WITH latest_bikepoints AS ( 
        SELECT 
            ID,
            max_by(latest_NbBikes, ExtractionDatetime) AS latest_NbBikes,
            max_by(latest_NbDocks, ExtractionDatetime) AS latest_NbDocks,
            max_by(latest_NbEmptyDocks, ExtractionDatetime) AS latest_NbEmptyDocks,
            max_by(latest_NbBrokenDocks, ExtractionDatetime) AS latest_NbBrokenDocks
        FROM bike_points
        GROUP BY ID
        )
        SELECT 
            SUM(latest_NbBikes) AS nb_available_bikes,
            CAST(ROUND(100 * SUM(latest_NbBikes) / SUM(latest_NbDocks), 2) AS STRING) AS percentage_available_bikes,
            SUM(latest_NbEmptyDocks) AS nb_in_use_bikes,
            CAST(ROUND(100 * SUM(latest_NbEmptyDocks) / SUM(latest_NbDocks), 2) AS STRING) AS percentage_in_use_bikes,
            SUM(latest_NbBrokenDocks) AS nb_broken_docks,
            CAST(ROUND(100 * SUM(latest_NbBrokenDocks) / SUM(latest_NbDocks), 2) AS STRING) AS percentage_broken_docks
        FROM bike_points
     """

    # Execute SQL query
    # metrics_df = spark_session.sql(sql_query)

    metrics_df = df.agg(
        # max("window.start").alias("max_window_start"),
        # max("window.end").alias("max_window_end"),
        sum("latest_NbBikes").alias("nb_available_bikes"),
        sum("latest_NbEmptyDocks").alias("nb_in_use_bikes"),
        sum("latest_NbBrokenDocks").alias("nb_broken_docks")
    # ).withColumn("percentage_available_bikes", concat(round((col("nb_available_bikes") / col("latest_NbDocks")) * 100, 2), lit("%"))
    # ).withColumn("percentage_in_use_bikes", concat(round((col("nb_in_use_bikes") / col("latest_NbDocks")) * 100, 2), lit("%"))
    # ).withColumn("percentage_broken_docks", concat(round((col("nb_broken_docks") / col("latest_NbDocks")) * 100, 2), lit("%"))
    ).select(
        # "max_window_start",
        # "max_window_end",
        "nb_available_bikes",
        # "percentage_available_bikes",
        "nb_in_use_bikes",
        # "percentage_in_use_bikes",
        "nb_broken_docks",
        # "percentage_broken_docks"
    )

    metrics_df.printSchema()

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

    # Calculate metrics using SQL
    metrics_df = calculate_metrics_sql(df, batch_id)

    # Serialize the df to write into kafka topic
    metrics_df = metrics_df.selectExpr("to_json(struct(*)) AS value")
    
    return metrics_df
