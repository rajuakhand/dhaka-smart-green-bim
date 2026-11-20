"""
Projects API — CRUD endpoints for building projects.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.models.schemas import BuildingCreate, Building

router = APIRouter()


# In-memory store for MVP (replace with DB in production)
_projects: dict[str, Building] = {}


class ProjectSummary(BaseModel):
    id: str
    name: str
    city: str
    building_type: str
    num_floors: int


@router.post("/projects", response_model=Building, status_code=201)
def create_project(building: BuildingCreate):
    """Create a new building project."""
    import uuid
    from datetime import datetime, timezone

    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    project = Building(
        id=project_id,
        created_at=now,
        updated_at=now,
        **building.model_dump(),
    )
    _projects[project_id] = project
    return project


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects():
    """List all projects."""
    return [
        ProjectSummary(
            id=p.id,
            name=p.name,
            city=p.city,
            building_type=p.building_type.value,
            num_floors=p.num_floors,
        )
        for p in _projects.values()
    ]


@router.get("/projects/{project_id}", response_model=Building)
def get_project(project_id: str):
    """Get a project by ID."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    return _projects[project_id]


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: str):
    """Delete a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")
    del _projects[project_id]