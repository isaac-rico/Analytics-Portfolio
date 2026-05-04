# script to aggregate data from wiki_edits table -> trending topic table

import psycopg2
from psycopg2.extras import execute_values
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

def trending_query(conn):

    with conn.cursor() as cursor:
        query = """
            with prev_window as (
                SELECT
                    title,   
                    wiki,
                    count(*) as edit_count,
                    count(distinct username) as unique_editors,
                    sum(bytes_changed) as total_bytes_changed,
                    avg(bytes_changed) as avg_bytes_changed,
                    min(time_utc) as first_edit,
                    max(time_utc) as last_edit,
                    now() as time_computed
                    FROM wiki_edits 
                where time_computed > interval '10 minutes' and time_computed <= now() - interval '5 minutes'
                order by time_computed desc
            ),

            curr_window as (
                SELECT
                    title,   
                    wiki,
                    count(*) as edit_count,
                    count(distinct username) as unique_editors,
                    sum(bytes_changed) as total_bytes_changed,
                    avg(bytes_changed) as avg_bytes_changed,
                    min(time_utc) as first_edit,
                    max(time_utc) as last_edit,
                    now() as time_computed
                    FROM wiki_edits 
                where time_computed > now() - interval '5 minutes'
                order by time_computed desc
            ),

            velocity as (
                SELECT 
                    curr_window.title,
                    curr_window.edit_count - coalesce(prev_window.edit_count, 0) as velocity,
                    case
                        when curr_window.edit_count > coalesce(prev_window.edit_count, 0) then 'trending'
                        else 'not trending'
                    end as trend
                FROM curr_window
                left join prev_window on curr_window.title = prev_window.title
            )

            SELECT
                curr_window.title,
                curr_window.wiki,
                curr_window.edit_count,
                curr_window.unique_editors,
                curr_window.total_bytes_changed,
                curr_window.avg_bytes_changed,
                curr_window.first_edit,
                curr_window.last_edit,
                now() as time_computed,
                v.velocity,
                v.trend
            FROM curr_window 
            left join velocity v on curr_window.title = v.title 
        """

    cursor.execute(query)
    results = cursor.fetchall()

    return results

def write_to_table(conn, data):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO 
            trending_topics (
                title, 
                wiki, 
                edit_count, 
                unique_editors, 
                total_bytes_changed, 
                avg_bytes_changed, 
                first_edit, 
                last_edit, 
                time_computed,
                velocity,
                trend
            )
        VALUES %s
        ON CONFLICT (title, wiki) DO UPDATE SET
            edit_count = EXCLUDED.edit_count,
            unique_editors = EXCLUDED.unique_editors,
            total_bytes_changed = EXCLUDED.total_bytes_changed,
            avg_bytes_changed = EXCLUDED.avg_bytes_changed,
            first_edit = EXCLUDED.first_edit,
            last_edit = EXCLUDED.last_edit,
            time_computed = EXCLUDED.time_computed,
            velocity = EXCLUDED.velocity,
            trend = EXCLUDED.trend;
        """
        execute_values(cursor, insert_query, data)
    conn.commit()

def main(conn):
    trending_query = trending_query(conn)
    write_to_table(conn, trending_query)

if __name__ == "__main__":
    conn = create_postgres_conn()
    # schedule to run query every minute
    schedule.every(1).minutes.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)