from src.extraction import get_bikepoints_from_api
from src.preprocessing import select_properties
from src.producing import produce

def main():
    bootstrap_servers = ['kafka1:9092']
    kafka_topic = 'bike-points'

    # Retrieve data from API
    bikepoints_data = get_bikepoints_from_api()

    # Process data
    processed_data = select_properties(bikepoints_data)

    # Send processed data to Kafka
    produce(bootstrap_servers, kafka_topic, processed_data)

if __name__ == "__main__":
    main()