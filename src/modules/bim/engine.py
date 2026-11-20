"""
Phase 3 — BIM Engine capability detection.

Honestly reports whether IfcOpenShell is available and usable. If the library is
installed but cannot load (e.g. a GLIBCXX mismatch on this host), that is
reported as a distinct, actionable state rather than a silent failure.

Principle: never claim BIM extraction ran when it did not.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, asdict

try:
    import ifcopenshell

    IFC_AVAILABLE = True
    IFC_VERSION = getattr(ifcopenshell, "VERSION", None) or getattr(
        ifcopenshell, "__version__", "unknown"
    )
    IFC_IMPORT_ERROR = ""
except Exception as exc:  # noqa: BLE001 - detection must never crash
    ifcopenshell = None  # type: ignore[assignment]
    IFC_AVAILABLE = False
    IFC_VERSION = None
    IFC_IMPORT_ERROR = str(exc)


# Minimum recommended version. 0.8.1 works on hosts with GLIBCXX <= 3.4.28;
# newer wheels (0.9.x) require GLIBCXX_3.4.29.
RECOMMENDED_MIN_VERSION = "0.8.0"

# gluing: a host may have the package on disk but fail at import time
INSTALL_HINT = (
    "Install IfcOpenShell with: pip install ifcopenshell==0.8.1 "
    "(0.9.x wheels require GLIBCXX_3.4.29; 0.8.1 is built against an older "
    "toolchain and works on more hosts). Conda: conda install -c conda-forge ifcopenshell."
)


@dataclass
class BimEngineStatus:
    name: str
    available: bool
    version: str | None = None
    recommended_min_version: str = RECOMMENDED_MIN_VERSION
    meets_recommended: bool = False
    detection_method: str = ""
    error: str | None = None
    install_hint: str = ""


def _version_tuple(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in str(v).split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        if digits:
            parts.append(int(digits))
    return tuple(parts)


def detect_ifc_engine() -> BimEngineStatus:
    """Detect whether IFC parsing is available and usable."""
    if not IFC_AVAILABLE:
        return BimEngineStatus(
            name="IfcOpenShell",
            available=False,
            detection_method="python import",
            error=IFC_IMPORT_ERROR or "ifcopenshell not installed",
            install_hint=INSTALL_HINT,
        )

    meets = _version_tuple(IFC_VERSION) >= _version_tuple(RECOMMENDED_MIN_VERSION)
    # Smoke-test that the library can actually do something
    try:
        import tempfile
        import os

        model = ifcopenshell.file(schema="IFC4")
        with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            model.write(tmp_path)
            reloaded = ifcopenshell.open(tmp_path)
            ok = reloaded.schema == "IFC4"
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        if not ok:
            return BimEngineStatus(
                name="IfcOpenShell",
                available=False,
                version=IFC_VERSION,
                meets_recommended=meets,
                detection_method="import + write/read smoke test",
                error="Library imported but a write/read round-trip failed.",
                install_hint=INSTALL_HINT,
            )
    except Exception as exc:  # noqa: BLE001
        return BimEngineStatus(
            name="IfcOpenShell",
            available=False,
            version=IFC_VERSION,
            meets_recommended=meets,
            detection_method="import + write/read smoke test",
            error=str(exc),
            install_hint=INSTALL_HINT,
        )

    return BimEngineStatus(
        name="IfcOpenShell",
        available=True,
        version=IFC_VERSION,
        meets_recommended=meets,
        detection_method="python import + write/read smoke test",
        install_hint="",
    )


def bim_capability_report() -> dict:
    """Full BIM capability report for the UI / API."""
    engine = detect_ifc_engine()

    capabilities = {
        "ifc_parse": engine.available,
        "ifc_write": engine.available,
        "space_extraction": engine.available,
        "element_extraction": engine.available,
        "geometry_extraction": engine.available,
        "unit_scaling": engine.available,
        "schema_detection": engine.available,
    }

    return {
        "engines": {"ifcopenshell": asdict(engine)},
        "any_engine_available": engine.available,
        "capabilities": capabilities,
        "supported_schemas": ["IFC2X3", "IFC4", "IFC4X3"],
        "max_upload_size_mb": 25,
        "accepted_extensions": [".ifc"],
        "principle": (
            "BIM extraction is only reported as performed when IfcOpenShell "
            "actually parsed the file. Otherwise results are 'Not evaluated'."
        ),
        "note": (
            "IfcOpenShell parses IFC structure and simple swept-solid geometry. "
            "Full B-rep / advanced geometry is only partially supported and is "
            "reported as a limitation, not silently approximated."
        ),
    }


def require_ifc_engine() -> BimEngineStatus:
    """Return the engine status. Caller must check `.available`."""
    return detect_ifc_engine()


def bim_not_evaluated(reason: str | None = None) -> dict:
    """Standard 'not evaluated' payload when IfcOpenShell is unavailable."""
    status = detect_ifc_engine()
    message = (
        "BIM extraction is not available, so this result was NOT evaluated. "
        f"{reason or status.install_hint or status.error or ''}".strip()
    )
    return {
        "engine": "IfcOpenShell",
        "engine_available": status.available,
        "executed": False,
        "status": "Not evaluated",
        "confidence": "Insufficient data",
        "message": message,
        "install_hint": status.install_hint,
        "limitations": [message, "No model data is reported because no parse was performed."],
    }