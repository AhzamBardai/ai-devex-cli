"""Validate command: lint the .ai/ folder against the convention schema."""

from __future__ import annotations

from pathlib import Path

from ai_context.schema import ValidationResult
from ai_context.validator import validate_ai_folder


def run_validate(path: Path = Path(".")) -> ValidationResult:
    """Run validation and return result.

    Args:
        path: Root directory containing .ai/

    Returns:
        ValidationResult with errors and warnings.
    """
    return validate_ai_folder(path)
