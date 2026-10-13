"""Backend registry.

Backends are keyed by stage (voice | face | llm). The config picks which
concrete adapter each stage uses; this module resolves the name to a class
and instantiates it with the backend's config block.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from persona_forge.config.schema import BackendConfig, ForgeConfig
from persona_forge.core.errors import BackendError
from persona_forge.services.backends.face_local import LocalFaceBackend
from persona_forge.services.backends.llm_http import HttpLlmBackend
from persona_forge.services.backends.voice_local import LocalVoiceBackend

if TYPE_CHECKING:
    from persona_forge.services.backends.base import Backend

_REGISTRY: dict[str, type["Backend"]] = {
    "piper-local": LocalVoiceBackend,
    "diffusers-local": LocalFaceBackend,
    "openai-compat": HttpLlmBackend,
    "ollama": HttpLlmBackend,
}


def get_backend(config: ForgeConfig, stage: str) -> "Backend":
    for backend_cfg in config.backends:
        if backend_cfg.kind == stage and backend_cfg.enabled:
            return _instantiate(backend_cfg)
    raise BackendError(f"no enabled backend for stage {stage!r}")


def _instantiate(cfg: BackendConfig) -> "Backend":
    try:
        cls = _REGISTRY[cfg.name]
    except KeyError as exc:
        raise BackendError(f"unknown backend {cfg.name!r}") from exc
    return cls(cfg)