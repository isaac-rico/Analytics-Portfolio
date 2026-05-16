# Real-Time Trending Topic Detector for Wikipedia

## TL;DR
- Ingests live Wikipedia edit events through Kafka, stores them in PostgreSQL, and serves trending topics using a FastAPI backend and a React frontend.
- Filtered and cleaned a Wikipedia SSE stream to only include edits to human-made English Wikpedia (enwiki) pages, dropping bot edits, and non-edit event types.
- Implemented a tiered cold-start window that expands dynamically as data flows in, grounded in observed data influx of ~100-150 edits per minute.
- Designed a velocity-based algorithm to determine trending topics and their trend acceleration by comparing activity between two rolling time windows.
- Built a data-quality Kafka Consumer that pushes data into PostgreSQL in batches, ensuring no data is lost even during error.

---

## Project Overview

This project detects trending Wikipedia articles and topics in real time by ingesting Wikipedia's Server-Side Events (SSE) stream, processing edits through a Kafka pipeline, aggregating them into a PostgreSQL database, and displaying results through a REST API backend and an interactive dashboard.

This pipeline is always running, as the producer maintains a constant connection with the SSE stream, the consumer continuously writes to Postgres, and the aggregation layer refreshes trending results every 2 minutes. Different from a typical static analytics project.

The project focuses on the full data engineering lifecycle: stream ingestion, message brokering, batched storage, time-windowed aggregation, API serving, and frontend visualization. This is all running locally via Docker Compose.

*Why this kind of project?*

I wanted to expand my breadth of knowledge with various data tools, more specifically utilizing a real-time event streaming platform like Kafka, to produce visualized results based on continous influxes of data. This project is more structured than my previous projects, as common best-practice techniques were implemented such as using Kafka's offset system with a commit after a successful batched postgres write, python-dotenv, docker compose, a REST API implementation, and logging with error detection.*

*The frontend was created with the assistance of an AI agent. My primary focus for this project was the data engineering layer. The frontend exists to make the pipeline's output visible and interactive, not a demonnstration of my frontend skills.

--- 

## Skills Demonstrated

- real-time stream ingestion (SSE)
- message brokering with Apache Kafka
- producer/consumer architecture
- batched database writes with error handling
- manual Kafka offset committing
- time-windowed SQL aggregation
- velocity-based trending algorithm design
- REST API development with FastAPI
- Pydantic response modeling
- cold start problem detection and mitigation
- environment-based configuration management
- Docker Compose orchestration
- React + TypeScript frontend development

--- 

## Tools & Technologies

- **Data Stream Source**: Wikipedia SSE Stream
- **Message Broker**: Apache Kafka
- **Storage**: PostgreSQL
- **Backend**: FastAPI + uvicorn, psycopg2
- **Aggregation**: Python + SQL
- **Frontend**: React + Typescript + Axios (FastAPI integration)
- **Orchestration**: Docker Compose
- **Configuration**: python-dotenv

--- 

## Data Source

**Source**: Wikimedia Foundation - [Recent Changes SSE Stream](https://stream.wikimedia.org/v2/stream/recentchange)

This link is a free, public server-side event stream for every Wikimedia edit worldwide. No API key is needed for requests, just need a valid ```User-Agent``` header identifying the client (just use an email, you're allowed 200 requests/email I believe).

**Filters Applied at Ingestion**: 
- ```wiki == "enwiki"``` - English Wikipedia only
- ```bot == false``` - ignore bots
- ```type == "edit"``` - only edits, dropping ```categorize``` and ```new``` page events

**Core Fields Used:**
- ```id```
- ```title```
- ```user```
- ```wiki```
- ```server_url```
- ```type```
- ```bot```
- ```bytes_changed```
- ```time_utc```

--- 

## Project Pipeline
```
Wikipedia SSE Stream
     ↓
Python Producer 
(filters + event serialization)
     ↓
Kafka Topic
(wiki-edits)
     ↓
Python Consumer
(batched writes, manual offset commits)
     ↓
PostgreSQL
(wiki_edits table)
     ↓
Aggregation Script
(runs every 2 minutes, two-window velocity query)
     ↓
PostgreSQL
(trending_topics table)
     ↓
FastAPI
(/trending, /trending/rising, /trending/not trending, /stats)
     ↓
React Frontend Dashboard
```

---


