"""Domain models for the order enrichment pipeline."""
from __future__ import annotations

from pydantic import BaseModel, Field


class OrderEvent(BaseModel):
    order_id: str
    customer_id: str
    total_usd: float
    status: str


class EnrichedOrder(BaseModel):
    order_id: str
    customer_id: str
    total_usd: float
    status: str
    margin_pct: float = Field(ge=0.0, le=1.0)
    enriched: bool = True
