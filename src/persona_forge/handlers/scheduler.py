"""Cadence scheduler.

Reads a persona's queue, drops posts whose scheduled_at has passed, and
emits an ordered publish list. Does not perform the actual publish — that
is out of scope for the forge (see SECURITY.md).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from persona_forge.models.persona import Persona, Post
from persona_forge.utils.log import get_logger

log = get_logger(__name__)


def due_posts(persona: Persona, *, now: datetime | None = None) -> list[Post]:
    now = now or datetime.now(timezone.utc)
    queue = persona.root / "queue"
    due: list[Post] = []
    for path in sorted(queue.glob("*.json")):
        post = Post.from_dict(json.loads(path.read_text("utf-8")))
        if post.scheduled_at <= now:
            due.append(post)
    log.info("%s: %d due of %d", persona.slug, len(due), len(list(queue.glob("*.json"))))
    return due


def write_publish_list(persona: Persona, out: Path) -> Path:
    due = due_posts(persona)
    out.write_text(
        json.dumps([p.to_dict() for p in due], indent=2), encoding="utf-8"
    )
    return out