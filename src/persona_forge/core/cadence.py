"""Cadence planner.

Produces a posting schedule for a persona given a config (posts/day, active
hours, jitter). Used by the scheduler handler and by the renderer to stamp
posts with a plausible publish time.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from persona_forge.config.schema import ForgeConfig
from persona_forge.models.persona import CadencePlan


@dataclass(slots=True)
class CadencePlanner:
    config: ForgeConfig
    rng: random.Random = random.Random(0xC0FFEE)

    def default_plan(self) -> CadencePlan:
        return CadencePlan(
            posts_per_day=self.config.default_posts_per_day,
            active_hours=(9, 22),
            jitter_minutes=45,
            timezone=self.config.default_timezone,
        )

    def next_slots(self, plan: CadencePlan, *, start: datetime, count: int) -> list[datetime]:
        slots: list[datetime] = []
        lo, hi = plan.active_hours
        span = (hi - lo) * 60
        for _ in range(count):
            minute = self.rng.randint(0, span)
            jitter = self.rng.randint(-plan.jitter_minutes, plan.jitter_minutes)
            dt = start.replace(hour=lo, minute=0, second=0, microsecond=0) + timedelta(
                minutes=minute + jitter
            )
            slots.append(dt)
        return sorted(slots)