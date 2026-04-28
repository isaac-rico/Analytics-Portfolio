
'''
process:
    1. initialize sql connection
    2. create consumer with retry
    3. check connection
    4. main loop to retrieve data and write to postgres
    5. in the case of fail, use idemoptent writes to postgres using insert ... on conflict do nothing

'''

# imports
from kafka import KafkaConsumer
import json
import logging
import time
from kafka.errors import KafkaError
from psycopg2 import sql
import psycopg2
from sqlalchemy import create_engine
from psycopg2.extras import execute_values, Json, DictCursor

# configs
KAFKA_TOPIC = "wiki-edits"
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]
POSTGRES_CONFIG = {
    'dbname': 'wiki',
    'user': 'postgres',
    'password': '12345',
    'host': 'localhost',
    'port': 5432
}

# postgres connection
def create_postgres_conn(retries: int = 10, delay: int = 5):
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            print("PostgreSQL connection established successfully.")
            return conn

        except psycopg2.Error as e:
            logging.warning(f"Error connecting to PostgreSQL: {e}, Attempt {attempt} of {retries}")
            time.sleep(delay)
    raise RuntimeError("Failed to connect to PostgreSQL after multiple attempts.")

# functions
def create_consumer(retries: int = 10, delay: int = 5):
    for attempt in range(1, retries + 1):
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='wiki-edit-consumers'
            )
            print("Kafka Consumer created successfully.")
            return consumer

        except KafkaError as e:
            logging.warning(f"Attempt {attempt} - Failed to create Kafka Consumer: {e}")
            time.sleep(delay)
            
    raise RuntimeError("Failed to create Kafka Consumer after multiple attempts.")

def check_consumer_connection(consumer):
    try:
        consumer.bootstrap_connected()
        print("Consumer is connected to Kafka.")
    except KafkaError as e:
        logging.error(f"Consumer connection error: {e}")
        raise

def write_to_postgres(conn, data):
    # implement logic to write data to postgres using insert ... on conflict do nothing
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO wiki_edits (page_id, user, timestamp, edit_type, wiki, is_bot, title)
        VALUES %s
        ON CONFLICT (page_id) DO NOTHING;
        """
        # example data to insert
        execute_values(cursor, insert_query, data)

# main loop to query, process data, retrieve from kafka topic

if __name__ == "__main__":
    consumer = create_consumer()
    check_consumer_connection(consumer)
    conn = create_postgres_conn()

    while True:
        for message in consumer:
            try:
                write_to_postgres(conn, message.value)
                consumer.commit()
            except Exception as e:
                logging.error(f"Error writing to PostgreSQL: {e}")

            print(f"Received message: {message.value}")
            # process data and write to postgres here
            # if fail, use idemoptent writes to postgres using insert ... on conflict do nothing