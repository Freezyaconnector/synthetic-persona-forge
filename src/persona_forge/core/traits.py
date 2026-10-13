"""Persona trait system.

A TraitSet is the identity DNA of a persona: voice profile, style profile,
personality axes, and content guardrails. Traits are serializable and
composable; niches provide sane defaults that users override in the
manifest.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from persona_forge.core.errors import PersonaError


@dataclass(slots=True)
class VoiceProfile:
    pitch: float = 0.0            # semitones, -12..+12
    pace: float = 1.0             # length-scale, 0.7..1.4
    warmth: float = 0.5           # 0..1
    accent: str = "neutral"
    backend: str = "piper-local"


@dataclass(slots=True)
class StyleProfile:
    palette: list[str] = field(default_factory=lambda: ["#f4e2c8", "#2b2b2b", "#c98a5b"])
    aesthetic: str = "warm-natural"
    caption_tone: str = "conversational"


@dataclass(slots=True)
class TraitSet:
    voice: VoiceProfile = field(default_factory=VoiceProfile)
    style: StyleProfile = field(default_factory=StyleProfile)
    personality: dict[str, float] = field(
        default_factory=lambda: {
            "openness": 0.7,
            "conscientiousness": 0.5,
            "extraversion": 0.6,
            "agreeableness": 0.7,
            "neuroticism": 0.3,
        }
    )
    guardrails: list[str] = field(
        default_factory=lambda: ["no-real-person-impersonation", "no-minors"]
    )

    def validate(self) -> None:
        for k, v in self.personality.items():
            if not 0.0 <= v <= 1.0:
                raise PersonaError(f"personality axis {k!r} out of range: {v}")
        if "no-minors" not in self.guardrails:
            raise PersonaError("guardrail 'no-minors' is mandatory and cannot be removed")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TraitSet":
        ts = cls(
            voice=VoiceProfile(**data.get("voice", {})),
            style=StyleProfile(**data.get("style", {})),
            personality=data.get("personality", cls().personality),
            guardrails=data.get("guardrails", cls().guardrails),
        )
        ts.validate()
        return ts


_NICHE_DEFAULTS: dict[str, dict[str, Any]] = {
    "lifestyle": {"caption_tone": "conversational", "aesthetic": "warm-natural"},
    "tech": {"caption_tone": "dry-analytical", "aesthetic": "cool-minimal"},
    "fitness": {"caption_tone": "high-energy", "aesthetic": "gritty-gym"},
    "travel": {"caption_tone": "wistful", "aesthetic": "golden-hour"},
}


def default_traits_for_niche(niche: str) -> TraitSet:
    preset = _NICHE_DEFAULTS.get(niche, _NICHE_DEFAULTS["lifestyle"])
    ts = TraitSet()
    ts.style.caption_tone = preset["caption_tone"]
    ts.style.aesthetic = preset["aesthetic"]
    ts.validate()
    return ts