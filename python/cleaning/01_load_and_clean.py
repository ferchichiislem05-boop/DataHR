"""
HR Analytics - Step 1: Load & Clean Data

Column mappings (discovered from raw data inspection):
  Emp Status     -> employee_status   (On-Board / Attrition / Transfer)
  Movement       -> movement          (IJP / OnRoll / NaN)
  Emp Id         -> employee_id
  Name           -> employee_name
  Date of Joining-> date_of_joining   (Excel serial)
  Data of Reliev -> date_of_relieving (Excel serial, mostly null for active)
  Reporting Mgr  -> reporting_manager
  Emp Type       -> employee_type     (Contract)
  Category       -> gender            *** actually stores Male/Female ***
  Date of Birth  -> date_of_birth     (Excel serial — data quality issue, unreliable)
  Marital status -> marital_status    (Single / Married)
  Grade          -> grade             (Contract / Trainees / Management / Professional)
  Department     -> department
  Total Exp      -> total_experience  (float, 0-19 years)
  Year           -> hire_year         (2020-2025)
  Stability      -> stability         (5+yr / 4+yr / ... / <1yr)
  Visa Type      -> visa_type         (Golden Visa / Company Sponsored / Family Sponsored)
  Year formule   -> (dropped — duplicate of stability)
"""

import pandas as pd
import numpy as np
from datetime import date
import pyxlsb
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_FILE  = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\raw\HR_Dataset.xlsb"
OUT_CSV   = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\processed\hr_cleaned.csv"
OUT_EXCEL = r"C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\processed\hr_cleaned.xlsx"

# ── Helper: Excel serial -> Timestamp ─────────────────────────────────────────
_EXCEL_EPOCH = pd.Timestamp("1899-12-30")

def xl_date(val):
    try:
        v = float(val)
        return _EXCEL_EPOCH + pd.Timedelta(days=v) if v > 1 else pd.NaT
    except Exception:
        return pd.NaT

# ── 1. Load raw sheet ──────────────────────────────────────────────────────────
print("Loading 'HR data' sheet...")
raw_rows = []
with pyxlsb.open_workbook(RAW_FILE) as wb:
    with wb.get_sheet("HR data") as sh:
        for row in sh.rows():
            raw_rows.append([c.v for c in row])

headers = raw_rows[0]
df = pd.DataFrame(raw_rows[1:], columns=headers)
df.replace("", np.nan, inplace=True)
df.dropna(how="all", inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"  {len(df)} rows, {df.shape[1]} columns\n")

# ── 2. Rename columns to clean names ──────────────────────────────────────────
col_map = {
    "Emp Status":           "employee_status",
    "Movement":             "movement",
    "Emp Id":               "employee_id",
    "Name":                 "employee_name",
    "Date of Joining":      "date_of_joining",
    "Data of Relieving":    "date_of_relieving",
    "Reporting Manager":    "reporting_manager",
    "Emp Type":             "employee_type",
    "Category":             "gender",          # ← actually stores Male/Female
    "Date of Birth":        "date_of_birth",   # serial dates, used only if valid
    "Marital status":       "marital_status",
    "Grade":                "grade",
    "Department":           "department",
    "Total Experience":     "total_experience",
    "Year":                 "hire_year",
    "Stability":            "stability",
    "Visa Type":            "visa_type",
    "Year formule avancer ": None,             # drop — duplicate of stability
}
df.rename(columns={k: v for k, v in col_map.items() if v is not None and k in df.columns},
          inplace=True)
drop_cols = [k for k, v in col_map.items() if v is None and k in df.columns]
df.drop(columns=drop_cols, errors="ignore", inplace=True)
print("Columns after rename:", list(df.columns), "\n")

# ── 3. Convert Excel date serials ─────────────────────────────────────────────
for col in ["date_of_joining", "date_of_relieving", "date_of_birth"]:
    if col in df.columns:
        df[col] = df[col].apply(xl_date)
        print(f"  {col}: {df[col].isna().sum()} nulls | "
              f"range: {df[col].min().date()} to {df[col].max().date()}")
