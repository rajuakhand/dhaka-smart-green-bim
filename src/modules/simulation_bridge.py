"""
Module P2-8 — Simulation Engine Bridge.

Honestly reports whether an external simulation engine (EnergyPlus, Radiance)
is available. This module NEVER fabricates simulation output.

If an engine is installed, the bridge would dispatch to it; if not, it reports
"not available" with the reason, and the caller must not present any number as
simulated.

Detected engines:
    - EnergyPlus  (command-line `energyplus`, or Python API)
    - Radiance    (`oconv`, `gensky`, `rpict`)

Design principle: "Never claim simulation was performed when it was not."
Every response carries an explicit `executed: bool`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, asdict

from src.models.schemas import ConfidenceLevel, ResultStatus


@dataclass
class EngineStatus:
    name: str
    available: bool
    path: str | None = None
    version: str | None = None
    detection_method: str = ""
    install_hint: str = ""


def _run(cmd: list[str], timeout: int = 10) -> tuple[int, str]:
    """Run a command, returning (returncode, combined output). Never raises."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError:
        return 127, "command not found"
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except Exception as exc:  # noqa: BLE001 - detection must never crash
        return 1, str(exc)


def detect_energyplus() -> EngineStatus:
    """Detect EnergyPlus availability."""
    path = shutil.which("energyplus")
    if path:
        code, out = _run([path, "--version"])
        version = out.strip().splitlines()[0] if out.strip() else None
        if code == 0:
            return EngineStatus(
                name="EnergyPlus",
                available=True,
                path=path,
                version=version,
                detection_method="shutil.which + --version",
            )

    # Python API fallback
    try:
        import pyenergyplus  # noqa: F401

        return EngineStatus(
            name="EnergyPlus",
            available=True,
            path=None,
            version=getattr(pyenergyplus, "__version__", "unknown"),
            detection_method="python API (pyenergyplus)",
        )
    except Exception:  # noqa: BLE001
        pass

    return EngineStatus(
        name="EnergyPlus",
        available=False,
        detection_method="shutil.which / pyenergyplus import",
        install_hint=(
            "Install EnergyPlus from https://energyplus.net/ and add it to PATH, "
            "or pip install pyenergyplus."
        ),
    )


def detect_radiance() -> EngineStatus:
    """Detect Radiance availability."""
    oconv = shutil.which("oconv")
    gensky = shutil.which("gensky")
    if oconv and gensky:
        code, out = _run([gensky, "-h"])
        return EngineStatus(
            name="Radiance",
            available=True,
            path=oconv,
            version=None,
            detection_method="shutil.which oconv + gensky",
        )
    return EngineStatus(
        name="Radiance",
        available=False,
        detection_method="shutil.which oconv / gensky",
        install_hint=(
            "Install Radiance from https://www.radiance-online.org/ and add "
            "the bin/ directory to PATH."
        ),
    )


def simulation_capability_report() -> dict:
    """Report the availability of every simulation engine.

    This is the honest status endpoint. A false `available` must never be
    presented as a completed simulation.
    """
    ep = detect_energyplus()
    rad = detect_radiance()

    return {
        "engines": {
            "energyplus": asdict(ep),
            "radiance": asdict(rad),
        },
        "any_engine_available": ep.available or rad.available,
        "note": (
            "Analytical, physics-based calculations (solar geometry, daylight "
            "factor, shading, solar heat gain) run natively without an external "
            "engine and are labelled 'Calculated'. Full hourly energy simulation "
            "and climate-based daylight (sDA/ASE) require these engines and are "
            "labelled 'Not evaluated' when unavailable."
        ),
        "principle": "Never report simulated values when no simulation was run.",
    }


def require_engine(engine: str) -> EngineStatus:
    """Return an engine status, raising nothing. Caller checks .available."""
    if engine.lower() == "energyplus":
        return detect_energyplus()
    if engine.lower() == "radiance":
        return detect_radiance()
    return EngineStatus(
        name=engine,
        available=False,
        detection_method="unsupported engine name",
        install_hint="Supported engines: energyplus, radiance",
    )


def not_evaluated(engine: str, reason: str | None = None) -> dict:
    """Standard 'not evaluated' payload used when an engine is missing.

    This is the ONLY correct response when a simulation cannot run. It must
    never be replaced by an estimate presented as a simulation.
    """
    status = require_engine(engine)
    message = (
        f"{status.name} simulation is not available, so this result was NOT "
        f"evaluated. {reason or status.install_hint}"
    )
    return {
        "engine": status.name,
        "engine_available": status.available,
        "executed": False,
        "simulated": False,
        "status": ResultStatus.NOT_EVALUATED.value,
        "confidence": ConfidenceLevel.INSUFFICIENT.value,
        "message": message,
        "install_hint": status.install_hint,
        "limitations": [
            message,
            "No number is reported because no simulation was performed.",
        ],
    }