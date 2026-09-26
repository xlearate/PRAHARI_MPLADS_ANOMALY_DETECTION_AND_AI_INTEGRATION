"""
PRAHARI Backend - /api/feedback routes
------------------------------------
UPDATED: now writes to the real `citizen_feedback` table in prahari.db
via models.Feedback, instead of the old in-memory Python list.

Previously (see git history / old version of this file): feedback was
stored in a plain list that reset to empty every time the server
restarted. That was a deliberate short-term trade-off during the
initial build under time pressure - this is the permanent fix.

The request/response shape (FeedbackIn/FeedbackOut) is UNCHANGED, so
nothing calling this API - Swagger, the frontend, teammates - needs
to change anything on their end. Only the storage underneath changed.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackIn(BaseModel):
    citizen_name: str
    citizen_contact: str | None = None
    state: str
    mp_id: str
    project_id: str
    issue_type: str
    description: str


class FeedbackOut(FeedbackIn):
    id: int
    created_at: str


@router.get("", response_model=list[FeedbackOut])
def list_feedback(db: Session = Depends(get_db)):
    """Returns all submitted reports from the database, most recent first."""
    reports = db.query(Feedback).order_by(Feedback.id.desc()).all()

    return [
        {
            "id": r.id,
            "citizen_name": r.citizen_name,
            "citizen_contact": r.citizen_contact,
            "state": r.state,
            "mp_id": r.mp_id,
            "project_id": r.project_id,
            "issue_type": r.issue_type,
            "description": r.description,
            "created_at": r.created_at.isoformat(),
        }
        for r in reports
    ]


@router.post("", response_model=FeedbackOut)
def submit_feedback(report: FeedbackIn, db: Session = Depends(get_db)):
    """Accepts a new citizen report and saves it permanently to the database."""
    if not report.citizen_name.strip() or not report.description.strip():
        raise HTTPException(status_code=400, detail="Name and description are required")

    record = Feedback(
        citizen_name=report.citizen_name,
        citizen_contact=report.citizen_contact,
        state=report.state,
        mp_id=report.mp_id,
        project_id=report.project_id,
        issue_type=report.issue_type,
        description=report.description,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "citizen_name": record.citizen_name,
        "citizen_contact": record.citizen_contact,
        "state": record.state,
        "mp_id": record.mp_id,
        "project_id": record.project_id,
        "issue_type": record.issue_type,
        "description": record.description,
        "created_at": record.created_at.isoformat(),
    }