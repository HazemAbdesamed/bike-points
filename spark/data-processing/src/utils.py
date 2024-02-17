import logging
from pyspark.sql import SparkSession


# Create the logger for spark part
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')

logger = logging.getLogger("kafka_spark")



def create_spark_session():
    """Creates the Spark Session with suitable configs"""

    # packages  = ['org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0', 
    #              'org.apache.kafka:kafka-clients:3.5.0']

    try:
        # Spark session is established with cassandra and kafka jars. Suitable versions can be found in Maven repository.
        spark = SparkSession \
                .builder \
                .master('local') \
                .appName("spark_bikepoints") \
                .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
     
        logging.info('Spark session created successfully')
        
        return spark

    except Exception as e:
        logging.error("Error in spark session creation: ", e)
