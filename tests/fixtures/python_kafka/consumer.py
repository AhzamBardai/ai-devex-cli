"""Kafka consumer: reads from 'orders' topic and writes enriched records to Elasticsearch."""
from __future__ import annotations

import json

import structlog
from pydantic import BaseModel

log = structlog.get_logger()


class OrderEvent(BaseModel):
    order_id: str
    customer_id: str
    total_usd: float
    status: str


def create_consumer(bootstrap_servers: str, topic: str) -> object:
    """Create a Kafka consumer connected to the given bootstrap servers."""
    from kafka import KafkaConsumer  # type: ignore[import]

    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda m: m.decode("utf-8"),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="order-enricher",
    )


def process_message(raw: str) -> OrderEvent:
    """Deserialize and validate an incoming Kafka message."""
    data = json.loads(raw)
    event = OrderEvent.model_validate(data)
    log.info("order_received", order_id=event.order_id, status=event.status)
    return event
