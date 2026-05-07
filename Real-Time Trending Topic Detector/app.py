# fastapi app to run the real-time trending topic detector

import json
import logging
from fastapi import FastAPI, HTTPException, Depends
import psycopg2
import requests
from sseclient import SSEClient

from config import POSTGRES_CONFIG

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
@app.get("/trending")
def trending(conn = Depends(get_db_conn)):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM trending_topics")
        data = cursor.fetchall()
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