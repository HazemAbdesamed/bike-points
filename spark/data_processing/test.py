from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, max_by, col

spark = SparkSession \
                .builder \
                .master('local') \
                .appName("spark_test") \
                .getOrCreate()

df = spark.createDataFrame(
    [
      ("BikePoints_1", 6, "2024-06-22 18:00:48"),
      ("BikePoints_1", 6, "2024-06-22 18:00:48"),
      ("BikePoints_1", 2, "2024-06-22 19:37:14"),
      ("BikePoints_2", 8, "2024-06-22 18:55:11"),
      ("BikePoints_2", 8, "2024-06-22 18:55:11"),
      ("BikePoints_2", 8, "2024-06-22 19:35:14"),
      ("BikePoints_3", 8, "2024-06-21 19:35:14"),

    ]
    ,["Id", "NbBikes", "ExtractionDatetime"]
    ).withColumn("ExtractionDatetime", to_timestamp("ExtractionDatetime"))

df = df.groupBy("Id") \
       .agg(
           max_by("NbBikes", "ExtractionDatetime").alias("latest_NbBikes")
       )
df = df.withColumn("sum_NbBikes", sum("latest_NbBikes"))
df.show()