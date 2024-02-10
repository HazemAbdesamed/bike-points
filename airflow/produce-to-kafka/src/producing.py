import json
from kafka import KafkaProducer

bootstrap_servers = ['kafka1:9092']

def produce(bootstrap_servers, topic, bikepoints):
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    for bikepoint_data in bikepoints:
        producer.send(topic=topic, value=json.dumps(bikepoint_data).encode("utf-8"))