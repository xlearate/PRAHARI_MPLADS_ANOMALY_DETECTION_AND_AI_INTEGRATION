"""
PRAHARI - Model Training (leakage-checked version)
------------------------------------------------------
This replaces the earlier train.py, which had a real (tested, confirmed)
leakage problem: the features included columns that could reconstruct
the label almost exactly through simple arithmetic. Two rounds of
"fixing" the feature list from the projects.csv snapshot alone still
failed the same test, because in this dataset almost every project-level
column is a near-exact function of one or two others.

THE FIX: instead of using more columns from projects.csv (the single
end-state snapshot), this pulls TREND features from monthly_data.csv
(the 6-month history per project) - these carry different information
(how things changed over time), not just another view of the same
end-state numbers.

IMPORTANT - even trend features needed checking, and not all of them
passed:
  - delay_trend (month6 - month1 delay)          -> correlation 1.000 with delay_days -> DROPPED, exact leak
  - cost_deviation_trend (month6 - month1)        -> correlation 0.985 with cost_deviation_pct -> DROPPED
  - velocity_gap_trend (fin. vel - phys. vel)     -> correlation 0.987 with progress_gap -> DROPPED
This happens because delay/cost-deviation accumulate steadily from
near-zero, so "change over 6 months" is nearly the same number as
"the final value" - same leakage, different name.

FEATURES KEPT (correlation with delay_days / cost_deviation_pct /
progress_gap all below 0.6, verified against the real dataset):
  - financial_velocity      (financial progress change per month)
  - spending_volatility     (std dev of monthly expenditure)
  - avg_monthly_expenditure (average monthly spend)
  - sanctioned_amount_lakh  (project size - near-zero correlation, safe)

HONEST CAVEAT: "not derivable by simple arithmetic" is not the same as
"causally meaningful." These features are moderately correlated with
the label (not 0), which is expected and fine - but this is a small,
synthetic dataset (100 projects), so treat any accuracy number here
as a rough signal for a hackathon demo, not a validated real-world
result. Report train AND test accuracy - if they're very close, that's
a good sign; if test accuracy is much lower, the model is likely just
memorizing the small training set.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# ---------------------------------------------------------------------------
# 1. Load both datasets
# ---------------------------------------------------------------------------
monthly = pd.read_csv('data/monthly_data.csv')
projects = pd.read_csv('data/projects.csv')

# ---------------------------------------------------------------------------
# 2. Engineer trend features per project from the 6 monthly snapshots
# ---------------------------------------------------------------------------
monthly = monthly.sort_values(['project_id', 'month_number'])


def make_features(g):
    g = g.sort_values('month_number')
    first, last = g.iloc[0], g.iloc[-1]
    return pd.Series({
        'financial_velocity': (last['financial_progress_pct'] - first['financial_progress_pct']) / 5,
        'spending_volatility': g['monthly_expenditure_lakh'].std(),
        'avg_monthly_expenditure': g['monthly_expenditure_lakh'].mean(),
    })


trend_features = monthly.groupby('project_id').apply(make_features).reset_index()

# Merge in sanctioned_amount_lakh (project size) and the raw ingredients
# needed ONLY to build the label - these three are NOT used as features.
df = trend_features.merge(
    projects[['project_id', 'sanctioned_amount_lakh', 'delay_days', 'cost_deviation_pct', 'progress_gap']],
    on='project_id'
)

# ---------------------------------------------------------------------------
# 3. Build the label - same definition as the rule-based risk score,
#    so this model's target stays consistent with what's already shown
#    on the frontend.
# ---------------------------------------------------------------------------
delay_score = np.clip((df['delay_days'] / 180.0) * 100, 0, 100)
cost_score = np.clip(df['cost_deviation_pct'], 0, 100)
gap_score = np.clip(df['progress_gap'], 0, 100)
df['computed_risk_score'] = (0.35 * delay_score) + (0.35 * cost_score) + (0.30 * gap_score)
y = (df['computed_risk_score'] > 50).astype(int)

# ---------------------------------------------------------------------------
# 4. Feature set - verified independent (see module docstring for the
#    correlation numbers that got the other candidates dropped)
# ---------------------------------------------------------------------------
feature_columns = [
    'financial_velocity',
    'spending_volatility',
    'avg_monthly_expenditure',
    'sanctioned_amount_lakh',
]

X = df[feature_columns]

# ---------------------------------------------------------------------------
# 5. Train/test split
# ---------------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------------------------------------------------------------------------
# 6. Train XGBoost (risk classification)
# ---------------------------------------------------------------------------
xgb_model = xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
xgb_model.fit(X_train, y_train)

train_acc = accuracy_score(y_train, xgb_model.predict(X_train))
test_acc = accuracy_score(y_test, xgb_model.predict(X_test))
print(f"XGBoost train accuracy: {train_acc:.3f}")
print(f"XGBoost test accuracy:  {test_acc:.3f}")
print("(If these two numbers are far apart, or both suspiciously close to 1.0")
print(" on a dataset this small, treat the result with caution.)")

# ---------------------------------------------------------------------------
# 7. Train Isolation Forest (anomaly detection - unsupervised, no
#    leakage risk since it has no label at all)
# ---------------------------------------------------------------------------
anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
anomaly_detector.fit(X_train)

# ---------------------------------------------------------------------------
# 8. Save
# ---------------------------------------------------------------------------
os.makedirs('ml', exist_ok=True)
joblib.dump({
    'xgb_model': xgb_model,
    'anomaly_model': anomaly_detector,
    'feature_columns': feature_columns,
}, 'ml/mplads_full_ai.pkl')

print("Saved to ml/mplads_full_ai.pkl")
