import utils
from batch_layer.consuming import consume
from batch_layer.processing import process
from batch_layer.loading import load

def main():
    # Create a spark session
    spark_session = utils.create_spark_session()

    # Consume data from kafka
    bikepoints = consume(spark_session)

    # Process data using pyspark
    bikepoints_processed = process(bikepoints)

    # Launch the streaming process and load the data
    load(bikepoints_processed)

if __name__ == "__main__":
    main()