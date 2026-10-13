"""ForgeEngine — the core pipeline for persona creation, training, render, export.

The engine is intentionally synchronous and file-backed: each persona lives
in `personas/<slug>/` with a manifest, trait set, and asset queue. Long
stages (voice clone, face LoRA) delegate to the backend adapters and write
artifacts back into the persona directory.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from persona_forge.config.schema import ForgeConfig
from persona_forge.core.cadence import CadencePlanner
from persona_forge.core.errors import PersonaError
from persona_forge.core.traits import TraitSet, default_traits_for_niche
from persona_forge.handlers.exporters import get_exporter
from persona_forge.handlers.renderers import PostRenderer
from persona_forge.models.persona import Persona, PersonaManifest
from persona_forge.services.backends import get_backend
from persona_forge.utils.slug import to_slug

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ForgeEngine:
    config: ForgeConfig
    personas_root: Path

    @classmethod
    def from_config(cls, config_path: Path) -> "ForgeEngine":
        cfg = ForgeConfig.from_toml(config_path.read_text(encoding="utf-8"))
        root = Path(cfg.personas_root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        return cls(config=cfg, personas_root=root)

    def _persona_dir(self, slug: str) -> Path:
        d = self.personas_root / slug
        if not d.exists():
            raise PersonaError(f"no persona at {d}")
        return d

    def create_persona(self, handle: str, niche: str) -> Persona:
        slug = to_slug(handle)
        root = self.personas_root / slug
        if root.exists():
            raise PersonaError(f"persona already exists: {slug}")
        root.mkdir(parents=True)
        (root / "queue").mkdir()

        traits: TraitSet = default_traits_for_niche(niche)
        manifest = PersonaManifest(
            handle=handle,
            slug=slug,
            niche=niche,
            traits=traits,
            cadence=CadencePlanner.from_config(self.config).default_plan(),
        )
        (root / "manifest.json").write_text(
            json.dumps(manifest.to_dict(), indent=2), encoding="utf-8"
        )
        log.info("created persona %s (%s)", slug, niche)
        return Persona(manifest=manifest, root=root)

    def load_persona(self, slug: str) -> Persona:
        root = self._persona_dir(slug)
        manifest = PersonaManifest.from_dict(json.loads((root / "manifest.json").read_text("utf-8")))
        return Persona(manifest=manifest, root=root)

    def train_stage(self, slug: str, stage: str) -> None:
        persona = self.load_persona(slug)
        backend = get_backend(self.config, stage)
        backend.train(persona)

    def render_posts(self, slug: str, count: int) -> None:
        persona = self.load_persona(slug)
        renderer = PostRenderer(config=self.config)
        renderer.render_batch(persona, count=count)

    def export_bundle(self, slug: str, platform: str) -> Path:
        persona = self.load_persona(slug)
        exporter = get_exporter(platform)
        return exporter.export(persona, out_dir=persona.root / "exports" / platform)