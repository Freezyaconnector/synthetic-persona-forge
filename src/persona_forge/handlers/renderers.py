"""Post renderer.

Given a persona, produces a batch of candidate posts: caption text (from the
LLM backend), a face image (from the face backend), and a voice clip (from
the voice backend). Posts land in the persona's `queue/` directory as
JSON+PNG+WAV triples.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from persona_forge.config.schema import ForgeConfig
from persona_forge.core.cadence import CadencePlanner
from persona_forge.models.persona import Persona, Post
from persona_forge.services.backends import get_backend

log = logging.getLogger(__name__)


class PostRenderer:
    def __init__(self, config: ForgeConfig) -> None:
        self.config = config
        self.cadence = CadencePlanner(config)
        self.llm = get_backend(config, "llm")
        self.face = get_backend(config, "face")
        self.voice = get_backend(config, "voice")

    def render_batch(self, persona: Persona, *, count: int) -> list[Post]:
        plan = persona.manifest.cadence
        slots = self.cadence.next_slots(
            plan, start=datetime.now(timezone.utc), count=count
        )
        out: list[Post] = []
        for slot in slots:
            caption = self.llm.generate_caption(persona, slot)
            image_path = self.face.render_image(persona, slot, out_dir=persona.root / "queue")
            voice_path = self.voice.render_clip(persona, caption, out_dir=persona.root / "queue")
            post = Post(
                id=f"{persona.slug}-{slot:%Y%m%d%H%M}",
                scheduled_at=slot,
                caption=caption,
                image_path=str(image_path),
                voice_path=str(voice_path) if voice_path else None,
                platform=persona.manifest.primary_platform,
            )
            self._write(persona, post)
            out.append(post)
        log.info("rendered %d post(s) for %s", len(out), persona.slug)
        return out

    @staticmethod
    def _write(persona: Persona, post: Post) -> None:
        path = persona.root / "queue" / f"{post.id}.json"
        path.write_text(json.dumps(post.to_dict(), indent=2), encoding="utf-8")