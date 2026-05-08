# Power BI DAX Measures — HR Analytics
# All measures reference the table named: fact_employees

---

## 1. Headcount

```dax
Total Headcount =
COUNTROWS(fact_employees)

Active Employees =
CALCULATE(
    COUNTROWS(fact_employees),
    fact_employees[is_attrition] = 0
)

Total Attritions =
CALCULATE(
    COUNTROWS(fact_employees),
    fact_employees[is_attrition] = 1
)
```

---

## 2. Attrition & Retention

```dax
Attrition Rate % =
DIVIDE([Total Attritions], [Total Headcount], 0) * 100

Retention Rate % =
100 - [Attrition Rate %]

Attrition Risk Label =
SWITCH(
    TRUE(),
    [Attrition Rate %] >= 40, "High Risk",
    [Attrition Rate %] >= 25, "Medium Risk",
    "Low Risk"
)
```

---

## 3. Tenure

```dax
Avg Tenure (Years) =
AVERAGE(fact_employees[tenure_years])

Avg Tenure Active =
CALCULATE(
    AVERAGE(fact_employees[tenure_years]),
    fact_employees[is_attrition] = 0
)

Avg Tenure Attrited =
CALCULATE(
    AVERAGE(fact_employees[tenure_years]),
    fact_employees[is_attrition] = 1
)
```

---

## 4. Experience

```dax
Avg Experience (Years) =
AVERAGE(fact_employees[total_experience])

Avg Estimated Age =
AVERAGE(fact_employees[estimated_age])
```

---

## 5. Gender

```dax
Male Count =
CALCULATE(COUNTROWS(fact_employees), fact_employees[gender] = "Male")

Female Count =
CALCULATE(COUNTROWS(fact_employees), fact_employees[gender] = "Female")

Female % =
DIVIDE([Female Count], [Total Headcount], 0) * 100
```

---

## 6. Hiring trend helpers

```dax
New Hires =
CALCULATE(
    COUNTROWS(fact_employees),
    NOT ISBLANK(fact_employees[date_of_joining])
)
```

---

## 7. Conditional formatting measure (for matrix cells)

```dax
Attrition Color =
VAR rate = [Attrition Rate %]
RETURN
    SWITCH(
        TRUE(),
        rate >= 40, "#C0392B",   -- red
        rate >= 25, "#E67E22",   -- orange
        "#27AE60"                 -- green
    )
```

---

## Recommended Dashboard Pages

### Page 1 — Executive Summary
| Visual          | Fields                                                    |
|-----------------|-----------------------------------------------------------|
| KPI Card        | [Total Headcount]                                         |
| KPI Card        | [Active Employees]                                        |
| KPI Card        | [Attrition Rate %]                                        |
| KPI Card        | [Retention Rate %]                                        |
| KPI Card        | [Avg Tenure (Years)]                                      |
| KPI Card        | [Avg Experience (Years)]                                  |
| Donut Chart     | gender → values: [Total Headcount]                        |
| Donut Chart     | marital_status → values: [Total Headcount]                |
| Bar Chart       | department → values: [Total Headcount]                    |
| Slicer          | grade, department, gender, visa_type, hire_year           |

### Page 2 — Attrition Analysis
| Visual          | Fields                                                    |
|-----------------|-----------------------------------------------------------|
| Bar Chart       | department → values: [Attrition Rate %]                   |
| Bar Chart       | grade → values: [Attrition Rate %]                        |
| Bar Chart       | tenure_band → values: [Attrition Rate %]                  |
| Bar Chart       | age_group → values: [Attrition Rate %]                    |
| Clustered Bar   | marital_status + gender → values: [Attrition Rate %]      |
| Bar Chart       | visa_type → values: [Attrition Rate %]                    |
| Matrix          | department (rows) + grade (cols) → [Attrition Rate %]     |

### Page 3 — Workforce Profile
| Visual          | Fields                                                    |
|-----------------|-----------------------------------------------------------|
| Column Chart    | age_group → values: [Total Headcount]                     |
| Column Chart    | tenure_band → values: [Total Headcount]                   |
| Column Chart    | stability → values: [Total Headcount]                     |
| Stacked Bar     | department + gender → [Total Headcount]                   |
| Stacked Bar     | grade + employee_type → [Total Headcount]                 |
| Table           | visa_type, headcount, attrition_rate_pct                  |

### Page 4 — Hiring Trend
| Visual          | Fields (use dim_hiring_trend table)                       |
|-----------------|-----------------------------------------------------------|
| Line Chart      | hire_year → values: new_hires                             |
| Column Chart    | hire_year + hire_month → new_hires                        |

### Page 5 — Manager Scoreboard
| Visual          | Fields (use dim_manager_scoreboard table)                 |
|-----------------|-----------------------------------------------------------|
| Table / Matrix  | reporting_manager, headcount, attritions, attrition_rate  |
| Bar Chart       | reporting_manager → attrition_rate_pct                    |
