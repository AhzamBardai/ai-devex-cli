"""Opt-in OpenTelemetry usage telemetry.

Set AI_CONTEXT_TELEMETRY=1 and OTEL_EXPORTER_OTLP_ENDPOINT to enable.
No telemetry is collected by default. This module is a no-op unless opted in.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator


def is_enabled() -> bool:
    """Return True if telemetry has been opted in via environment variable."""
    return os.environ.get("AI_CONTEXT_TELEMETRY", "0") == "1"


@contextmanager
def trace_command(command: str) -> Generator[None, None, None]:
    """Context manager that records command execution as an OTEL span when enabled.

    Args:
        command: Name of the CLI command being executed.
    """
    if not is_enabled():
        yield
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider

        provider = TracerProvider()
        tracer = provider.get_tracer("ai-context")
        with tracer.start_as_current_span(f"ai_context.{command}"):
            yield
    except ImportError:
        yield
