# fastapi app to run the real-time trending topic detector

import logging
from fastapi import FastAPI, Depends, JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from datetime import datetime
from config import POSTGRES_CONFIG, LIMIT

class Trending(BaseModel):
    title: str
    edit_count: int
    unique_editors: int
    total_bytes_changed: int
    avg_bytes_changed: int
    velocity: float
    trend: str
    first_edit: datetime
    last_edit: datetime
    time_computed: datetime
    

app = FastAPI(
        title="Wikipedia Stream API",
        description="Real-time trending topics from the Wikipedia edit stream.",
        version="1.0.0",
    )

def get_db_conn():
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@app.get("/")
def read_root():
    return {"message": "wiki stream API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}


'''
trending flow:
    1. pull data from trending table
        a. what data
        b. how often
    2. display trending topics
'''
@app.get("/trending", response_model=list[Trending])
def trending(limit: int = LIMIT, conn = Depends(get_db_conn)):
    with conn.cursor(cursor=RealDictCursor) as cursor:
        '''
        TRENDING:
            determined by velocity multiplied by edit count
            this shows topics that are both active and accelerating in velocity 
            (velocity meaning if num of edits are increasing/decreasing from previous window to current window, num is the magnitude of the change)
            trending = positive velocity -- more edits than previous window
            not trending = negative velocity -- less edits than previous window
            stable = 0
        '''
        query = """
            SELECT 
                * -- mayb change later for more specifics 
            FROM trending_topics 
            ORDER by velocity * edit count DESC 
            LIMIT %s
        """
        cursor.execute(query, (limit))
        data = cursor.fetchall()

        if not data:
            return JSONResponse(
                status_code=201,
                content={"message": "pipeline warming up, please wait"},
            )
    return data


''' 
overall statistics:
    1. aggregated metrics
    - how many edits
    - how many articles
    - how many users
    - how many bytes changed
    - how many unique users
    etc
'''
@app.get("/stats")
def stats(conn = Depends(get_db_conn)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM wiki_edits") # sample query, fix later
        data = cursor.fetchall()
    return data