# fastapi app to run the real-time trending topic detector

import json
import logging
from fastapi import FastAPI, HTTPException
import psycopg2
import requests
from sseclient import SSEClient

# configs

POSTGRES_CONFIG = {
    'dbname': 'wikistream',
    'user': 'wiki',
    'password': 'wiki',
    'host': 'localhost',
    'port': 5432
}

app = FastAPI(
        title="Wikipedia Stream API",
        description="Real-time trending topics from the Wikipedia edit stream.",
        version="1.0.0",
    )

def get_db_conn():
    return psycopg2.connect(
        dbname=POSTGRES_CONFIG['dbname'],
        user=POSTGRES_CONFIG['user'],
        password=POSTGRES_CONFIG['password'],
        host=POSTGRES_CONFIG['host'],
        port=POSTGRES_CONFIG['port']
        )

@app.get("/")
def read_root():
    return {"message": "wiki stream API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}


'''
trending flow:
    1. pull data from trending table
    2. 
'''
@app.get("/trending")
def trending():
    pass

@app.get("/stats")
def stats():
    pass