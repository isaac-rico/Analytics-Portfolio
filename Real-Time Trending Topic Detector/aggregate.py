# script to aggregate data from wiki_edits table -> trending topic table

import psycopg2
import schedule
import time
import logging

POSTGRES_CONFIG = {
    'dbname': 'wikistream',
    'user': 'wiki',
    'password': 'wiki',
    'host': 'localhost',
    'port': 5432
}

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

def aggregate_data(conn, cursor):

    trending_query = """
        SELECT 
            title,   
            wiki,
            count(*) as edit_count,
            count(distinct username) as unique_editors,
            min(time_utc) as first_edit,
            max(time_utc) as last_edit
            FROM wiki_edits 
        where time_utc > DATEADD(minute, -5, GETDATE())
        group by title, wiki
        order by edit_count desc;
    """
    cursor.execute(trending_query)
    
    results = cursor.fetchall()
    return results