print()

# ── 4. Derived columns ────────────────────────────────────────────────────────
today = pd.Timestamp(date.today())

# Tenure from joining date
if "date_of_joining" in df.columns:
    df["tenure_years"] = ((today - df["date_of_joining"]).dt.days / 365.25).round(2)
    df["tenure_years"] = df["tenure_years"].where(df["tenure_years"].between(0, 40))

# Hire year (already present, cast to int)
if "hire_year" in df.columns:
    df["hire_year"] = pd.to_numeric(df["hire_year"], errors="coerce").astype("Int64")

# Estimated age from experience (experience + avg entry age 23)
if "total_experience" in df.columns:
    df["total_experience"] = pd.to_numeric(df["total_experience"], errors="coerce")
    df["estimated_age"] = (df["total_experience"] + 23).round(1)
    df["estimated_age"] = df["estimated_age"].where(df["estimated_age"].between(18, 70))

# Age group (from estimated_age)
if "estimated_age" in df.columns:
    df["age_group"] = pd.cut(
        df["estimated_age"],
        bins=[0, 25, 30, 35, 40, 50, 120],
        labels=["<25", "25-29", "30-34", "35-39", "40-49", "50+"],
        right=False
    ).astype(str)

# Tenure band
if "tenure_years" in df.columns:
    df["tenure_band"] = pd.cut(
        df["tenure_years"],
        bins=[0, 1, 2, 3, 4, 5, 6, 100],
        labels=["<1yr", "1yr", "2yr", "3yr", "4yr", "5yr", "6+yr"],
        right=False
    ).astype(str)

# Attrition flag: 0 = On-Board (active), 1 = Attrition or Transfer
if "employee_status" in df.columns:
    df["is_attrition"] = (
        df["employee_status"].astype(str).str.lower().str.strip()
        .isin(["attrition", "transfer"])
    ).astype(int)
    rate = df["is_attrition"].mean() * 100
    active = (df["is_attrition"] == 0).sum()
    left   = df["is_attrition"].sum()
    print(f"Attrition: {left} left ({rate:.1f}%) | {active} active")

# ── 5. Clean text fields ──────────────────────────────────────────────────────
text_cols = [c for c in df.columns
             if df[c].dtype not in ["datetime64[us]", "float64", "int64", "Int64"]
             and c not in ["age_group", "tenure_band"]]
for col in text_cols:
    df[col] = (df[col].astype(str)
               .str.strip().str.title()
               .replace({"Nan": np.nan, "None": np.nan, "": np.nan}))

# ── 6. Null report ────────────────────────────────────────────────────────────
nulls = df.isnull().sum()
nulls = nulls[nulls > 0]
print("\nNull values:")
print(nulls.to_string())

# ── 7. Key stats ──────────────────────────────────────────────────────────────
print(f"\nTotal rows: {len(df)}")
print(f"Avg tenure: {df['tenure_years'].mean():.1f} years")
print(f"Avg estimated age: {df['estimated_age'].mean():.1f} years")
print(f"Departments: {df['department'].nunique()}")
print(f"Grades: {df['grade'].unique().tolist()}")
print(f"Visa types: {df['visa_type'].unique().tolist()}")
print(f"Gender split: {df['gender'].value_counts().to_dict()}")
print(f"Marital: {df['marital_status'].value_counts().to_dict()}")

# ── 8. Export ─────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
df.drop(columns=["date_of_birth"], errors="ignore", inplace=True)  # unreliable
df.to_csv(OUT_CSV, index=False, encoding="utf-8")
df.to_excel(OUT_EXCEL, index=False)
print(f"\nSaved -> {OUT_CSV}")
print(f"Saved -> {OUT_EXCEL}")
print(f"Final shape: {df.shape[0]} rows x {df.shape[1]} columns")
