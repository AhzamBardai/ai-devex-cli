"""Unit tests for the CLI commands via Typer test client."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ai_context.main import app

runner = CliRunner()


# ── init command ──────────────────────────────────────────────────────────────

def test_cli_init_success(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init"], catch_exceptions=False)
    # Runner uses current dir; just verify it doesn't crash with bad template
    assert result.exit_code == 0 or "Created" in result.output or "initialized" in result.output


def test_cli_init_invalid_template() -> None:
    result = runner.invoke(app, ["init", "--template", "invalid"])
    assert result.exit_code == 1
    assert "Invalid template" in result.output


def test_cli_init_already_initialized(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(app, ["init"])
        result = runner.invoke(app, ["init"])
        assert "Nothing to do" in result.output


# ── validate command ──────────────────────────────────────────────────────────

def test_cli_validate_passes_on_valid_folder(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(app, ["init"])
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0
        assert "Validation passed" in result.output


def test_cli_validate_fails_on_missing_folder(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 1
        assert ".ai/" in result.output


def test_cli_validate_shows_suggestion(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["validate"])
        assert "→" in result.output or "suggestion" in result.output.lower() or "init" in result.output


# ── diff command ──────────────────────────────────────────────────────────────

def test_cli_diff_no_git_repo(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(app, ["init"])
        result = runner.invoke(app, ["diff"])
        assert result.exit_code == 0


# ── stats command ─────────────────────────────────────────────────────────────

def test_cli_stats_shows_table(tmp_path: Path) -> None:
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(app, ["init"])
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "Memory files" in result.output


# ── generate command ──────────────────────────────────────────────────────────

def test_cli_generate_invalid_model() -> None:
    result = runner.invoke(app, ["generate", "--model", "gpt4"])
    assert result.exit_code == 1
    assert "Invalid model" in result.output


def test_cli_generate_invalid_focus() -> None:
    result = runner.invoke(app, ["generate", "--focus", "everything"])
    assert result.exit_code == 1
    assert "Invalid focus" in result.output


def test_cli_generate_missing_api_key(tmp_path: Path) -> None:
    import os

    with runner.isolated_filesystem(temp_dir=tmp_path):
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict("os.environ", env, clear=True):
            result = runner.invoke(app, ["generate"])
            assert result.exit_code == 1
            assert "ANTHROPIC_API_KEY" in result.output
