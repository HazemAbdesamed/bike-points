import utils
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, DecimalType, TimestampType
from pyspark.sql.functions import from_json,col, to_date, date_format, weekofyear, dayofweek, expr, cast


def process(df):
    """Process data received from kafka"""     
    schema = StructType([
                StructField("id", StringType()),
                StructField("common_name", StringType()),
                StructField("lat", DecimalType(8, 6)),
                StructField("lon", DecimalType(9, 6)),
                StructField("Installed", StringType()),
                StructField("Locked", StringType()),
                StructField("NbBikes", IntegerType()),
                StructField("NbEBikes", IntegerType()),
                StructField("NbEmptyDocks", IntegerType()),
                StructField("NbDocks", IntegerType()),
                StructField("extraction_datetime", TimestampType())
    ])

    
    
    df = df.selectExpr("CAST(value AS STRING)")\
        .select( from_json( col("value"), schema ).alias("bp") )\
        .select(
          col("bp.id").alias("bike_point_id"),
          col("bp.common_name").alias("common_name"),
          col("bp.lat").alias("lat"),
          col("bp.lon").alias("lon"),
          col("bp.Installed").alias("installed"),
          col("bp.Locked").alias("locked"),
          col("bp.NbBikes").alias("nb_bikes"),
          col("bp.NbEBikes").alias("nb_ebikes"),
          col("bp.NbEmptyDocks").alias("nb_empty_docks"),
          col("bp.NbDocks").alias("nb_docks"),
          (col("bp.NbDocks") - (col("bp.NbBikes") + col("bp.NbEmptyDocks")) ).alias("nb_broken_docks"),
          col("bp.extraction_datetime").alias("extraction_datetime"),
          (to_date(col("bp.extraction_datetime"))).alias("extraction_date"),
          (date_format(col("bp.extraction_datetime"), "MMMM")).alias("month_name"),
          (date_format(col("bp.extraction_datetime"), "M")).alias("month_number"),
          (date_format(col("bp.extraction_datetime"), "dd")).alias("day_of_month"), 
          (weekofyear(col("bp.extraction_datetime"))).alias("week_of_year"),
          (date_format(col("bp.extraction_datetime"), "EEEE")).alias("day_of_week"),
          (dayofweek(col("bp.extraction_datetime"))).alias("day_of_week_number"),
          (date_format(col("bp.extraction_datetime"), "H")).alias("Hour")
        ) \
        .where(col("bp.id").isNotNull() & col("bp.extraction_datetime").isNotNull())

    # Convert Installed and Locked columns to Boolean
    # Convert month_number and day_of_month to Integer
    # create hour_interval column
    df = df.withColumn("installed", expr("installed == 'true'")) \
           .withColumn("locked", expr("locked == 'true'")) \
           .withColumn("lat", col("Lat").cast(DecimalType(8, 6))) \
           .withColumn("lon", col("Lon").cast(DecimalType(9, 6))) \
           .withColumn("month_number", col("month_number").cast(IntegerType())) \
           .withColumn("day_of_month", col("day_of_month").cast(IntegerType())) \
           .withColumn("hour_interval",
             expr("concat('[', floor(hour(extraction_datetime) / 2) * 2, ', ', (floor(hour(extraction_datetime) / 2) * 2 + 2) % 24, '[')"))
         
    
    return df 
