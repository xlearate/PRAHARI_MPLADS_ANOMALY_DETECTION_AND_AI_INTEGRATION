"""
PRAHARI Backend — /api/risk routes
------------------------------------
UPDATED: now ranks by the REAL trained model's risk_score (via
ml_service.get_all_risk_predictions), same change as anomalies.py -
see that file's docstring for why this addresses the score-clustering
at 100 that rule_based_risk_score produced.

ml_reasons (from ml_service.py) replaces what the frontend's
explanation cards were showing from cost_status/work_status/
progress_gap directly - those raw fields are still present on
ProjectWithRiskOut, so nothing that read them before breaks.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Project
from schemas import ProjectWithRiskOut
from services import ml_service

router = APIRouter(prefix="/api/risk", tags=["risk"])


def _merge(project: Project, prediction: dict) -> ProjectWithRiskOut:
    base = {c.name: getattr(project, c.name) for c in project.__table__.columns}
    return ProjectWithRiskOut(
        **base,
        ml_risk_score=prediction["risk_score"],
        ml_risk_level=prediction["risk_level"],
        ml_anomaly_score=prediction["anomaly_score"],
        ml_is_anomaly=prediction["is_anomaly"],
        ml_reasons=prediction["reasons"],
        model_version=prediction["model_version"],
    )


@router.get("/top", response_model=list[ProjectWithRiskOut])
def get_top_risk(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Returns the top `limit` highest-risk projects by the real model's
    score. ml_reasons carries the explanatory factors the frontend's
    factor chips render.
    """
    predictions = ml_service.get_all_risk_predictions(db)
    predictions_by_id = {p["project_id"]: p for p in predictions}

    projects = db.query(Project).all()
    merged = [
        _merge(project, predictions_by_id[project.project_id])
        for project in projects
        if project.project_id in predictions_by_id
    ]

    merged.sort(key=lambda p: p.ml_risk_score, reverse=True)
    return merged[:limit]