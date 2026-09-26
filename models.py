"""
PRAHARI Backend - Database Models
------------------------------------
ORM models built directly against the real uploaded datasets:
  - data/monthly_data.csv  (600 rows: 100 projects x 6 months)
  - data/projects.csv       (100 rows: one per project, aggregated)

IMPORTANT - risk_score / risk_level renaming:
The project-level CSV includes `risk_score` and `risk_level` columns
that are computed directly from the same features stored alongside
them (progress_gap, delay_days, cost_deviation_pct, etc). This means:
  - They are NOT real-world verified outcomes.
  - They should NEVER be used as a prediction target for a genuine
    supervised model - that would just be learning the rule that
    generated them (leakage), not real risk.
Per the changelog, these are renamed here to `rule_based_risk_score`
and `rule_based_risk_level` so nobody downstream (frontend, teammates,
judges) mistakes them for ground truth or real model output.

NOTE ON mp_id: no separate MP-profile dataset has been provided yet,
so `mp_id` is stored as a plain string column on both tables rather
than a foreign key to an `mp_profiles` table. That table can be added
later without touching these two.

FEEDBACK TABLE (added later, once time pressure eased):
citizen_feedback was originally an in-memory Python list in
routes/feedback.py (see that file's old NOTE) - it reset to empty on
every server restart. This table replaces that with real persistence.
Field names match the FeedbackIn/FeedbackOut schemas already in use,
so routes/feedback.py only needed to change how it stores data, not
its request/response shape - the frontend and Swagger contract are
unaffected.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base


class MonthlyUpdate(Base):
    """
    One row = one project's progress snapshot for one month.
    Maps to data/monthly_data.csv (600 rows).
    """
    __tablename__ = "monthly_updates"

    # Surrogate primary key - no single CSV column is unique per row,
    # since project_id repeats once per month (6 times each).
    id = Column(Integer, primary_key=True, autoincrement=True)

    project_id = Column(String, index=True, nullable=False)
    mp_id = Column(String, index=True, nullable=False)
    month_number = Column(Integer, nullable=False)
    reporting_period = Column(String, nullable=False)

    sanctioned_amount_lakh = Column(Float, nullable=False)
    cumulative_amount_spent_lakh = Column(Float, nullable=False)
    monthly_expenditure_lakh = Column(Float, nullable=False)

    financial_progress_pct = Column(Float, nullable=False)
    physical_progress_pct = Column(Float, nullable=False)
    expected_progress_pct = Column(Float, nullable=False)

    current_estimated_cost_lakh = Column(Float, nullable=False)
    cost_deviation_pct = Column(Float, nullable=False)
    delay_days_estimate = Column(Integer, nullable=False)
    financial_physical_gap_pct = Column(Float, nullable=False)


class Project(Base):
    """
    One row = one project's aggregated, current-state summary.
    Maps to data/projects.csv (100 rows, one per project_id).
    """
    __tablename__ = "projects"

    # project_id is genuinely unique here (one row per project), so it
    # doubles as the primary key - no separate surrogate id needed.
    project_id = Column(String, primary_key=True, index=True)
    mp_id = Column(String, index=True, nullable=False)

    sanctioned_amount_lakh = Column(Float, nullable=False)
    current_estimated_cost_lakh = Column(Float, nullable=False)
    amount_spent_lakh = Column(Float, nullable=False)

    financial_progress_pct = Column(Float, nullable=False)
    physical_progress_pct = Column(Float, nullable=False)
    expected_progress_pct = Column(Float, nullable=False)

    progress_gap = Column(Float, nullable=False)
    max_progress_gap = Column(Float, nullable=False)
    delay_days = Column(Integer, nullable=False)
    max_delay_days = Column(Integer, nullable=False)
    cost_deviation_pct = Column(Float, nullable=False)

    cost_status = Column(String, nullable=False)   # e.g. "Within Budget", "Major Overrun"
    work_status = Column(String, nullable=False)    # e.g. "Work in Progress", "Completed"

    # Renamed from the CSV's `risk_score` / `risk_level` - see module
    # docstring above for why. Do not rename these back or treat them
    # as verified ground truth.
    rule_based_risk_score = Column(Float, nullable=False)
    rule_based_risk_level = Column(String, nullable=False)


class Feedback(Base):
    """
    One row = one citizen-submitted report about a project.
    Replaces the old in-memory `_reports` list in routes/feedback.py,
    which lost all data on every server restart.

    Field names deliberately match the existing FeedbackIn/FeedbackOut
    Pydantic schemas in routes/feedback.py, so the API's request and
    response shape does not change - only where the data is stored.
    """
    __tablename__ = "citizen_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)

    citizen_name = Column(String, nullable=False)
    citizen_contact = Column(String, nullable=True)
    state = Column(String, nullable=False)
    mp_id = Column(String, index=True, nullable=False)
    project_id = Column(String, index=True, nullable=False)
    issue_type = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # Stored as an actual DateTime column (not a string) so it can be
    # sorted/filtered properly by the database if needed later.
    created_at = Column(DateTime, nullable=False)