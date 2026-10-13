"""Typer entrypoint for the persona-forge desktop tool.

Commands map 1:1 to the desktop utility's task bar: doctor, new, train,
render, export, schedule. Long-running work is dispatched to the core
engine; the CLI stays a thin shell.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer
from rich.console import Console

from persona_forge import __version__
from persona_forge.bootstrap import doctor as doctor_mod
from persona_forge.core.engine import ForgeEngine
from persona_forge.core.errors import ForgeError
from persona_forge.utils.log import configure_logging

app = typer.Typer(
    name="persona-forge",
    help="Generate and manage synthetic AI influencer personas.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
log = logging.getLogger("persona_forge.cli")

CONFIG_DEFAULT = Path("config/local.toml")


def _engine(config_path: Path) -> ForgeEngine:
    if not config_path.exists():
        raise ForgeError(f"config not found: {config_path}. run `persona-forge doctor` first.")
    return ForgeEngine.from_config(config_path)


@app.command()
def version() -> None:
    """Print the forge version."""
    console.print(f"synthetic-persona-forge {__version__}")


@app.command()
def doctor(
    config_path: Path = typer.Option(CONFIG_DEFAULT, "--config", "-c"),
    fix: bool = typer.Option(False, "--fix", help="Write a starter config if missing."),
) -> None:
    """Check Python, sidecars, backends, and config. `--fix` scaffolds config."""
    report = doctor_mod.run(config_path=config_path, fix=fix)
    console.print(report.render())
    if not report.ok:
        raise typer.Exit(code=1)


@app.command("new")
def new_persona(
    handle: str = typer.Argument(..., help="Persona handle, e.g. @nova.quinn"),
    niche: str = typer.Option("lifestyle", "--niche", "-n"),
    config_path: Path = typer.Option(CONFIG_DEFAULT, "--config", "-c"),
) -> None:
    """Scaffold a new persona directory and identity manifest."""
    engine = _engine(config_path)
    persona = engine.create_persona(handle=handle, niche=niche)
    console.print(f"[green]created[/] {persona.slug} at {persona.root}")


@app.command()
def train(
    slug: str = typer.Argument(..., help="Persona slug."),
    stage: str = typer.Option("voice", "--stage", help="voice | face | style"),
    config_path: Path = typer.Option(CONFIG_DEFAULT, "--config", "-c"),
) -> None:
    """Run a training stage for a persona."""
    engine = _engine(config_path)
    engine.train_stage(slug=slug, stage=stage)
    console.print(f"[green]trained[/] {stage} for {slug}")


@app.command()
def render(
    slug: str,
    count: int = typer.Option(1, "--count", "-k"),
    config_path: Path = typer.Option(CONFIG_DEFAULT, "--config", "-c"),
) -> None:
    """Render N posts (image + caption + voice) into the persona's queue."""
    engine = _engine(config_path)
    engine.render_posts(slug=slug, count=count)
    console.print(f"[green]rendered[/] {count} post(s) for {slug}")


@app.command()
def export(
    slug: str,
    platform: str = typer.Option("instagram", "--platform", "-p"),
    config_path: Path = typer.Option(CONFIG_DEFAULT, "--config", "-c"),
) -> None:
    """Export a persona's queue into a platform-ready bundle."""
    engine = _engine(config_path)
    out = engine.export_bundle(slug=slug, platform=platform)
    console.print(f"[green]exported[/] {platform} bundle -> {out}")


def main() -> None:
    configure_logging()
    try:
        app()
    except ForgeError as exc:
        log.error("forge error: %s", exc)
        console.print(f"[red]error:[/] {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()