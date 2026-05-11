# fastapi app to run the real-time trending topic detector

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
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
    avg_bytes_changed: float
    velocity: float
    trend: str
    first_edit: datetime
    last_edit: datetime
    time_computed: datetime

class Stats(BaseModel):
    total_edits: int
    edits_per_minute: int
    articles_tracked: int
    last_aggregation: datetime
    

app = FastAPI(
        title="Wikipedia Stream API",
        description="Real-time trending topics from the Wikipedia edit stream.",
        version="1.0.0",
    )

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_conn():
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    hello i will put in frontend soon
    """

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
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
            ORDER by velocity * edit_count DESC 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        data = cursor.fetchall()

        if not data:
            return []
    return [Trending(**row) for row in data]

@app.get("/trending/rising", response_model=list[Trending])
def rising(limit: int = LIMIT, conn = Depends(get_db_conn)):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        '''
        RISING:
            determined by positive velocity -- accelerating in velocity meaning more edits than previous window
        '''
        query = """
            SELECT 
                *
            FROM trending_topics 
            where trend = 'trending'
            ORDER by velocity DESC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        data = cursor.fetchall()

        if not data:
            return []
    return [Trending(**row) for row in data]

@app.get("/trending/not trending", response_model=list[Trending])
def not_trending(limit: int = LIMIT, conn = Depends(get_db_conn)):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        '''
        NOT TRENDING:
            determined by negative velocity -- losing momentum meaning less edits than previous window
        '''
        query = """
            SELECT 
                *
            FROM trending_topics 
            where trend = 'not trending'
            ORDER by velocity ASC
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        data = cursor.fetchall()

        if not data:
            return []
    return [Trending(**row) for row in data]
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
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            SELECT 
                (SELECT COUNT(*) AS total_edits FROM wiki_edits) AS total_edits,
                (SELECT COUNT(*) as edits_per_minute from wiki_edits where time_received > now() - INTERVAL '1 minute') AS edits_per_minute,
                (SELECT COUNT(DISTINCT title) FROM trending_topics) AS articles_tracked,
                (SELECT max(time_computed) FROM trending_topics) AS last_aggregation;
            """
        cursor.execute(query) # sample query, fix later
        data = cursor.fetchone()
        if not data:
            return Stats(total_edits=0, edits_per_minute=0, articles_tracked=0, last_aggregation=datetime.now())
    return Stats(**data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)