# Producer for Kafka

'''
process:
    1. create kafka producer with retry attempts max 10
    2. connect to wikipedia stream using SSEClient
    3. filter data to enwiki and non bot edits
    4. send data to kafka topic
    5. flush data to ensure it's sent to kafka
'''


# imports 

from kafka import KafkaProducer
from kafka.errors import KafkaError
import requests
import json
import time
import logging 

# configs in config.py
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, WIKI_STREAM_URL, HEADERS

# functions

def get_stream():
    print("Getting stream...")
    res = requests.get(WIKI_STREAM_URL, stream=True, headers=HEADERS)
    
    # ======= requests iter_lines method =======
    for line in res.iter_lines():
        if not line:
            continue
        
        # SSE data lines start with "data: "
        line = line.decode("utf-8")
        if not line.startswith("data:"):
            continue
        
        # strip the "data: " prefix and parse the JSON
        raw = line[len("data:"):].strip()
        
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        
        # if bot entries are needed, comment this out
        if data.get("bot"):
            continue
        
        # filter to only english wiki edits
        if data.get("wiki") != "enwiki":
            continue

        # filter to only edits
        if data.get("type") != "edit":
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
    try:
        for data in stream:
            producer.send(topic, value=data)
    except KafkaError as e:
        logging.error(f"Kafka error while sending data: {e}")    

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
            send_to_kafka(producer, KAFKA_TOPIC, data)
            print("Data sent to Kafka.")
        
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
        
        except Exception as e:
            logging.error(f"Error sending data to Kafka: {e}")


    