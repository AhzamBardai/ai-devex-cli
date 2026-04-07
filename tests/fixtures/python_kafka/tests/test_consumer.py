"""Tests for the Kafka consumer message processing."""
import pytest
from consumer import process_message


def test_process_valid_message() -> None:
    raw = '{"order_id": "ord_123", "customer_id": "cust_456", "total_usd": 99.99, "status": "placed"}'
    event = process_message(raw)
    assert event.order_id == "ord_123"
    assert event.status == "placed"


def test_process_invalid_message_raises() -> None:
    with pytest.raises(Exception):
        process_message('{"bad": "data"}')
