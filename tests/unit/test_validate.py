"""Unit tests for the .ai/ folder convention linter."""
from pathlib import Path


def _scaffold(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(path=tmp_path)


def test_valid_minimal_folder_passes(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    _scaffold(tmp_path)
    result = validate_ai_folder(tmp_path)
    assert result.passed
    assert result.errors == []


def test_missing_ai_folder_reports_error(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    result = validate_ai_folder(tmp_path)
    assert not result.passed
    assert any(".ai/" in e.file for e in result.errors)


def test_broken_memory_link_reports_error(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    _scaffold(tmp_path)
    memory_md = tmp_path / ".ai" / "memory" / "MEMORY.md"
    memory_md.write_text("# Memory\n\n- [Architecture](architecture.md) — system design\n")
    result = validate_ai_folder(tmp_path)
    assert not result.passed
    assert any("architecture.md" in e.message for e in result.errors)


def test_valid_memory_link_passes(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    _scaffold(tmp_path)
    arch = tmp_path / ".ai" / "memory" / "architecture.md"
    # Must include all required sections to pass full validation
    arch.write_text(
        "# Architecture\n\n## Overview\n\nOverview.\n\n"
        "## Key Services\n\nServices.\n\n"
        "## Data Flow\n\nFlow.\n\n"
        "## Dependencies\n\nDeps.\n"
    )
    memory_md = tmp_path / ".ai" / "memory" / "MEMORY.md"
    memory_md.write_text("# Memory\n\n- [Architecture](architecture.md) — system design\n")
    result = validate_ai_folder(tmp_path)
    assert result.passed


def test_skill_missing_frontmatter_reports_error(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    _scaffold(tmp_path)
    skill = tmp_path / ".ai" / "skills" / "my-skill.md"
    skill.write_text("# My Skill\n\nNo frontmatter here.\n")
    result = validate_ai_folder(tmp_path)
    assert not result.passed
    assert any("my-skill.md" in e.file for e in result.errors)


def test_skill_with_valid_frontmatter_passes(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    _scaffold(tmp_path)
    skill = tmp_path / ".ai" / "skills" / "my-skill.md"
    skill.write_text("---\nname: my-skill\ndescription: Does a thing\n---\n\n# My Skill\n")
    result = validate_ai_folder(tmp_path)
    assert result.passed


def test_skill_missing_name_field_reports_error(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    _scaffold(tmp_path)
    skill = tmp_path / ".ai" / "skills" / "bad.md"
    skill.write_text("---\ndescription: Missing name\n---\n\n# Bad Skill\n")
    result = validate_ai_folder(tmp_path)
    assert not result.passed
    assert any("name" in e.message for e in result.errors)


def test_architecture_missing_key_services_reports_error(tmp_path: Path) -> None:
    from ai_context.validator import validate_ai_folder

    _scaffold(tmp_path)
    arch = tmp_path / ".ai" / "memory" / "architecture.md"
    arch.write_text(
        "# Architecture\n\n## Overview\n\nSome overview.\n\n## Data Flow\n\n## Dependencies\n"
    )
    result = validate_ai_folder(tmp_path)
    assert not result.passed
    assert any("Key Services" in e.message for e in result.errors)


def test_validate_false_positive_rate_zero_on_full_template(tmp_path: Path) -> None:
    """Valid folder with full template must report zero errors."""
    from ai_context.commands.init import run_init
    from ai_context.validator import validate_ai_folder

    run_init(template="full", path=tmp_path)
    result = validate_ai_folder(tmp_path)
    assert result.passed, f"Got unexpected errors: {result.errors}"
