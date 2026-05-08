"""
HR Analytics - Step 2: Exploratory Data Analysis & KPI Summary
Run AFTER 01_load_and_clean.py has produced hr_cleaned.csv
"""

import pandas as pd
import numpy as np
import os

CLEANED = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\processed\hr_cleaned.csv"
EXPORT  = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\exports\kpi_summary.csv"

df = pd.read_csv(CLEANED)

print("=" * 60)
print("  HR ANALYTICS -- KPI DASHBOARD")
print("=" * 60)

total         = len(df)
attrition_col = "is_attrition" if "is_attrition" in df.columns else None
dept_col      = next((c for c in df.columns if "department" in c), None)
gender_col    = next((c for c in df.columns if "gender" in c), None)
grade_col     = next((c for c in df.columns if "grade" in c), None)
marital_col   = next((c for c in df.columns if "marital" in c), None)
exp_col       = "total_experience" if "total_experience" in df.columns else None
visa_col      = next((c for c in df.columns if "visa" in c), None)
stab_col      = next((c for c in df.columns if "stability" in c), None)
mgr_col       = next((c for c in df.columns if "manager" in c), None)

# ── KPI 1: Headcount ──────────────────────────────────────────────────────────
active = int((df["is_attrition"] == 0).sum()) if attrition_col else total
left   = int(df["is_attrition"].sum()) if attrition_col else 0

print(f"\n[KPI 1] Total Headcount          : {total:,}")
print(f"[KPI 2] Active (On-Board)        : {active:,}")
print(f"        Left (Attrition+Transfer): {left:,}")

# ── KPI 3: Attrition Rate ─────────────────────────────────────────────────────
attrition_rate = 0.0
if attrition_col:
    attrition_rate = df[attrition_col].mean() * 100
    print(f"[KPI 3] Attrition Rate           : {attrition_rate:.1f}%")
    print(f"        Retention Rate           : {100 - attrition_rate:.1f}%")

# ── KPI 4: Avg Tenure ─────────────────────────────────────────────────────────
avg_tenure = 0.0
med_tenure = 0.0
if "tenure_years" in df.columns:
    avg_tenure = df["tenure_years"].mean()
    med_tenure = df["tenure_years"].median()
    print(f"[KPI 4] Avg Tenure               : {avg_tenure:.1f} years")
    print(f"        Median Tenure            : {med_tenure:.1f} years")

# ── KPI 5: Avg Experience ─────────────────────────────────────────────────────
avg_exp = 0.0
if exp_col:
    avg_exp = df[exp_col].mean()
    print(f"[KPI 5] Avg Total Experience     : {avg_exp:.1f} years")

# ── KPI 6: Avg Estimated Age ─────────────────────────────────────────────────
if "estimated_age" in df.columns:
    avg_age = df["estimated_age"].mean()
    print(f"[KPI 6] Avg Estimated Age        : {avg_age:.1f} years")

# ── Department Breakdown ──────────────────────────────────────────────────────
if dept_col:
    print(f"\n--- Department Breakdown ---")
    dept = df[dept_col].value_counts()
    print(dept.to_string())

    if attrition_col:
        print(f"\n--- Attrition by Department ---")
        dept_attr = (
            df.groupby(dept_col)[attrition_col]
            .agg(["sum", "count", "mean"])
            .rename(columns={"sum": "attritions", "count": "headcount", "mean": "rate"})
            .assign(rate=lambda x: (x["rate"] * 100).round(1))
            .sort_values("rate", ascending=False)
        )
        print(dept_attr.to_string())

# ── Gender Distribution ───────────────────────────────────────────────────────
if gender_col:
    print(f"\n--- Gender Distribution ---")
    gender_count = df[gender_col].value_counts()
    gender_pct   = df[gender_col].value_counts(normalize=True).mul(100).round(1)
    for g in gender_count.index:
        print(f"  {g:10}: {gender_count[g]:4}  ({gender_pct[g]}%)")

    if attrition_col:
        print(f"\n--- Attrition by Gender ---")
        g_attr = (
            df.groupby(gender_col)[attrition_col]
            .agg(["sum", "count", "mean"])
            .rename(columns={"sum": "attritions", "count": "headcount", "mean": "rate"})
            .assign(rate=lambda x: (x["rate"] * 100).round(1))
        )
        print(g_attr.to_string())

