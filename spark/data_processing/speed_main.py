from utils import create_spark_session
from speed_layer.consuming import consume
from speed_layer.processing import process
from speed_layer.loading import streaming

def main():
    # Create a spark session
    spark_session = create_spark_session()

    # Consume data from kafka
    bikepoints = consume(spark_session)

    # Process data using pyspark
    bikepoints_processed = process(bikepoints, spark_session)

    # Launch the streaming process and load the data
    streaming(bikepoints_processed)

if __name__ == "__main__":
    main()