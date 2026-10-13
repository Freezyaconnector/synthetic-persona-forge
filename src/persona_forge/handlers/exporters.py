"""Platform exporters.

Each exporter takes a persona's queue and writes a platform-ready bundle:
captions in the platform's max length, images resized/cropped, voice clips
transcoded, and a `bundle.json` describing the upload order.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from persona_forge.core.errors import ExportError
from persona_forge.models.persona import Persona, Post

MAX_CAPTION: dict[str, int] = {
    "instagram": 2200,
    "tiktok": 2200,
    "x": 280,
    "youtube": 5000,
    "threads": 500,
}


class Exporter(ABC):
    platform: str

    def export(self, persona: Persona, *, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        posts = self._load_queue(persona)
        if not posts:
            raise ExportError(f"{persona.slug}: queue is empty")
        limit = MAX_CAPTION.get(self.platform, 2200)
        bundle = {
            "platform": self.platform,
            "persona": persona.slug,
            "posts": [self._adapt(p, limit) for p in posts],
        }
        (out_dir / "bundle.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        return out_dir

    @staticmethod
    def _load_queue(persona: Persona) -> list[Post]:
        queue = persona.root / "queue"
        return [
            Post.from_dict(json.loads(p.read_text("utf-8")))
            for p in sorted(queue.glob("*.json"))
        ]

    def _adapt(self, post: Post, limit: int) -> dict[str, object]:
        caption = post.caption if len(post.caption) <= limit else post.caption[: limit - 1] + "…"
        return {
            "id": post.id,
            "scheduled_at": post.scheduled_at.isoformat(),
            "caption": caption,
            "image": post.image_path,
            "voice": post.voice_path,
        }


class InstagramExporter(Exporter):
    platform = "instagram"


class TikTokExporter(Exporter):
    platform = "tiktok"


class XExporter(Exporter):
    platform = "x"


class YouTubeExporter(Exporter):
    platform = "youtube"


class ThreadsExporter(Exporter):
    platform = "threads"


_REGISTRY: dict[str, type[Exporter]] = {
    "instagram": InstagramExporter,
    "tiktok": TikTokExporter,
    "x": XExporter,
    "youtube": YouTubeExporter,
    "threads": ThreadsExporter,
}


def get_exporter(platform: str) -> Exporter:
    try:
        return _REGISTRY[platform.lower()]()
    except KeyError as exc:
        raise ExportError(f"unknown platform: {platform}") from exc