"""
Rooms API — CRUD endpoints for room data.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from src.models.schemas import RoomCreate, Room
from src.api.projects import _projects

router = APIRouter()

# In-memory store for MVP
_rooms: dict[str, list[Room]] = {}


@router.post("/projects/{project_id}/rooms", response_model=list[Room], status_code=201)
def create_rooms(project_id: str, rooms: list[RoomCreate]):
    """Create rooms for a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")

    import uuid
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    created = []
    for r in rooms:
        room = Room(
            id=str(uuid.uuid4()),
            building_id=project_id,
            created_at=now,
            **r.model_dump(),
        )
        created.append(room)

    if project_id not in _rooms:
        _rooms[project_id] = []
    _rooms[project_id].extend(created)
    return created


@router.get("/projects/{project_id}/rooms", response_model=list[Room])
def list_rooms(project_id: str):
    """List rooms for a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    return _rooms.get(project_id, [])


@router.delete("/projects/{project_id}/rooms/{room_id}", status_code=204)
def delete_room(project_id: str, room_id: str):
    """Delete a room."""
    if project_id not in _rooms:
        raise HTTPException(status_code=404, detail="Project not found.")
    _rooms[project_id] = [r for r in _rooms[project_id] if r.id != room_id]