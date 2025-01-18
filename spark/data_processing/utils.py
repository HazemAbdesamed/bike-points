import os
import logging
from pyspark.sql import SparkSession



# Create the logger for spark part
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s')

logger = logging.getLogger("kafka_spark")


def create_spark_session(processing_nature):
    """Creates the Spark Session with suitable configs"""

    # packages  = ['org.postgresql:postgresql:42.7.4',
    #              'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0', 
    #              'org.apache.kafka:kafka-clients:3.5.0',
    #              'com.datastax.spark:spark-cassandra-connector_2.12:3.5.0']
#org.postgresql:postgresql:42.7.4,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0

    try:

        if processing_nature not in {"speed", "batch"}:
           raise ValueError(f"Invalid processing nature: {processing_nature}. Choose either 'speed' or 'batch'.")

        #Initialize SparkSession builder for batch and speed processing job
        builder = SparkSession\
                 .builder \
                 .master("local") \
                 .appName(f"spark_{processing_nature}_job")

        
        if processing_nature == "speed":
            # Cassandra configurations
            CASSANDRA_HOST = os.getenv("CASSANDRA_HOST")
            CASSANDRA_PORT = os.getenv("CASSANDRA_PORT")
            CASSANDRA_USER = os.getenv("CASSANDRA_USER")
            CASSANDRA_PASSWORD = os.getenv("CASSANDRA_PASSWORD")

            # Configure the builder for speed processing job
            builder = builder \
                .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
                .config("spark.cassandra.connection.port", CASSANDRA_PORT) \
                .config("spark.cassandra.auth.username", CASSANDRA_USER) \
                .config("spark.cassandra.auth.password", CASSANDRA_PASSWORD) \
                .config('spark.streaming.stopGracefullyOnShutdown', True) \
                .config("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", False) \

        
        # Create Spark session
        spark = builder.getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")
     
        logging.info('Spark session created successfully')
        
        return spark

    except Exception as e:
        logging.error("Error in spark session creation: ", e)



def get_postgres_jdbc_url():
    """
    Constructs the JDBC URL for PostgreSQL.
    """
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_HISTORICAL_DATA_DB")

    return f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def get_postgres_properties():
    """
    Returns the properties required for PostgreSQL JDBC connection.
    
    Returns: dict: A dictionary of JDBC properties.
    """
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    
    return {
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "driver": "org.postgresql.Driver"
    }