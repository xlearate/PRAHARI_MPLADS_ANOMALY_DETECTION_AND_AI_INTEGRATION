"""
PRAHARI Backend — /api/mp routes
------------------------------------
NOTE: the real dataset has no separate MP-profile or per-year table
(see models.py's own note on this). So unlike the frontend's mock
mockMPs.js — which has fake multi-year history for the demo — this
endpoint can only aggregate what actually exists: each MP's CURRENT
snapshot across their projects. No 2023/2024/2025 breakdown is
possible from real data yet.

Tier logic mirrors the frontend's mpYearScore()/mpTierFromScore() in
mockMPs.js, so a demo switching from mock to real data doesn't change
what "Good/Moderate/Worse" means.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

from database import get_db
from models import Project

router = APIRouter(prefix="/api/mp", tags=["mp"])


def _tier_from_score(score: float) -> str:
    if score >= 70:
        return "good"
    if score >= 45:
        return "moderate"
    return "worse"


@router.get("/performance")
def get_mp_performance(db: Session = Depends(get_db)):
    """
    Groups all projects by mp_id and returns each MP's current
    performance summary: project count, completed count, average
    fund utilization, average risk, and a Good/Moderate/Worse tier.
    """
    projects = db.query(Project).all()
    by_mp = defaultdict(list)
    for p in projects:
        by_mp[p.mp_id].append(p)

    results = []
    for mp_id, plist in by_mp.items():
        total = len(plist)
        completed = sum(1 for p in plist if p.work_status == "Completed")
        avg_utilization = sum(
            (p.amount_spent_lakh / p.sanctioned_amount_lakh * 100) if p.sanctioned_amount_lakh else 0
            for p in plist
        ) / total
        avg_risk = sum(p.rule_based_risk_score for p in plist) / total

        # Same weighting shape as the frontend's mpYearScore(), adapted
        # to current-snapshot fields instead of yearly aggregates.
        completion_mix = (completed / total) * 100
        score = round(
            completion_mix * 0.35 + avg_utilization * 0.30 + (100 - avg_risk) * 0.35,
            1,
        )

        results.append({
            "mp_id": mp_id,
            "total_projects": total,
            "completed_projects": completed,
            "avg_utilization_pct": round(avg_utilization, 1),
            "avg_risk_score": round(avg_risk, 1),
            "performance_score": score,
            "tier": _tier_from_score(score),
        })

    return sorted(results, key=lambda r: r["performance_score"], reverse=True)