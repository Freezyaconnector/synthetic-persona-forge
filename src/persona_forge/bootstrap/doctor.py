"""Environment + config doctor for the forge.

Checks the runtime (Python version, platform), the sidecars (C++/C#/Java
optional), the backends reachable from config, and whether the config file
is present and parseable. `--fix` writes a starter config.
"""

from __future__ import annotations

import platform
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w

from persona_forge.config.schema import ForgeConfig
from persona_forge.utils.log import get_logger

log = get_logger(__name__)

STARTER_CONFIG = ForgeConfig.starter()


@dataclass(slots=True)
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass(slots=True)
class DoctorReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)

    def render(self) -> str:
        lines = ["synthetic-persona-forge :: doctor", "-" * 40]
        for c in self.checks:
            mark = "ok " if c.ok else "FAIL"
            lines.append(f"[{mark}] {c.name:<22} {c.detail}")
        lines.append("-" * 40)
        lines.append("all good" if self.ok else "one or more checks failed")
        return "\n".join(lines)


def _check_python() -> Check:
    v = sys.version_info
    ok = (3, 11) <= (v.major, v.minor) < (3, 13)
    return Check("python", ok, f"{v.major}.{v.minor}.{v.micro} on {platform.system()}")


def _check_sidecar(name: str, prog: str) -> Check:
    path = shutil.which(prog)
    return Check(f"sidecar:{name}", True, path or "not found (optional)")


def _check_backends(cfg: ForgeConfig) -> list[Check]:
    out: list[Check] = []
    for backend in cfg.backends:
        out.append(Check(f"backend:{backend.name}", backend.enabled, backend.kind))
    return out


def run(config_path: Path, fix: bool = False) -> DoctorReport:
    report = DoctorReport()
    report.checks.append(_check_python())
    report.checks.append(_check_sidecar("msvc", "cl"))
    report.checks.append(_check_sidecar("dotnet", "dotnet"))
    report.checks.append(_check_sidecar("jdk", "java"))

    if not config_path.exists():
        if fix:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(tomli_w.dumps(STARTER_CONFIG.to_toml()), encoding="utf-8")
            report.checks.append(Check("config", True, f"wrote starter -> {config_path}"))
        else:
            report.checks.append(Check("config", False, f"missing: {config_path}"))
            return report

    try:
        cfg = ForgeConfig.from_toml(config_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - doctor surfaces any parse failure
        report.checks.append(Check("config", False, f"parse error: {exc}"))
        return report

    report.checks.append(Check("config", True, f"{len(cfg.backends)} backend(s)"))
    report.checks.extend(_check_backends(cfg))
    return report