"""Exception hierarchy for the forge."""

from __future__ import annotations


class ForgeError(Exception):
    """Base class for all forge errors."""


class ConfigError(ForgeError):
    """Raised when config is missing, malformed, or inconsistent."""


class PersonaError(ForgeError):
    """Raised when a persona manifest or trait set is invalid."""


class BackendError(ForgeError):
    """Raised when a voice/face/LLM backend fails or is unreachable."""


class ExportError(ForgeError):
    """Raised when a platform export cannot be assembled."""