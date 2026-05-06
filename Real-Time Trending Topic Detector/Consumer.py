
'''
process:
    1. initialize sql connection
    2. create consumer with retry
    3. check connection
    4. main loop to retrieve data and write to postgres
    5. in the case of fail, use idemoptent writes to postgres using insert ... on conflict do nothing

'''

'''
write to postgres model:
events coming off Kafka
    1. accumulate in a list
    2. when list hits 50 events:
        2a. write entire list to Postgres in one INSERT and commit to postgres (yea forgot that last part)
        2b. commit Kafka offset
        2c. clear the list
        2d. start accumulating again
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
from datetime import datetime, UTC

# configs
KAFKA_TOPIC = "wiki-edits"
KAFKA_BOOTSTRAP_SERVERS = ["localhost:9092"]
POSTGRES_CONFIG = {
    'dbname': 'wikistream',
    'user': 'wiki',
    'password': 'wiki',
    'host': 'localhost',
    'port': 5432
}

# # for timing analysis
# times = []

# postgres connection
def create_postgres_conn(retries: int = 10, delay: int = 5):
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(
                dbname=POSTGRES_CONFIG['dbname'],
                user=POSTGRES_CONFIG['user'],
                password=POSTGRES_CONFIG['password'],
                host=POSTGRES_CONFIG['host'],
                port=POSTGRES_CONFIG['port']
            )
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
            check_consumer_connection(consumer)
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

def write_batch(consumer, conn): # create batch, once batch hits 50 events, write to postgres, commit kafka offset, clear batch
    # batch
    batch = []
    BATCH_SIZE = 50
    
    try:
        for message in consumer:
            event = message.value
            
            if not event.get('id'):
                continue
            
            if len(batch) == 0:
                start_time = time.perf_counter()
            
            batch.append((
                event.get('id'),
                event.get('title'),
                event.get('user'),
                event.get('wiki'),
                event.get('server_url'),
                event.get('type'),
                event.get('bot'),
                event.get('length', {}).get('new', 0) - event.get('length', {}).get('old', 0),
                datetime.fromtimestamp(event.get("timestamp"), tz=UTC).isoformat(),
                datetime.fromtimestamp(int(time.time()), tz=UTC).isoformat()
            ))
            

            if len(batch) >= BATCH_SIZE:
                write_to_postgres(conn, batch)
                consumer.commit()
                end_time = time.perf_counter()
                
                process_time = end_time - start_time
                times.append(process_time)
                
                print(f"Batch written to postgres.")
                print(f"Batch processing time: {process_time:.2f} seconds")
                
                batch = []

        # flush remaining if producer is stopped midway
        
        if batch:
            write_to_postgres(conn, batch)
            consumer.commit()
            print(f"Remaining {len(batch)} events flushed to postgres.")
            
    # error handling
    except KafkaError as e:
        logging.error(f"Kafka error while consuming messages: {e}")
        
    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error while writing batch: {e}")
            
    except Exception as e:
        logging.error(f"Error writing batch to PostgreSQL: {e}")

# write to postgres
def write_to_postgres(conn, data):
    
    with conn.cursor() as cursor:
        
        insert_query = """
        INSERT INTO wiki_edits (id, title, username, wiki, server_url, edit_type, bot, bytes_changed, time_utc, time_received)
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
        """
        
        execute_values(cursor, insert_query, data)
    # uhh need this to commit to postgres db
    conn.commit()
    
# truncate table for new data when app starts
def truncate(conn):
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE wiki_edits")
    conn.commit()
    print("Table truncated successfully.")
    
# main loop to query, process data, retrieve from kafka topic

if __name__ == "__main__":
    consumer = create_consumer()
    conn = create_postgres_conn()
    
    # for timing analysis
    times = []
    
    # truncate (comment out if historical data is needed)
    truncate(conn)

    while True:
        try:
            write_batch(consumer, conn)
        except KeyboardInterrupt:
            average_time = sum(times) / len(times)
            print("consumer stopped by user.")
            print(f"average batch processing time: {average_time:.2f} seconds")
            break
        except Exception as e:
            logging.error(f"Error writing to PostgreSQL: {e}")