"""Unit tests for prompt building and Claude tool schema definitions."""

from pathlib import Path


def test_prompt_contains_file_contents(tmp_path: Path) -> None:
    from ai_context.generator import build_context_prompt

    files = [(tmp_path / "main.py", "def hello(): pass\n")]
    prompt = build_context_prompt(files, tmp_path)
    assert "def hello(): pass" in prompt


def test_prompt_contains_relative_path(tmp_path: Path) -> None:
    from ai_context.generator import build_context_prompt

    subdir = tmp_path / "src"
    subdir.mkdir()
    files = [(subdir / "app.py", "# app content\n")]
    prompt = build_context_prompt(files, tmp_path)
    assert "src/app.py" in prompt
    assert str(tmp_path) not in prompt


def test_prompt_contains_separator(tmp_path: Path) -> None:
    from ai_context.generator import build_context_prompt

    files = [
        (tmp_path / "a.py", "# a"),
        (tmp_path / "b.py", "# b"),
    ]
    prompt = build_context_prompt(files, tmp_path)
    assert "---" in prompt


def test_architecture_tool_has_required_fields() -> None:
    from ai_context.generator import ARCHITECTURE_TOOL

    schema = ARCHITECTURE_TOOL["input_schema"]
    assert "overview" in schema["properties"]
    assert "key_services" in schema["properties"]
    assert "data_flow" in schema["properties"]
    assert "dependencies" in schema["properties"]
    assert set(schema["required"]) == {"overview", "key_services", "data_flow", "dependencies"}


def test_conventions_tool_has_required_keys() -> None:
    from ai_context.generator import CONVENTIONS_TOOL

    schema = CONVENTIONS_TOOL["input_schema"]
    assert "logging" in schema["properties"]
    assert "model_validation" in schema["properties"]
    assert "test_structure" in schema["properties"]


def test_prompt_empty_files_returns_header() -> None:
    from ai_context.generator import build_context_prompt

    prompt = build_context_prompt([], Path("/any"))
    assert "repository" in prompt.lower()


def test_architecture_doc_from_tool_output() -> None:
    from ai_context.generator import _parse_architecture_output
    from ai_context.schema import ArchitectureDoc

    raw: dict = {
        "overview": "A Kafka consumer service.",
        "key_services": [
            {"name": "Consumer", "description": "Reads from Kafka", "technology": "Python"}
        ],
        "data_flow": [
            {"source": "Kafka", "sink": "Elasticsearch", "description": "streams events"}
        ],
        "dependencies": ["kafka-python", "elasticsearch-py"],
    }
    doc = _parse_architecture_output(raw)
    assert isinstance(doc, ArchitectureDoc)
    assert doc.key_services[0].name == "Consumer"
    assert doc.dependencies == ["kafka-python", "elasticsearch-py"]
