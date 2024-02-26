import os

from src.extraction import get_bikepoints_from_api
from src.preprocessing import select_fields
from src.producing import produce

TOPIC_NAME = os.environ.get("TOPIC_NAME")
BROKER1 = os.environ.get("BROKER1")
PORT1 = os.environ.get("PORT1")

bootstrap_servers = [f'{BROKER1}:{PORT1}']
kafka_topic = f'{TOPIC_NAME}'

def main():

    # Retrieve data from API
    bikepoints_data = get_bikepoints_from_api()

    # Process data
    processed_data = select_fields(bikepoints_data)

    # Send processed data to Kafka
    produce(bootstrap_servers, kafka_topic, processed_data)

if __name__ == "__main__":
    main()