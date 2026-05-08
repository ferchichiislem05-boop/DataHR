# Power BI Setup Guide — HR Analytics

---

## Step 1 — Import the CSV files

1. Open **Power BI Desktop**
2. Click **Home → Get Data → Text/CSV**
3. Import each file below **one at a time** — navigate to:
   `C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\exports\`

| File | What it is |
|------|-----------|
| `fact_employees.csv` | Main fact table — one row per employee |
| `dim_department_kpis.csv` | Pre-aggregated department stats |
| `dim_grade_kpis.csv` | Pre-aggregated grade stats |
| `dim_age_group_kpis.csv` | Pre-aggregated age group stats |
| `dim_tenure_kpis.csv` | Pre-aggregated tenure band stats |
| `dim_gender_kpis.csv` | Pre-aggregated gender stats |
| `dim_hiring_trend.csv` | Monthly hiring trend (52 months) |
| `dim_manager_scoreboard.csv` | Manager performance stats |
| `kpi_summary.csv` | Single-row summary of all KPIs |

> For each file, click **Load** (not Transform) — the data is already clean.

---

## Step 2 — Fix column types in Power Query

After loading, for **fact_employees** only:

1. Click **Transform Data** (top ribbon)
2. Select `fact_employees`
3. Fix these columns:

| Column | Change To |
|--------|-----------|
| `date_of_joining` | Date |
| `date_of_relieving` | Date |
| `is_attrition` | Whole Number |
| `hire_year` | Whole Number |
| `tenure_years` | Decimal Number |
| `total_experience` | Decimal Number |
| `estimated_age` | Decimal Number |

4. Click **Close & Apply**

---

## Step 3 — Relationships (Model view)

Click the **Model view** icon (left sidebar, 3rd icon).

**Do NOT create relationships between fact and dim tables.**
The dim tables are pre-aggregated snapshots — they are used directly as visual sources, not joined.

The only optional relationship you can create:

- `dim_hiring_trend[hire_year]` → `fact_employees[hire_year]`
  - Cardinality: Many to Many
  - Cross-filter: Single
  - Only useful if you want year slicers to affect both tables

Otherwise, leave all tables disconnected. Each dim table feeds its own visual.

---

## Step 4 — Create a Measures Table

1. **Home → Enter Data**
2. Name: `_Measures`, leave it empty, click **Load**
3. Select `_Measures` in the Fields pane
4. Click **New Measure** (Modeling tab) for each measure below

### Paste these measures one by one:

```dax
Total Headcount =
COUNTROWS(fact_employees)
```

```dax
Active Employees =
CALCULATE(
    COUNTROWS(fact_employees),
    fact_employees[is_attrition] = 0
)
```

```dax
Total Attritions =
CALCULATE(
    COUNTROWS(fact_employees),
    fact_employees[is_attrition] = 1
)
```

```dax
Attrition Rate % =
DIVIDE([Total Attritions], [Total Headcount], 0) * 100
```

```dax
Retention Rate % =
100 - [Attrition Rate %]
```

```dax
Avg Tenure (Years) =
AVERAGE(fact_employees[tenure_years])
```

```dax
Avg Experience (Years) =
AVERAGE(fact_employees[total_experience])
```

```dax
Avg Estimated Age =
AVERAGE(fact_employees[estimated_age])
```

```dax
Male Count =
CALCULATE(COUNTROWS(fact_employees), fact_employees[gender] = "Male")
```

```dax
Female Count =
CALCULATE(COUNTROWS(fact_employees), fact_employees[gender] = "Female")
```

```dax
Female % =
DIVIDE([Female Count], [Total Headcount], 0) * 100
```

```dax
Attrition Risk Label =
SWITCH(
    TRUE(),
    [Attrition Rate %] >= 40, "High Risk",
    [Attrition Rate %] >= 25, "Medium Risk",
    "Low Risk"
)
```

---

## Step 5 — Build Page 1: Executive Summary

1. Rename the default page: double-click tab → type **"Executive Summary"**
2. Change canvas background (optional): View → Canvas background → Color #F5F5F5

### Add KPI Cards (top row)
For each card: **Insert → Card visual** → drag the measure into the **Fields** well.

| Card | Measure | Format |
|------|---------|--------|
| Card 1 | `[Total Headcount]` | No decimal |
| Card 2 | `[Active Employees]` | No decimal |
| Card 3 | `[Total Attritions]` | No decimal |
| Card 4 | `[Attrition Rate %]` | 1 decimal, add "%" suffix |
| Card 5 | `[Retention Rate %]` | 1 decimal, add "%" suffix |
| Card 6 | `[Avg Tenure (Years)]` | 1 decimal |

> To format a card: click it → Format pane → Callout value → set decimal places

### Add Donut Charts (middle row)

**Gender donut:**
- Visual: Donut Chart
- Legend: `fact_employees[gender]`
- Values: `[Total Headcount]`
- Title: "Gender Distribution"
- Colors: Male = #2980B9, Female = #E74C3C

**Marital Status donut:**
- Visual: Donut Chart
- Legend: `fact_employees[marital_status]`
- Values: `[Total Headcount]`
- Title: "Marital Status"

### Add Bar Chart — Department Headcount

- Visual: Clustered Bar Chart
- Y-axis: `fact_employees[department]`
- X-axis: `[Total Headcount]`
- Title: "Headcount by Department"
- Sort: descending by headcount

### Add Slicers (right column)

Add one slicer for each field:
- `fact_employees[grade]` — style: Tile
- `fact_employees[department]` — style: Dropdown
- `fact_employees[gender]` — style: Tile
- `fact_employees[visa_type]` — style: Dropdown
- `fact_employees[hire_year]` — style: Tile or Between

---

## Step 6 — Build Page 2: Attrition Analysis

Add new page, rename **"Attrition Analysis"**

### Attrition Rate by Department (bar chart)
- Visual: Clustered Bar Chart
- Y-axis: `fact_employees[department]`
- X-axis: `[Attrition Rate %]`
- Title: "Attrition Rate by Department"
- Sort: descending
- Add data labels: on

### Attrition by Grade (bar chart)
- Y-axis: `fact_employees[grade]`
- X-axis: `[Attrition Rate %]`
- Title: "Attrition Rate by Grade"

### Attrition by Tenure Band (column chart)
- X-axis: `fact_employees[tenure_band]`
- Y-axis: `[Attrition Rate %]`
- Title: "Attrition by Tenure"

### Attrition by Age Group (column chart)
- X-axis: `fact_employees[age_group]`
- Y-axis: `[Attrition Rate %]`
- Title: "Attrition by Age Group"

### Attrition by Visa Type (bar chart)
- Y-axis: `fact_employees[visa_type]`
- X-axis: `[Attrition Rate %]`
- Title: "Attrition by Visa Type"

### Matrix — Department × Grade breakdown
- Rows: `fact_employees[department]`
- Columns: `fact_employees[grade]`
- Values: `[Attrition Rate %]`, `[Total Headcount]`
- Enable Conditional Formatting on Attrition Rate % (background color: red-green diverging)

---

## Step 7 — Build Page 3: Workforce Profile

Rename page **"Workforce Profile"**

### Age Group Distribution (column chart)
- X-axis: `fact_employees[age_group]`
- Y-axis: `[Total Headcount]`
- Title: "Age Group Distribution"

### Tenure Band Distribution (column chart)
- X-axis: `fact_employees[tenure_band]`
- Y-axis: `[Total Headcount]`
- Title: "Tenure Distribution"

### Stability Score (column chart)
- X-axis: `fact_employees[stability]`
- Y-axis: `[Total Headcount]`

### Gender × Department (stacked bar)
- Y-axis: `fact_employees[department]`
- X-axis: `[Total Headcount]`
- Legend: `fact_employees[gender]`
- Title: "Headcount by Department & Gender"

### Grade × Employee Type (stacked bar)
- Y-axis: `fact_employees[grade]`
- X-axis: `[Total Headcount]`
- Legend: `fact_employees[employee_type]`

### Visa Type table
- Visual: Table
- Columns: from `dim_gender_kpis` or use `fact_employees[visa_type]`, `[Total Headcount]`, `[Attrition Rate %]`

---

## Step 8 — Build Page 4: Hiring Trend

Rename page **"Hiring Trend"**

### Hiring by Year (line chart)
- Visual: Line Chart
- X-axis: `dim_hiring_trend[hire_year]`
- Y-axis: `dim_hiring_trend[new_hires]`
- Title: "New Hires per Year"
- Add data labels

### Hiring by Month × Year (clustered column)
- X-axis: `dim_hiring_trend[hire_month]`
- Y-axis: `dim_hiring_trend[new_hires]`
- Legend: `dim_hiring_trend[hire_year]`
- Title: "Monthly Hiring Pattern"

---

## Step 9 — Build Page 5: Manager Scoreboard

Rename page **"Manager Scoreboard"**

### Manager table
- Visual: Table
- Source: `dim_manager_scoreboard`
- Columns: `reporting_manager`, `headcount`, `attritions`, `attrition_rate_pct`
- Sort: `attrition_rate_pct` descending
- Add conditional formatting on `attrition_rate_pct` (background: red/green)

### Manager attrition bar chart
- Visual: Clustered Bar Chart
- Y-axis: `dim_manager_scoreboard[reporting_manager]`
- X-axis: `dim_manager_scoreboard[attrition_rate_pct]`
- Title: "Attrition Rate by Manager"
- Sort descending

---

## Step 10 — Final Styling

1. **Theme**: View → Themes → choose "Executive" or "Innovate"
2. **Title bar**: Insert → Text Box at the top of each page
   - Page 1 title: `HR Analytics Dashboard — Executive Summary`
   - Use font: Segoe UI, size 18, bold, color #1A1A2E
3. **Company logo placeholder**: Insert → Image → add a placeholder
4. **Background**: Format pane → Canvas background → #F8F9FA (light grey)

---

## Refresh data in future

When you re-run the Python scripts and new CSVs are generated:

1. Power BI Desktop → **Home → Refresh**
2. All visuals update automatically from the CSV files

If you later connect to SQL Server instead:
1. **Home → Get Data → SQL Server**
2. Server: `localhost` (or your SQL Server name)
3. Database: `HRAnalytics`
4. Connect to the views: `vw_ActiveEmployees`, `vw_DepartmentKPIs`, etc.
5. Delete the CSV-based tables and recreate relationships
