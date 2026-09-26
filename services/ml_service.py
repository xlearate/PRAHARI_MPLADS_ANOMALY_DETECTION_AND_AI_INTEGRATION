"""
PRAHARI Backend - ML Integration Service (real model)
-------------------------------------------------------
Replaces the mock rule-based logic with the actual trained model from
ml/mplads_full_ai.pkl (built by train.py).

WHY THIS FILE LOOKS DIFFERENT FROM THE MOCK:
The mock's get_risk_prediction() took a flat dict of a project's
CURRENT snapshot fields. The real model was trained on TREND features
computed from 6 months of history (see train.py's docstring for why -
snapshot fields leaked the label almost exactly). So this version
needs a database Session, not just a dict - it has to pull a
project's monthly_updates rows itself to compute the same features
train.py computed from monthly_data.csv.

THE FEATURE MATH BELOW IS DELIBERATELY WRITTEN TO MIRROR train.py'S
make_features() EXACTLY:
    financial_velocity      = (last.financial_progress_pct - first.financial_progress_pct) / span
    spending_volatility     = std of monthly_expenditure_lakh (sample std, ddof=1, same as pandas .std())
    avg_monthly_expenditure = mean of monthly_expenditure_lakh
    sanctioned_amount_lakh  = pulled from the Project row (train.py merged it from projects.csv,
                              not monthly_data.csv - same source here)
If monthly_data ever stops being exactly 6 rows per project, span is
computed from actual month_number values rather than hardcoding /5,
so this degrades gracefully instead of silently producing wrong numbers.

NOT YET DONE: routes/anomalies.py and routes/risk.py still sort by
Project.rule_based_risk_score directly - they don't call this service
at all yet. Wiring them up needs schemas.py (to know what ProjectOut
can safely carry) before I touch them, so I haven't guessed at it here.

NOT YET TESTED END-TO-END: this container doesn't have your prahari.db
or the source CSVs, so this hasn't been run against real rows. Please
run the smoke test at the bottom of this file's companion instructions
before trusting it.
"""

import os
from typing import TypedDict

import numpy as np
from sqlalchemy.orm import Session

from models import Project, MonthlyUpdate

# ml/ is a sibling of services/ (this file's directory), per train.py's
# `os.makedirs('ml', exist_ok=True)` when run from BACKEND/.
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ml", "mplads_full_ai.pkl")

_model_bundle = None  # lazy-loaded once, cached for the life of the process


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(_MODEL_PATH):
            raise RuntimeError(
                f"Model file not found at {_MODEL_PATH}. "
                "Run `python train.py` from BACKEND/ first to generate it."
            )
        import joblib
        _model_bundle = joblib.load(_MODEL_PATH)
    return _model_bundle


class RiskPredictionOutput(TypedDict):
    project_id: str
    anomaly_score: float
    is_anomaly: bool
    risk_score: int
    risk_level: str
    reasons: list[str]
    model_version: str


def _compute_trend_features(project: Project, monthly_rows: list[MonthlyUpdate]) -> dict:
    """
    Same math as train.py's make_features(), applied to ORM rows
    instead of a pandas groupby. Raises rather than guessing if a
    project has no monthly history - a silent default here would be
    exactly the kind of quiet wrong-number bug we don't want.
    """
    if not monthly_rows:
        raise ValueError(f"No monthly_updates rows found for project {project.project_id}")

    rows = sorted(monthly_rows, key=lambda r: r.month_number)
    first, last = rows[0], rows[-1]

    # train.py divides by a fixed 5 (month 1 to month 6). Computed here
    # from the actual month_number span instead, so this still gives
    # the right answer if a project ever has a different number of
    # reporting months - falls back to the same /5 in the normal case.
    span_months = max(last.month_number - first.month_number, 1)

    expenditures = [r.monthly_expenditure_lakh for r in rows]

    financial_velocity = (last.financial_progress_pct - first.financial_progress_pct) / span_months

    if len(expenditures) > 1:
        spending_volatility = float(np.std(expenditures, ddof=1))  # ddof=1 matches pandas .std()
    else:
        spending_volatility = 0.0  # can't measure volatility from a single month's data

    avg_monthly_expenditure = float(np.mean(expenditures))

    return {
        "financial_velocity": financial_velocity,
        "spending_volatility": spending_volatility,
        "avg_monthly_expenditure": avg_monthly_expenditure,
        "sanctioned_amount_lakh": project.sanctioned_amount_lakh,
    }


