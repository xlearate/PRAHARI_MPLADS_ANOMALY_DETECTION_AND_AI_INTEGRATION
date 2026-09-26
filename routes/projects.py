"""
PRAHARI Backend — /api/projects routes
------------------------------------
Moved out of main.py so main.py just wires routers together.
Same logic as before, no behavior change.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Project, MonthlyUpdate
from schemas import ProjectOut, ProjectDetailOut

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    """Returns all projects from the real database (100 rows)."""
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Returns one project's full detail, including its 6-month history."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    monthly = (
        db.query(MonthlyUpdate)
        .filter(MonthlyUpdate.project_id == project_id)
        .order_by(MonthlyUpdate.month_number)
        .all()
    )

    return ProjectDetailOut(
        **{c.name: getattr(project, c.name) for c in project.__table__.columns},
        monthly_updates=monthly
    )