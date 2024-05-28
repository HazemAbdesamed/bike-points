import utils
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, DecimalType, TimestampType
from pyspark.sql.functions import from_json,col, to_date, date_format, weekofyear, expr


def process(df):
    """Process data received from kafka"""     
    schema = StructType([
                StructField("Id", StringType()),
                StructField("CommonName", StringType()),
                StructField("Lat", DecimalType(8, 6)),
                StructField("Lon", DecimalType(9, 6)),
                StructField("Installed", StringType()),
                StructField("Locked", StringType()),
                StructField("NbBikes", IntegerType()),
                StructField("NbEmptyDocks", IntegerType()),
                StructField("NbDocks", IntegerType()),
                StructField("NbBrokenDocks", IntegerType()),
                StructField("NbEBikes", IntegerType()),
                StructField("ExtractionDatetime", TimestampType())
    ])

    
    
    df = df.selectExpr("CAST(value AS STRING)")\
        .select( from_json( col("value"), schema ).alias("bp") )\
        .select(
        col("bp.Id").alias("bikepointid"),
        col("bp.commonname"),
        col("bp.lat"),
        col("bp.lon"),
        col("bp.installed"),
        col("bp.locked"),
        col("bp.NbBikes").alias("nbbikes"),
        col("bp.NbEmptyDocks").alias("nbemptydocks"),
        col("bp.NbDocks").alias("nbdocks"),
        col("bp.NbEBikes").alias("nbebikes"),
        (col("bp.NbDocks") - (col("bp.NbBikes") + col("bp.NbEmptyDocks")) ).alias("nbbrokendocks"),
        col("bp.extractiondatetime"),
        (to_date(col("ExtractionDatetime"))).alias("extractiondate"), 
        (date_format(col("ExtractionDatetime"), "EEEE")).alias("dayofweek") ,
        (weekofyear(col("ExtractionDatetime"))).alias("weekofyear")
    )

    # Convert Installed and Locked columns to Boolean
    df = df.withColumn("installed", expr("Installed == 'true'")) \
           .withColumn("locked", expr("Locked == 'true'"))
  
    return df