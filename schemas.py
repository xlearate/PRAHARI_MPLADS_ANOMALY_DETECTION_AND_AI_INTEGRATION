"""
PRAHARI Backend — Pydantic schemas
------------------------------------
These define the *shape* of API responses (what JSON gets sent out),
separate from models.py (which defines the *database* table structure).

Field names below are matched exactly against the real models.py
(MonthlyUpdate and Project tables) — confirmed 2026-09-26.
"""

from pydantic import BaseModel
from typing import Optional


class MonthlyUpdateOut(BaseModel):
    project_id: str
    mp_id: str
    month_number: int
    reporting_period: str

    sanctioned_amount_lakh: float
    cumulative_amount_spent_lakh: float
    monthly_expenditure_lakh: float

    financial_progress_pct: float
    physical_progress_pct: float
    expected_progress_pct: float

    current_estimated_cost_lakh: float
    cost_deviation_pct: float
    delay_days_estimate: int
    financial_physical_gap_pct: float

    class Config:
        from_attributes = True  # lets this read directly from a SQLAlchemy row


class ProjectOut(BaseModel):
    project_id: str
    mp_id: str

    sanctioned_amount_lakh: float
    current_estimated_cost_lakh: float
    amount_spent_lakh: float

    financial_progress_pct: float
    physical_progress_pct: float
    expected_progress_pct: float

    progress_gap: float
    max_progress_gap: float
    delay_days: int
    max_delay_days: int
    cost_deviation_pct: float

    cost_status: str    # e.g. "Within Budget", "Major Overrun"
    work_status: str    # e.g. "Work in Progress", "Completed"

    # NOTE: these are rule-derived, not verified ground truth or real
    # model output — see models.py's docstring for why they're named
    # this way. Never rename these back to risk_score/risk_level.
    rule_based_risk_score: float
    rule_based_risk_level: str

    class Config:
        from_attributes = True


class ProjectDetailOut(ProjectOut):
    monthly_updates: list[MonthlyUpdateOut] = []


class ProjectWithRiskOut(ProjectOut):
    """
    ProjectOut plus the REAL trained model's output (ml_service.py),
    prefixed ml_ so it's never confused with rule_based_risk_score/
    level above. Used by /api/anomalies and /api/risk/top now that
    they're wired to the actual model instead of just sorting on the
    rule-based score.
    """
    ml_risk_score: int
    ml_risk_level: str
    ml_anomaly_score: float
    ml_is_anomaly: bool
    ml_reasons: list[str]
    model_version: str