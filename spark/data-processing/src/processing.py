from .utils import logger
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, TimestampType
from pyspark.sql.functions import from_json,col

def process(df):
    """Process data received from kafka"""     
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
                StructField("ExtractedDatetime", TimestampType())
    ])
    
    df = df.selectExpr("CAST(value AS STRING)")\
        .select( from_json( col("value"), schema ).alias("data") )\
        .select(
        col("data.Id"),
        col("data.CommonName"),
        col("data.Lat"),
        col("data.Lon"),
        col("data.Installed"),
        col("data.Locked"),
        col("data.NbBikes").cast(IntegerType()).alias("NbBikes"),
        col("data.NbEmptyDocks").cast(IntegerType()).alias("NbEmptyDocks"),
        col("data.NbDocks").cast(IntegerType()).alias("NbDocks"),
        (col("data.NbDocks") - col("data.NbBikes") + col("data.NbEmptyDocks")).cast(IntegerType()).alias("NbBrokenDocks"),
        col("data.NbEBikes").cast(IntegerType()).alias("NbEBikes"),
        col("data.ExtractedDatetime")
    ) 
    
    logger.info("Data processed in spark successfully")
    return df