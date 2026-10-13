"""Backend protocol.

Every backend implements train() and one of the render_* methods depending
on its stage. Backends are stateless w.r.t. the persona; all state lives in
the persona directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from persona_forge.config.schema import BackendConfig
from persona_forge.models.persona import Persona


@runtime_checkable
class Backend(Protocol):
    name: str
    stage: str

    def __init__(self, config: BackendConfig) -> None: ...

    def train(self, persona: Persona) -> None: ...

    def generate_caption(self, persona: Persona, when: object) -> str: ...

    def render_image(self, persona: Persona, when: object, *, out_dir: Path) -> Path: ...

    def render_clip(self, persona: Persona, text: str, *, out_dir: Path) -> Path | None: ...