# Contributing to synthetic-persona-forge

Thanks for wanting to push the forge forward. This repo is a Windows desktop
tool that generates and manages synthetic AI influencers — persona identity,
voice, face, posting cadence, and platform-ready asset bundles.

## Dev environment

- Python 3.11 or 3.12 (3.12 recommended; 3.13 not yet supported by `onnxruntime`)
- Windows 10/11 x64. Linux/macOS work for the CLI layer only.
- Optional sidecars: MSVC 2022 (C++), .NET 8 SDK (C#), JDK 21 (Java) — only
  needed if you touch `native/`, `dotnet/`, or `java/`.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m persona_forge doctor
```

## Branch + commit style

- Branch: `feat/<area>-<short>`, `fix/<area>-<short>`, `chore/<short>`
- Commits: conventional commits (`feat(voice): add elevenlabs adapter`)
- One logical change per PR. Keep diffs reviewable.

## What we want

- New `PersonaTrait` subclasses (see `src/persona_forge/core/traits.py`)
- New platform exporters under `src/persona_forge/handlers/exporters/`
- Voice/face backend adapters under `src/persona_forge/services/backends/`
- Tests. If you add a handler, add a fixture persona and a golden test.

## What will get your PR closed

- Hardcoded API keys, cookies, or session tokens
- Personas that impersonate a real, identifiable living person
- Anything that scrapes a platform in violation of its ToS without a proxy
  pool and rate-limit config
- Generated content targeting minors. This is a hard line.

## Style

- `ruff` + `black` (line length 100). Run `make lint` before pushing.
- Type hints on every public function. `mypy --strict` on `src/persona_forge/core`.
- No `print()` in library code — use the logger from `persona_forge.utils.log`.

## Tests

```powershell
pytest -q
pytest -q tests/test_persona_pipeline.py -k cadence
```