# ── Grade Distribution ────────────────────────────────────────────────────────
if grade_col:
    print(f"\n--- Grade Distribution ---")
    if attrition_col:
        g_grade = (
            df.groupby(grade_col)[attrition_col]
            .agg(["count", "sum", "mean"])
            .rename(columns={"count": "headcount", "sum": "attritions", "mean": "rate"})
            .assign(rate=lambda x: (x["rate"] * 100).round(1))
            .sort_values("rate", ascending=False)
        )
        print(g_grade.to_string())
    else:
        print(df[grade_col].value_counts().to_string())

# ── Age Group Distribution ────────────────────────────────────────────────────
if "age_group" in df.columns:
    print(f"\n--- Age Group Distribution ---")
    print(df["age_group"].value_counts().sort_index().to_string())

# ── Tenure Band Distribution ──────────────────────────────────────────────────
if "tenure_band" in df.columns:
    print(f"\n--- Tenure Band Distribution ---")
    if attrition_col:
        tb = (
            df.groupby("tenure_band")[attrition_col]
            .agg(["count", "sum", "mean"])
            .rename(columns={"count": "headcount", "sum": "attritions", "mean": "rate"})
            .assign(rate=lambda x: (x["rate"] * 100).round(1))
        )
        print(tb.to_string())
    else:
        print(df["tenure_band"].value_counts().sort_index().to_string())

# ── Marital Status ────────────────────────────────────────────────────────────
if marital_col:
    print(f"\n--- Marital Status vs Attrition ---")
    m = (
        df.groupby(marital_col)[attrition_col]
        .agg(["count", "sum", "mean"])
        .rename(columns={"count": "headcount", "sum": "attritions", "mean": "rate"})
        .assign(rate=lambda x: (x["rate"] * 100).round(1))
    )
    print(m.to_string())

# ── Visa Type ────────────────────────────────────────────────────────────────
if visa_col:
    print(f"\n--- Visa Type ---")
    v = (
        df.groupby(visa_col)[attrition_col]
        .agg(["count", "sum", "mean"])
        .rename(columns={"count": "headcount", "sum": "attritions", "mean": "rate"})
        .assign(rate=lambda x: (x["rate"] * 100).round(1))
        .sort_values("rate", ascending=False)
    )
    print(v.to_string())

# ── Stability ────────────────────────────────────────────────────────────────
if stab_col:
    print(f"\n--- Stability ---")
    print(df[stab_col].value_counts().to_string())

# ── Top Managers by Team Size ────────────────────────────────────────────────
if mgr_col:
    print(f"\n--- Manager Scoreboard (top 10 by team size) ---")
    mgr = (
        df.groupby(mgr_col)[attrition_col]
        .agg(["count", "sum", "mean"])
        .rename(columns={"count": "team_size", "sum": "attritions", "mean": "rate"})
        .assign(rate=lambda x: (x["rate"] * 100).round(1))
        .query("team_size >= 3")
        .sort_values("team_size", ascending=False)
        .head(10)
    )
    print(mgr.to_string())

# ── Export KPI summary ────────────────────────────────────────────────────────
kpis = {
    "total_headcount":    total,
    "active_employees":   active,
    "total_attritions":   left,
    "attrition_rate_pct": round(attrition_rate, 2),
    "retention_rate_pct": round(100 - attrition_rate, 2),
    "avg_tenure_years":   round(avg_tenure, 2),
    "median_tenure_years":round(med_tenure, 2),
    "avg_experience_years":round(avg_exp, 2),
    "departments":        df[dept_col].nunique() if dept_col else None,
}
os.makedirs(os.path.dirname(EXPORT), exist_ok=True)
pd.DataFrame([kpis]).to_csv(EXPORT, index=False)
print(f"\nKPI summary exported -> {EXPORT}")
