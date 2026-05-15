# Real-Time Trending Topic Detector for Wikipedia

## TL;DR
- built an end-to-end **real-time streaming pipeline** using **Kafka, Python, PostgreSQL, FastAPI** with a **React** frontend
- ingests live Wikipedia edit events through Kafka, stores them in PostgreSQL, and serves trending topics using a FastAPI backend and a React frontend.
- Filtered and cleaned a Wikipedia SSE stream to only include edits to human-made English Wikpedia (enwiki) pages, dropping bot edits, and non-edit event types.
- implemented a tiered cold-start window that expands dynamically as data flows in, grounded in observed data influx of ~100-150 edits per minute.
- designed a velocity-based algorithm to determine trending topics and their trend acceleration by comparing activity between two rolling time windows.
- built a data-quality Kafka Consumer that pushes data into PostgreSQL in batches, ensuring no data is lost even during error.

---

## Project Overview

This project detects trending Wikipedia articles and topics in real time by ingesting Wikipedia's Server-Side Events (SSE) stream, processing edits through a Kafka pipeline, aggregating them into a PostgreSQL database, and displaying results through a REST API backend and an interactive dashboard.

This pipeline is always running, as the producer maintains a constant connection with the SSE stream, the consumer continuously writes to Postgres, and the aggregation layer refreshes trending results every 2 minutes. Different from a typical static analytics project.

The project focuses on the full data engineering lifecycle: stream ingestion, message brokering, batched storage, time-windowed aggregation, API serving, and frontend visualization. This is all running locally via Docker Compose.

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