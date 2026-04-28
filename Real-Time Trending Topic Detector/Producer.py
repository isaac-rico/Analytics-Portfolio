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

    # filter data to english wikipedia data
    for event in client.events():
        data = json.loads(event.data)
        # if bot and not enwiki continue, don't want bots or non english
        if data.get("bot") or data.get("wiki") != "enwiki":
            continue

    yield data

# create a producer that connects to kafka, with retry attempts max 10
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

# pull wikipedia edits, filter, send to kafka topic
def send_to_kafka(producer, topic, stream):
    # send data to kafka topic
    for data in stream:
        producer.send(topic, value=data)
    return

# flush data
def flush_data(producer):
    return producer.flush()

def check_producer_connection(producer):
    try:
        producer.bootstrap_connected()
        print("Producer is connected to Kafka.")
    except KafkaError as e:
        logging.error(f"Producer connection error: {e}")
        raise

# main loop
if __name__ == "__main__":
    producer = create_producer()
    check_producer_connection(producer)
    reconnect_attempts = 0

    while True:
        try:    
            data = get_stream()
            send_to_kafka(producer, KAKFA_TOPIC, data)
        
        except KafkaError as e:
            logging.error(f"Kafka error: {e}")
            reconnect_attempts += 1
            if reconnect_attempts > 5:
                logging.critical("Exceeded maximum Kafka reconnection attempts. Exiting.")
                break
            time.sleep(5)  # wait before retrying

        except KeyboardInterrupt:
            flush_data(producer)
            producer.close()
            print("Stream stopped by user.")
            break


    