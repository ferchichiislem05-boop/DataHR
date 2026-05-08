"""
HR Analytics - Step 3: Export aggregated tables for Power BI
These CSVs can be loaded directly into Power BI as flat tables,
bypassing the need for a live SQL Server connection.
"""

import pandas as pd
import os

CLEANED  = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\processed\hr_cleaned.csv"
OUT_DIR  = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\exports"

df = pd.read_csv(CLEANED)
os.makedirs(OUT_DIR, exist_ok=True)

def save(frame, name):
    path = os.path.join(OUT_DIR, name)
    frame.to_csv(path, index=False)
    print(f"Saved: {name}  ({len(frame)} rows)")

# ── Detect column names dynamically ──────────────────────────
dept_col    = next((c for c in df.columns if "department" in c), None)
grade_col   = next((c for c in df.columns if "grade" in c), None)
gender_col  = next((c for c in df.columns if "gender" in c or "sex" in c), None)
manager_col = next((c for c in df.columns if "manager" in c), None)
join_col    = next((c for c in df.columns if "join" in c), None)
status_col  = next((c for c in df.columns if "status" in c), None)
type_col    = next((c for c in df.columns if "employee_type" in c), None)

attr = "is_attrition"

def attr_agg(grp_cols):
    return (
        df.groupby(grp_cols, dropna=False)
        .agg(
            headcount=(attr, "count"),
            attritions=(attr, "sum"),
        )
        .assign(attrition_rate_pct=lambda x: (x["attritions"] / x["headcount"] * 100).round(2))
        .reset_index()
    )

# 1. Full cleaned dataset (Power BI main fact table)
save(df, "fact_employees.csv")

# 2. Department KPIs
if dept_col:
    save(attr_agg(dept_col), "dim_department_kpis.csv")

# 3. Grade KPIs
if grade_col:
    save(attr_agg(grade_col), "dim_grade_kpis.csv")

# 4. Age Group KPIs
if "age_group" in df.columns:
    save(attr_agg("age_group"), "dim_age_group_kpis.csv")

# 5. Tenure Band KPIs
if "tenure_band" in df.columns:
    save(attr_agg("tenure_band"), "dim_tenure_kpis.csv")

# 6. Gender KPIs
if gender_col:
    save(attr_agg(gender_col), "dim_gender_kpis.csv")

# 7. Hiring Trend (with date column for Power BI time intelligence)
if join_col:
    df[join_col] = pd.to_datetime(df[join_col], errors="coerce")
    trend = (
        df.dropna(subset=[join_col])
        .assign(hire_year=df[join_col].dt.year, hire_month=df[join_col].dt.month)
        .groupby(["hire_year", "hire_month"])
        .size()
        .reset_index(name="new_hires")
    )
    # Add a proper date column (first of each month) and month name
    trend["date"] = pd.to_datetime(
        trend["hire_year"].astype(str) + "-" + trend["hire_month"].astype(str).str.zfill(2) + "-01"
    )
    trend["month_name"] = trend["date"].dt.strftime("%b")
    trend = trend[["date", "hire_year", "hire_month", "month_name", "new_hires"]]
    save(trend, "dim_hiring_trend.csv")

# 8. Manager Scoreboard
if manager_col:
    mgr = (
        attr_agg(manager_col)
        .query("headcount >= 2")
        .sort_values("attrition_rate_pct", ascending=False)
    )
    save(mgr, "dim_manager_scoreboard.csv")

print("\nAll exports complete.")
