"""
PRAHARI Backend — /api/anomalies routes
------------------------------------
UPDATED: now ranks by the REAL trained model's risk_score (via
ml_service.get_all_risk_predictions), not rule_based_risk_score.

WHY THIS FIXES THE SCORE-CLUSTERING: rule_based_risk_score is a
capped formula (0.35*delay + 0.35*cost + 0.30*gap, clipped at 100),
so many genuinely different projects tie at exactly 100. The trained
model outputs a continuous probability instead, so ties like that
should mostly go away - if they don't, that's worth a second look,
not something to assume is fixed just because we swapped the source.

rule_based_risk_score/level are still included in the response
(ProjectWithRiskOut extends ProjectOut) so nothing that already reads
those fields breaks - the new ml_* fields are additions, not
replacements.

Projects with no monthly_updates rows can't get a real model
prediction (ml_service needs 6 months of history to compute trend
features) - they're skipped here rather than given a fake score.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Project
from schemas import ProjectWithRiskOut
from services import ml_service

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


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


@router.get("", response_model=list[ProjectWithRiskOut])
def get_anomalies(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns projects ranked by the real model's risk_score, highest
    (most anomalous) first. `limit` caps how many rows come back.
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