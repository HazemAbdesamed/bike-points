import os
import logging
from pyspark.sql import SparkSession

CASSANDRA_HOST = os.getenv("CASSANDRA_HOST")
CASSANDRA_PORT = os.getenv("CASSANDRA_PORT")
CASSANDRA_USER = os.getenv("CASSANDRA_USER")
CASSANDRA_PASSWORD = os.getenv("CASSANDRA_PASSWORD")

# Create the logger for spark part
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s')

logger = logging.getLogger("kafka_spark")



def create_spark_session():
    """Creates the Spark Session with suitable configs"""

    # packages  = ['org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0', 
    #              'org.apache.kafka:kafka-clients:3.5.0',
    #              'com.datastax.spark:spark-cassandra-connector_2.12:3.5.0']
#org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0

    try:
        spark = SparkSession \
                .builder \
                .master('local') \
                .config('spark.streaming.stopGracefullyOnShutdown', True)\
                .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
                .config("spark.cassandra.connection.port",CASSANDRA_PORT)\
                .config("spark.cassandra.auth.username", CASSANDRA_USER) \
                .config("spark.cassandra.auth.password", CASSANDRA_PASSWORD) \
                .appName("spark_bikepoints") \
                .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
     
        logging.info('Spark session created successfully')
        
        return spark

    except Exception as e:
        logging.error("Error in spark session creation: ", e)
