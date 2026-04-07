"""Unit tests for the diff command — git-based .ai/ change detection."""
import subprocess
from pathlib import Path


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=path, capture_output=True
    )
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, capture_output=True)


def _git_commit_all(path: Path, msg: str = "init") -> None:
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=path, capture_output=True)


def test_diff_no_changes_returns_empty(tmp_path: Path) -> None:
    from ai_context.commands.diff import run_diff
    from ai_context.commands.init import run_init

    _git_init(tmp_path)
    run_init(path=tmp_path)
    _git_commit_all(tmp_path)

    result = run_diff(tmp_path)
    assert not result.has_changes


def test_diff_detects_modification(tmp_path: Path) -> None:
    from ai_context.commands.diff import run_diff
    from ai_context.commands.init import run_init

    _git_init(tmp_path)
    run_init(path=tmp_path)
    _git_commit_all(tmp_path)

    memory_md = tmp_path / ".ai" / "memory" / "MEMORY.md"
    memory_md.write_text("# Modified Memory\n\nNew content.\n")

    result = run_diff(tmp_path)
    assert result.has_changes


def test_diff_detects_stale_context_from_new_file(tmp_path: Path) -> None:
    from ai_context.commands.diff import run_diff
    from ai_context.commands.init import run_init

    _git_init(tmp_path)
    run_init(path=tmp_path)
    arch = tmp_path / ".ai" / "memory" / "architecture.md"
    arch.write_text(
        "# Architecture\n\n## Overview\nOrderService handles orders.\n"
        "## Key Services\n## Data Flow\n## Dependencies\n"
    )
    _git_commit_all(tmp_path)

    notifier = tmp_path / "notifier.py"
    notifier.write_text("class NotifierService:\n    pass\n")
    subprocess.run(["git", "add", "notifier.py"], cwd=tmp_path, capture_output=True)

    result = run_diff(tmp_path)
    assert any("notifier.py" in h.new_file for h in result.stale_hints)


def test_diff_no_stale_when_service_mentioned(tmp_path: Path) -> None:
    from ai_context.commands.diff import run_diff
    from ai_context.commands.init import run_init

    _git_init(tmp_path)
    run_init(path=tmp_path)
    arch = tmp_path / ".ai" / "memory" / "architecture.md"
    arch.write_text(
        "# Architecture\n\n## Overview\nNotifierService sends emails.\n"
        "## Key Services\nnotifier\n## Data Flow\n## Dependencies\n"
    )
    _git_commit_all(tmp_path)

    notifier = tmp_path / "notifier.py"
    notifier.write_text("class NotifierService:\n    pass\n")
    subprocess.run(["git", "add", "notifier.py"], cwd=tmp_path, capture_output=True)

    result = run_diff(tmp_path)
    stale_files = [h.new_file for h in result.stale_hints]
    assert "notifier.py" not in stale_files


def test_diff_returns_empty_when_no_git_repo(tmp_path: Path) -> None:
    from ai_context.commands.diff import run_diff

    result = run_diff(tmp_path)
    assert not result.has_changes


def test_diff_returns_empty_when_no_ai_folder(tmp_path: Path) -> None:
    from ai_context.commands.diff import run_diff

    _git_init(tmp_path)
    result = run_diff(tmp_path)
    assert not result.has_changes