def _reasons_from_project(project: Project, features: dict) -> list[str]:
    """
    Human-readable reasons. Deliberately pulls from Project's real,
    already-verified fields (delay_days, cost_deviation_pct,
    progress_gap) for the headline reasons - these are honest facts
    about the project, not model internals, so they stay meaningful
    regardless of what the model itself is doing under the hood. The
    two trend-based reasons are added on top, tied directly to what
    those specific features mean.
    """
    reasons = []

    if project.progress_gap > 20:
        reasons.append("Large financial-physical progress gap")
    if project.delay_days > 30:
        reasons.append("Significant delay against schedule")
    if project.cost_deviation_pct > 15:
        reasons.append("Cost deviation exceeds threshold")
    if features["financial_velocity"] <= 0:
        reasons.append("Financial progress has stalled or reversed over the reporting period")
    if (
        features["avg_monthly_expenditure"] > 0
        and features["spending_volatility"] > features["avg_monthly_expenditure"]
    ):
        reasons.append("Highly irregular month-to-month spending pattern")

    if not reasons:
        reasons.append("No significant anomalies detected")

    return reasons


def _predict_batch(feature_rows: list[dict]):
    """Runs both trained models on a batch, in the exact column order train.py saved."""
    bundle = _load_model()
    xgb_model = bundle["xgb_model"]
    anomaly_model = bundle["anomaly_model"]
    feature_columns = bundle["feature_columns"]

    X = np.array([[row[col] for col in feature_columns] for row in feature_rows])

    risk_proba = xgb_model.predict_proba(X)[:, 1]      # P(computed_risk_score > 50), per train.py's label
    anomaly_raw = anomaly_model.decision_function(X)   # higher = more normal, per sklearn's convention

    return risk_proba, anomaly_raw


def _to_output(project_id: str, risk_proba: float, anomaly_raw: float, reasons: list[str]) -> RiskPredictionOutput:
    risk_score = int(round(risk_proba * 100))

    # Same 60/30 bands the mock and the frontend already use, so
    # switching the underlying number doesn't change what HIGH/MEDIUM/
    # LOW mean on screen.
    if risk_score >= 60:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # IsolationForest's decision_function is unbounded, higher = more
    # normal. Flipped and squashed through a sigmoid purely so the
    # frontend gets something in (0, 1) - this is a relative ranking
    # signal, not a calibrated probability, and should be labelled as
    # such wherever it's shown.
    anomaly_score = round(float(1 / (1 + np.exp(anomaly_raw * 5))), 3)
    is_anomaly = anomaly_raw < 0  # IsolationForest's own inlier/outlier cutoff

    return {
        "project_id": project_id,
        "anomaly_score": anomaly_score,
        "is_anomaly": bool(is_anomaly),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "model_version": "xgb-trend-v1",
    }


def get_risk_prediction(db: Session, project_id: str) -> RiskPredictionOutput:
    """
    Single-project prediction. Pulls the project and its full monthly
    history from the real database, computes the same trend features
    train.py did, and runs both trained models.
    """
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    monthly_rows = (
        db.query(MonthlyUpdate)
        .filter(MonthlyUpdate.project_id == project_id)
        .all()
    )

    features = _compute_trend_features(project, monthly_rows)
    risk_proba, anomaly_raw = _predict_batch([features])
    reasons = _reasons_from_project(project, features)

    return _to_output(project_id, risk_proba[0], anomaly_raw[0], reasons)


def get_all_risk_predictions(db: Session) -> list[RiskPredictionOutput]:
    """
    Batch version for routes that need every project ranked (anomalies
    table, top-risk list). Computes features for all projects and runs
    both models once, instead of once per project - matters once this
    is called on every request.

    Projects with no monthly_updates rows are skipped rather than
    guessed at; check the count you get back against your expected
    project count if you're not sure why one's missing.
    """
    projects = db.query(Project).all()
    all_monthly = db.query(MonthlyUpdate).all()

    monthly_by_project: dict[str, list[MonthlyUpdate]] = {}
    for row in all_monthly:
        monthly_by_project.setdefault(row.project_id, []).append(row)

    feature_rows = []
    valid_projects = []
    for project in projects:
        rows = monthly_by_project.get(project.project_id, [])
        if not rows:
            continue
        feature_rows.append(_compute_trend_features(project, rows))
        valid_projects.append(project)

    if not feature_rows:
        return []

    risk_proba, anomaly_raw = _predict_batch(feature_rows)

    results = []
    for project, features, proba, araw in zip(valid_projects, feature_rows, risk_proba, anomaly_raw):
        reasons = _reasons_from_project(project, features)
        results.append(_to_output(project.project_id, proba, araw, reasons))

    return results