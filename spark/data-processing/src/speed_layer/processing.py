from ..utils import logger
from pyspark.sql.types import StructType,StructField,IntegerType,StringType, TimestampType
from pyspark.sql.functions import from_json,col
from .realtime_metrics import *

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
                StructField("ExtractionDatetime", TimestampType())
    ])

    
    
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

    return df
