"""Unit tests for FileSelector — token-budget file selection."""
from pathlib import Path


def test_selects_readme_first(tmp_path: Path) -> None:
    from ai_context.generator import FileSelector, estimate_tokens

    (tmp_path / "README.md").write_text("# Project\n" * 20)
    (tmp_path / "other.py").write_text("x = 1\n" * 20)
    selector = FileSelector(tmp_path, max_tokens=10000)
    selected = selector.select()
    assert selected[0][0].name == "README.md"


def test_respects_token_budget(tmp_path: Path) -> None:
    from ai_context.generator import FileSelector, estimate_tokens

    for i in range(20):
        (tmp_path / f"file{i}.py").write_text("x = 1\n" * 200)
    selector = FileSelector(tmp_path, max_tokens=100)
    selected = selector.select()
    total_tokens = sum(estimate_tokens(content) for _, content in selected)
    assert total_tokens <= 120  # slight margin for truncation


def test_respects_gitignore(tmp_path: Path) -> None:
    from ai_context.generator import FileSelector

    (tmp_path / ".gitignore").write_text("ignored.py\n")
    (tmp_path / "ignored.py").write_text("secret = 'hidden'\n")
    (tmp_path / "main.py").write_text("# main\n")
    selector = FileSelector(tmp_path, max_tokens=10000)
    selected = selector.select()
    names = [p.name for p, _ in selected]
    assert "ignored.py" not in names
    assert "main.py" in names


def test_skips_git_directory(tmp_path: Path) -> None:
    from ai_context.generator import FileSelector

    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n")
    (tmp_path / "main.py").write_text("# main\n")
    selector = FileSelector(tmp_path, max_tokens=10000)
    selected = selector.select()
    paths_str = [str(p) for p, _ in selected]
    assert not any(".git" in p for p in paths_str)


def test_skips_venv_directory(tmp_path: Path) -> None:
    from ai_context.generator import FileSelector

    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "activate").write_text("# activate\n")
    (tmp_path / "app.py").write_text("# app\n")
    selector = FileSelector(tmp_path, max_tokens=10000)
    selected = selector.select()
    paths_str = [str(p) for p, _ in selected]
    assert not any(".venv" in p for p in paths_str)


def test_pyproject_toml_has_high_priority(tmp_path: Path) -> None:
    from ai_context.generator import FileSelector

    (tmp_path / "a_utility.py").write_text("def util(): pass\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    selector = FileSelector(tmp_path, max_tokens=10000)
    selected = selector.select()
    names = [p.name for p, _ in selected]
    assert names.index("pyproject.toml") < names.index("a_utility.py")


def test_estimate_tokens_approximation() -> None:
    from ai_context.generator import estimate_tokens

    text = "x" * 400
    assert estimate_tokens(text) == 100


def test_select_returns_empty_for_empty_dir(tmp_path: Path) -> None:
    from ai_context.generator import FileSelector

    selector = FileSelector(tmp_path, max_tokens=1000)
    selected = selector.select()
    assert selected == []
