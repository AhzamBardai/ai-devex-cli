# Kafka Consumer Service

A Python service that consumes events from Kafka and writes enriched records to Elasticsearch.

## Architecture

- **Consumer**: Reads from `orders` Kafka topic using kafka-python
- **Enricher**: Calls external pricing API to add margin data
- **Sink**: Writes to Elasticsearch `orders-enriched` index

## Tech Stack

Python 3.11, kafka-python, elasticsearch-py, pydantic, structlog, pytest
