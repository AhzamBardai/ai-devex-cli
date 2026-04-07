"""Configuration loaded from environment variables."""
from __future__ import annotations

import os


def get_kafka_bootstrap() -> str:
    return os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")


def get_es_url() -> str:
    return os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")


def get_topic() -> str:
    return os.environ.get("KAFKA_TOPIC", "orders")
