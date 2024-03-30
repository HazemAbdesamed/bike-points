import json
from .utils import logger
from kafka import KafkaProducer

def produce(bootstrap_servers, topic, bikepoints):
    """Produce data to kafka"""
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

        for bikepoint_data in bikepoints:
                producer.send(topic=topic, value=json.dumps(bikepoint_data).encode("utf-8"))
                logger.info(f"Entry produced to {topic} kafka topic : %s", json.dumps(bikepoint_data))
            
    except Exception as e:
        logger.error("Error in producing entry to kafka: %s", e)