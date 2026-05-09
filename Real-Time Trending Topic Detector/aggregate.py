# script to aggregate data from wiki_edits table -> trending topic table

import psycopg2
from psycopg2.extras import execute_values
import schedule
import time
import logging

from config import POSTGRES_CONFIG

def create_postgres_conn(retries: int = 10, delay: int = 5):
    for attempt in range(1, retries + 1):
        try:
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            print("Postgres connection established successfully.")
            return conn

        except psycopg2.Error as e:
            logging.warning(f"Error connecting to postgres: {e}, Attempt {attempt} of {retries}")
            time.sleep(delay)
    raise RuntimeError("Failed to connect to postgres after multiple attempts.")

# determine window size based on num of events
def get_window_size(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM wiki_edits")
        count = cursor.fetchone()[0]

        if count < 500:
            return 2
        elif count < 1500:
            return 5
        elif count < 3000:
            return 15
        elif count < 5000:
            return 30

def trending_query(conn):
    window_size = get_window_size(conn)
    print(f"window size: {window_size}")

    with conn.cursor() as cursor:
        query = """
            with prev_window as (
                SELECT
                    title,   
                    count(*) as edit_count,
                    count(distinct username) as unique_editors,
                    sum(bytes_changed) as total_bytes_changed,
                    avg(bytes_changed) as avg_bytes_changed,
                    min(time_utc) as first_edit,
                    max(time_utc) as last_edit,
                    now() as time_computed
                FROM wiki_edits 
                where time_received > now() - interval '%s minutes'
                and time_received <= now() - interval '%s minutes' 
                group by title
                order by time_computed desc
            ),

            curr_window as (
                SELECT
                    title,   
                    count(*) as edit_count,
                    count(distinct username) as unique_editors,
                    sum(bytes_changed) as total_bytes_changed,
                    avg(bytes_changed) as avg_bytes_changed,
                    min(time_utc) as first_edit,
                    max(time_utc) as last_edit,
                    now() as time_computed
                FROM wiki_edits 
                where time_received > now() - interval '%s minutes'
                group by title
                order by time_computed desc
            ),

            velocity as (
                SELECT 
                    curr_window.title,
                    curr_window.edit_count - coalesce(prev_window.edit_count, 0) as velocity, -- velocity as taking the diff between current and previous time windows
                    case
                        when curr_window.edit_count > coalesce(prev_window.edit_count, 0) then 'trending'     -- more activity than prev time window
                        when curr_window.edit_count < coalesce(prev_window.edit_count, 0) then 'not trending' -- less activity than prev time window
                        else 'stable' -- same activity in both time windows
                    end as trend
                FROM curr_window
                left join prev_window on curr_window.title = prev_window.title
            )

            SELECT
                curr_window.title,
                curr_window.edit_count,
                curr_window.unique_editors,
                curr_window.total_bytes_changed,
                curr_window.avg_bytes_changed,
                v.velocity,
                v.trend,
                curr_window.first_edit,
                curr_window.last_edit,
                now() as time_computed
            FROM curr_window 
            left join velocity v on curr_window.title = v.title 
        """

        cursor.execute(query, (window_size*2, window_size, window_size))
        results = cursor.fetchall()

    return results

def write_to_table(conn, data):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO 
            trending_topics (
                title,  
                edit_count, 
                unique_editors, 
                total_bytes_changed, 
                avg_bytes_changed, 
                velocity,
                trend,
                first_edit, 
                last_edit, 
                time_computed
            )
        VALUES %s
        ON CONFLICT (title) DO UPDATE SET
            edit_count = EXCLUDED.edit_count,
            unique_editors = EXCLUDED.unique_editors,
            total_bytes_changed = EXCLUDED.total_bytes_changed,
            avg_bytes_changed = EXCLUDED.avg_bytes_changed,
            velocity = EXCLUDED.velocity,
            trend = EXCLUDED.trend,
            first_edit = EXCLUDED.first_edit,
            last_edit = EXCLUDED.last_edit,
            time_computed = EXCLUDED.time_computed;
        """
        execute_values(cursor, insert_query, data)
    conn.commit()

## uncomment if connection check is needed
# def ping_conn(conn):
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT 1")
#         return conn
#     except psycopg2.OperationalError:
#         return create_postgres_conn()

def truncate(conn):
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE trending_topics")
    conn.commit()
    print("Table truncated successfully.")

def main(conn):
    results = trending_query(conn)
    write_to_table(conn, results)
    print("trending topics updated")

if __name__ == "__main__":
    conn = create_postgres_conn()
    truncate(conn) # truncate table for new data -- comment out if historical data is needed
    count = 0

    try:
        # schedule to run query every 5 minutes
        schedule.every(3).minutes.do(lambda: main(conn))

        while True:
            # conn = ping_conn(conn) # uncomment if connection check is needed
            schedule.run_pending()
            time.sleep(1)
            count += 1
            if count % 30 == 0:
                print(f"stream running {count} seconds")

    except KeyboardInterrupt:
        print("Stream stopped by user")
    
    except Exception as e:
        logging.error(f"Error writing to postgres: {e}")