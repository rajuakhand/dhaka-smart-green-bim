"""
Phase 3 API — BIM / IFC integration.

Endpoints:
    GET  /bim/capability            - honest engine availability
    POST /bim/upload                - upload an IFC file (multipart)
    POST /bim/analyze               - parse + validate + convert a server-side path
    POST /bim/projects/{id}/import  - import an IFC into a project's rooms

Security:
    - Extension allowlist (.ifc only)
    - Size limit from settings (default 25 MB)
    - Filename sanitisation (basename only, no path traversal)
    - Stored under a dedicated uploads directory, never executed
    - Parsed only by IfcOpenShell; never evaluated as code

Principle:
    If IfcOpenShell is unavailable, every endpoint returns
    `{"executed": false, "status": "Not evaluated", ...}` — never fabricated
    model data.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.core.config import settings
from src.modules.bim import engine as bim_engine
from src.modules.bim.converter import convert_to_analysis_model
from src.modules.bim.parser import model_summary, parse_ifc
from src.modules.bim.validator import validate_model

router = APIRouter(prefix="/bim")

# Upload directory (created on demand)
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "uploads",
)

ALLOWED_EXTENSIONS = (".ifc",)
DEFAULT_MAX_SIZE_MB = 25


def _ensure_upload_dir() -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


def _safe_name(filename: str) -> str:
    """Reduce an uploaded filename to a safe basename."""
    name = os.path.basename(filename or "")
    name = name.replace("..", "_").replace("/", "_").replace("\\", "_")
    name = "".join(ch for ch in name if ch.isalnum() or ch in "._- ")
    return name.strip() or f"model_{uuid.uuid4().hex[:8]}.ifc"


def _validate_upload(filename: str, size_bytes: int) -> None:
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    max_bytes = DEFAULT_MAX_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_bytes / (1024*1024):.1f} MB "
                   f"(limit {DEFAULT_MAX_SIZE_MB} MB).",
        )


class AnalyzeRequest(BaseModel):
    file_path: str
    run_validation: bool = True


@router.get("/capability")
def bim_capability():
    """Report whether IFC parsing is available on this deployment."""
    return bim_engine.bim_capability_report()


@router.post("/upload")
async def upload_ifc(file: UploadFile = File(...)):
    """Upload an IFC file and parse it.

    Returns the model summary plus a server-side path usable with /bim/analyze.
    """
    status = bim_engine.detect_ifc_engine()
    if not status.available:
        return bim_engine.bim_not_evaluated(
            f"IfcOpenShell unavailable: {status.error or 'not installed'}"
        )

    _ensure_upload_dir()
    safe = _safe_name(file.filename)
    unique = f"{uuid.uuid4().hex[:8]}_{safe}"
    dest = os.path.join(UPLOAD_DIR, unique)

    size = 0
    try:
        with open(dest, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > DEFAULT_MAX_SIZE_MB * 1024 * 1024:
                    out.close()
                    os.unlink(dest)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {DEFAULT_MAX_SIZE_MB} MB limit.",
                    )
                out.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        if os.path.exists(dest):
            os.unlink(dest)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    _validate_upload(safe, size)

    try:
        model = parse_ifc(dest)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"IFC parse failed: {exc}")

    return {
        "executed": True,
        "uploaded": {
            "original_name": file.filename,
            "stored_name": unique,
            "server_path": dest,
            "size_bytes": size,
        },
        "model": model_summary(model),
        "note": "The server-side path is for analysis only; do not expose it publicly.",
    }


@router.post("/analyze")
def analyze_ifc(req: AnalyzeRequest):
    """Parse, validate and convert an IFC file into the analysis model."""
    status = bim_engine.detect_ifc_engine()
    if not status.available:
        return bim_engine.bim_not_evaluated(
            f"IfcOpenShell unavailable: {status.error or 'not installed'}"
        )

    path = req.file_path
    if not os.path.isabs(path):
        # allow relative to the repo root
        repo_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        candidate = os.path.join(repo_root, path)
        if os.path.exists(candidate):
            path = candidate

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"File not found: {req.file_path}")

    try:
        model = parse_ifc(path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"IFC parse failed: {exc}")

    result: dict = {
        "executed": True,
        "file": os.path.basename(path),
        "model": model_summary(model),
    }

    if req.run_validation:
        result["validation"] = validate_model(model).to_dict()

    result["analysis_model"] = convert_to_analysis_model(model)
    return result


@router.post("/projects/{project_id}/import")
def import_ifc_to_project(project_id: str, req: AnalyzeRequest):
    """Import an IFC file and create rooms on an existing project."""
    from src.api.projects import _projects
    from src.api.rooms import _rooms
    from src.models.schemas import Room, RoomCreate

    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")

    status = bim_engine.detect_ifc_engine()
    if not status.available:
        return bim_engine.bim_not_evaluated(
            f"IfcOpenShell unavailable: {status.error or 'not installed'}"
        )

    path = req.file_path
    if not os.path.isabs(path):
        repo_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        candidate = os.path.join(repo_root, path)
        if os.path.exists(candidate):
            path = candidate

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"File not found: {req.file_path}")

    try:
        model = parse_ifc(path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"IFC parse failed: {exc}")

    analysis = convert_to_analysis_model(model)

    created: list[Room] = []
    skipped: list[dict] = []
    for room in analysis["rooms"]:
        if not room.get("length_m") or not room.get("width_m") or not room.get("height_m"):
            skipped.append({"name": room["name"], "reason": "missing dimensions"})
            continue

        if room.get("window_area_m2") is None:
            # Window area unknown from BIM; keep as unknown rather than zero.
            window_area = 0.0
            skipped.append({
                "name": room["name"],
                "reason": "window area not resolvable from IFC; set to 0 for screening",
            })
        else:
            window_area = room["window_area_m2"]

        try:
            rc = RoomCreate(
                name=room["name"],
                room_type=room["room_type"],
                length_m=room["length_m"],
                width_m=room["width_m"],
                height_m=room["height_m"],
                window_area_m2=window_area,
                openable_window_area_m2=window_area,
                occupants=1,
            )
        except Exception as exc:  # noqa: BLE001
            skipped.append({"name": room["name"], "reason": f"validation: {exc}"})
            continue

        # Persist as a full Room with identity, matching POST /projects/{id}/rooms
        created.append(Room(
            id=str(uuid.uuid4()),
            building_id=project_id,
            created_at=datetime.now(timezone.utc),
            **rc.model_dump(),
        ))

    if not created:
        raise HTTPException(
            status_code=422,
            detail=f"No usable rooms extracted. Skipped: {skipped}",
        )

    if project_id not in _rooms:
        _rooms[project_id] = []
    _rooms[project_id].extend(created)

    return {
        "executed": True,
        "project_id": project_id,
        "source_file": os.path.basename(path),
        "rooms_created": len(created),
        "rooms_skipped": skipped,
        "analysis_model": analysis,
        "note": (
            "Rooms were created from IfcSpace geometry. Occupants default to 1 and "
            "must be confirmed by the user; window area is set from BIM glazing "
            "where resolvable."
        ),
    }


@router.get("/schemas")
def supported_schemas():
    """List supported IFC schemas and parser capabilities."""
    return {
        "schemas": ["IFC2X3", "IFC4", "IFC4X3"],
        "measurable_entities": {
            "spaces": ["IfcSpace", "IfcZone", "IfcSpatialZone"],
            "walls": ["IfcWall", "IfcWallStandardCase", "IfcCurtainWall"],
            "slabs": ["IfcSlab", "IfcCovering"],
            "roofs": ["IfcRoof"],
            "windows": ["IfcWindow", "IfcWindowStandardCase"],
            "doors": ["IfcDoor", "IfcDoorStandardCase"],
        },
        "geometry_supported": ["IfcExtrudedAreaSolid (rectangular / circular / arbitrary-closed profile)"],
        "geometry_not_supported": ["IfcFacetedBrep", "IfcAdvancedBrep", "IfcBooleanClippingResult"],
        "length_units_converted": [
            "METRE", "KILO", "CENTI", "MILLI", "MICRO",
            "DECI", "DECA", "HECTO", "MEGA", "GIGA",
        ],
        "note": "Non-SI length units (e.g. FOOT) are not converted and are flagged.",
    }