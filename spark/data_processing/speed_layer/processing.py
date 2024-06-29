import os
from utils import logger
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, TimestampType
from pyspark.sql.functions import from_json, col, sum, max, max_by, concat, lit, round

BROKER1 = os.environ.get("BROKER1")
PORT1 = os.environ.get("PORT1")
TOPIC_METRICS = os.environ.get("TOPIC_METRICS")

def calculate_metrics_sql(df, batch_id):
    """
    Calculates metrics using Spark SQL
    Returns a df contining the metrics in each column
    """

    df = df.filter((col("Id") == "BikePoints_1") | (col("Id") == "BikePoints_2"))

    # Calculate latest values within the window
    df = df.groupBy("Id") \
           .agg(
            max("ExtractionDatetime").alias("ExtractionDatetime"),
            max_by("NbBikes", "ExtractionDatetime").alias("latest_NbBikes"),
            max_by("NbDocks", "ExtractionDatetime").alias("latest_NbDocks"),
            max_by("NbEmptyDocks", "ExtractionDatetime").alias("latest_NbEmptyDocks"),
            max_by("NbBrokenDocks", "ExtractionDatetime").alias("latest_NbBrokenDocks")
          )

    metrics_df = df.agg(
        max("ExtractionDatetime").alias("ExtractionDatetime"),
        sum("latest_NbBikes").alias("nb_available_bikes"),
        sum("latest_NbDocks").alias("latest_NbDocks"),
        sum("latest_NbEmptyDocks").alias("nb_in_use_bikes"),
        sum("latest_NbBrokenDocks").alias("nb_broken_docks")
        ) \
     .withColumn("percentage_available_bikes", concat(round((col("nb_available_bikes") / col("latest_NbDocks")) * 100, 2), lit("%"))) \
     .withColumn("percentage_in_use_bikes", concat(round((col("nb_in_use_bikes") / col("latest_NbDocks")) * 100, 2), lit("%"))) \
     .withColumn("percentage_broken_docks", concat(round((col("nb_broken_docks") / col("latest_NbDocks")) * 100, 2), lit("%"))
    ).select(
        "ExtractionDatetime",
         "nb_available_bikes",
        "percentage_available_bikes",
        "nb_in_use_bikes",
        "percentage_in_use_bikes",
        "nb_broken_docks",
        "percentage_broken_docks"
    )


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
    metrics_df = calculate_metrics_sql(df, batch_id)

    # Serialize the df to write into kafka topic
    metrics_df = metrics_df.selectExpr("to_json(struct(*)) AS value")
    
    metrics_df.show(truncate=False)

    # metrics_df.write \
    #     .format("kafka") \
    #     .option("kafka.bootstrap.servers", f"{BROKER1}:{PORT1}") \
    #     .option("topic", "metrics") \
    #     .save()

    return metrics_df
