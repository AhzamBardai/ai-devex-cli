"""Entry point for the ai-context CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(
    name="ai-context",
    help="Scaffold and manage .ai/ context for AI coding agents.",
    add_completion=False,
)

console = Console()


@app.command("init")
def init(
    template: str = typer.Option("minimal", help="Scaffold size: minimal, full, or team"),
    no_agents_md: bool = typer.Option(False, "--no-agents-md", help="Skip creating AGENTS.md"),
) -> None:
    """Scaffold .ai/ folder structure in the current repo."""
    from ai_context.commands.init import run_init

    valid_templates = ("minimal", "full", "team")
    if template not in valid_templates:
        console.print(
            f"[red]Invalid template '{template}'. Choose from: {', '.join(valid_templates)}[/red]"
        )
        raise typer.Exit(1)

    created = run_init(
        template=template,  # type: ignore[arg-type]
        no_agents_md=no_agents_md,
        path=Path("."),
    )

    if not created:
        console.print("[yellow]Nothing to do — .ai/ already initialized.[/yellow]")
    else:
        for f in created:
            console.print(f"[green]✓[/green] Created {f}")
        console.print(
            "\nNext: run [bold]ai-context generate[/bold] to let AI analyze your repo "
            "and fill in context."
        )


@app.command("generate")
def generate(
    model: str = typer.Option("haiku", help="Model: haiku (cost) or sonnet (quality)"),
    focus: str = typer.Option(
        "all", help="What to generate: architecture, conventions, skills, or all"
    ),
    max_tokens: int = typer.Option(4000, help="Max tokens from repo to send to LLM"),
) -> None:
    """AI-powered: analyze repo and generate .ai/ context files."""
    from ai_context.commands.generate import run_generate, write_output

    valid_models = ("haiku", "sonnet")
    valid_focus = ("architecture", "conventions", "skills", "all")

    if model not in valid_models:
        console.print(f"[red]Invalid model '{model}'. Choose: {', '.join(valid_models)}[/red]")
        raise typer.Exit(1)
    if focus not in valid_focus:
        console.print(f"[red]Invalid focus '{focus}'. Choose: {', '.join(valid_focus)}[/red]")
        raise typer.Exit(1)

    root = Path(".")
    console.print("Analyzing repo...")

    try:
        output = run_generate(
            path=root,
            model=model,  # type: ignore[arg-type]
            focus=focus,  # type: ignore[arg-type]
            max_tokens=max_tokens,
        )
    except OSError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1) from None

    written = write_output(output, root)

    console.print("\n[green]Generated:[/green]")
    for f in written:
        content = (root / f).read_text()
        tokens = len(content) // 4
        console.print(f"  {f}  ({tokens} tokens)")

    console.print(
        "\nReview and edit before committing. Run [bold]ai-context validate[/bold] to check."
    )


@app.command("validate")
def validate(
    path: str = typer.Option(".", help="Root directory containing .ai/"),
) -> None:
    """Lint .ai/ folder against the convention schema."""
    from ai_context.commands.validate import run_validate

    result = run_validate(Path(path))

    for err in result.errors:
        console.print(f"[red]✗[/red] {err.file} — {err.message}")
        if err.suggestion:
            console.print(f"  [dim]→ {err.suggestion}[/dim]")
    for warn in result.warnings:
        console.print(f"[yellow]⚠[/yellow] {warn.file} — {warn.message}")

    total_errors = len(result.errors)
    total_warnings = len(result.warnings)

    if result.passed:
        console.print("[green]✓[/green] Validation passed.")
    else:
        console.print(f"\n[red]{total_errors} error(s), {total_warnings} warning(s)[/red]")
        raise typer.Exit(1)


@app.command("diff")
def diff(
    path: str = typer.Option(".", help="Root directory"),
) -> None:
    """Show what changed in .ai/ context since last git commit."""
    from ai_context.commands.diff import print_diff, run_diff

    result = run_diff(Path(path))
    print_diff(result, console)


@app.command("stats")
def stats(
    path: str = typer.Option(".", help="Root directory"),
) -> None:
    """Report .ai/ context usage statistics."""
    from ai_context.commands.stats import print_stats, run_stats

    data = run_stats(Path(path))
    print_stats(data, console)


if __name__ == "__main__":
    app()
