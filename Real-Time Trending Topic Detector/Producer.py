# Producer for Kafka

# imports 

from kafka import KafkaProducer
from kafka.errors import KafkaError
from sseclient import SSEClient
import requests
import json
import time
import logging

# configs

KAKFA_TOPIC = "wiki-edits"
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]
LINK = "https://stream.wikimedia.org/v2/stream/recentchange"

headers = {
    "Accept": "text/event-stream",
    "User-Agent": "isaacarnell.rico@gmail.com"
}

# functions

def get_stream():
    res = requests.get(LINK, stream=True, headers=headers)
    client = SSEClient(res)
    return client

def create_producer(retries: int = 10, delay: int = 5):
    
    for attempt in range(1, retries + 1):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                retries=3,
                acks = "all",
            )
            
            print("Kafka Producer created successfully.")
            return producer

        except KafkaError as e:
            logging.warning(f"Attempt {attempt} - Failed to create Kafka Producer: {e}")
            time.sleep(delay)
            
    raise RuntimeError("Failed to create Kafka Producer after multiple attempts.")

def send_to_kafka(producer, topic, data):