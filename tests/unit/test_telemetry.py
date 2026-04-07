"""Unit tests for the telemetry opt-in stub."""

from unittest.mock import patch


def test_telemetry_disabled_by_default() -> None:
    from ai_context.telemetry import is_enabled

    with patch.dict("os.environ", {}, clear=True):
        assert not is_enabled()


def test_telemetry_enabled_when_env_set() -> None:
    from ai_context.telemetry import is_enabled

    with patch.dict("os.environ", {"AI_CONTEXT_TELEMETRY": "1"}):
        assert is_enabled()


def test_trace_command_noop_when_disabled() -> None:
    from ai_context.telemetry import trace_command

    with patch.dict("os.environ", {}, clear=True):
        with trace_command("test"):
            pass  # must not raise


def test_trace_command_yields_when_enabled() -> None:
    from ai_context.telemetry import trace_command

    with patch.dict("os.environ", {"AI_CONTEXT_TELEMETRY": "1"}):
        # Will fall through to the ImportError path since OTEL TracerProvider may not be
        # fully configured — ensure it yields without crashing
        with trace_command("test"):
            pass  # must not raise
