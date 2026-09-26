"""
PRAHARI Backend - One-time data loader
------------------------------------------
Creates the database tables (if they don't exist) and loads the two
CSVs into them. Safe to re-run: it clears existing rows first so you
don't get duplicates if you run it twice.

Run with:
    python load_data.py
"""

import csv
from database import engine, SessionLocal, Base
from models import MonthlyUpdate, Project

# Create tables based on models.py
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Clear existing rows first so re-running this doesn't duplicate data
    db.query(MonthlyUpdate).delete()
    db.query(Project).delete()

    # ---- Load monthly_data.csv ----
    with open("data/monthly_data.csv", newline="") as f:
        reader = csv.DictReader(f)
        monthly_count = 0
        for row in reader:
            db.add(MonthlyUpdate(
                project_id=row["project_id"],
                mp_id=row["mp_id"],
                month_number=int(row["month_number"]),
                reporting_period=row["reporting_period"],
                sanctioned_amount_lakh=float(row["sanctioned_amount_lakh"]),
                cumulative_amount_spent_lakh=float(row["cumulative_amount_spent_lakh"]),
                monthly_expenditure_lakh=float(row["monthly_expenditure_lakh"]),
                financial_progress_pct=float(row["financial_progress_pct"]),
                physical_progress_pct=float(row["physical_progress_pct"]),
                expected_progress_pct=float(row["expected_progress_pct"]),
                current_estimated_cost_lakh=float(row["current_estimated_cost_lakh"]),
                cost_deviation_pct=float(row["cost_deviation_pct"]),
                delay_days_estimate=int(row["delay_days_estimate"]),
                financial_physical_gap_pct=float(row["financial_physical_gap_pct"]),
            ))
            monthly_count += 1

    # ---- Load projects.csv ----
    with open("data/projects.csv", newline="") as f:
        reader = csv.DictReader(f)
        project_count = 0
        for row in reader:
            db.add(Project(
                project_id=row["project_id"],
                mp_id=row["mp_id"],
                sanctioned_amount_lakh=float(row["sanctioned_amount_lakh"]),
                current_estimated_cost_lakh=float(row["current_estimated_cost_lakh"]),
                amount_spent_lakh=float(row["amount_spent_lakh"]),
                financial_progress_pct=float(row["financial_progress_pct"]),
                physical_progress_pct=float(row["physical_progress_pct"]),
                expected_progress_pct=float(row["expected_progress_pct"]),
                progress_gap=float(row["progress_gap"]),
                max_progress_gap=float(row["max_progress_gap"]),
                delay_days=int(row["delay_days"]),
                max_delay_days=int(row["max_delay_days"]),
                cost_deviation_pct=float(row["cost_deviation_pct"]),
                cost_status=row["cost_status"],
                work_status=row["work_status"],
                # Renamed on the way in - CSV column is `risk_score`/`risk_level`
                rule_based_risk_score=float(row["risk_score"]),
                rule_based_risk_level=row["risk_level"],
            ))
            project_count += 1

    db.commit()
    print(f"Loaded {monthly_count} monthly records and {project_count} projects.")

finally:
    db.close()