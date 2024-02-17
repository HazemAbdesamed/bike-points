from src.utils import create_spark_session
from src.consuming import consume
from src.processing import process
from src.loading import streaming

def main():
    # Create a spark session
    spark_session = create_spark_session()

    # Consume data from kafka
    bikepoints = consume(spark_session)

    # Process data using pyspark
    bikepoints_processed = process(bikepoints)
    
    # Launch the streaming process and load the data
    streaming(bikepoints_processed)

if __name__ == "__main__":
    main()    



      
    
    
