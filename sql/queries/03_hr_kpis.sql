-- ============================================================
--  HR Analytics — Core KPI Queries
--  Run after data is imported into dbo.Employees
-- ============================================================

USE HRAnalytics;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 1: Headcount Summary
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                        AS total_headcount,
    SUM(CASE WHEN is_attrition = 0 THEN 1 ELSE 0 END) AS active_employees,
    SUM(is_attrition)                               AS total_attritions,
    CAST(
        SUM(is_attrition) * 100.0 / COUNT(*)
    AS DECIMAL(5,2))                                AS attrition_rate_pct
FROM dbo.Employees;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 2: Attrition by Department
-- ────────────────────────────────────────────────────────────
SELECT
    department,
    COUNT(*)                                              AS headcount,
    SUM(is_attrition)                                     AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct,
    CAST(AVG(tenure_years) AS DECIMAL(5,2))               AS avg_tenure_years,
    CAST(AVG(age)          AS DECIMAL(5,1))               AS avg_age
FROM dbo.Employees
GROUP BY department
ORDER BY attrition_rate_pct DESC;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 3: Attrition by Grade
-- ────────────────────────────────────────────────────────────
SELECT
    grade,
    COUNT(*)                                                      AS headcount,
    SUM(is_attrition)                                             AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY grade
ORDER BY grade;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 4: Attrition by Tenure Band
-- ────────────────────────────────────────────────────────────
SELECT
    tenure_band,
    COUNT(*)                                                      AS headcount,
    SUM(is_attrition)                                             AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY tenure_band
ORDER BY tenure_band;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 5: Attrition by Age Group
-- ────────────────────────────────────────────────────────────
SELECT
    age_group,
    COUNT(*)                                                      AS headcount,
    SUM(is_attrition)                                             AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY age_group
ORDER BY age_group;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 6: Gender Distribution
-- ────────────────────────────────────────────────────────────
SELECT
    gender,
    COUNT(*)                                     AS headcount,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) AS pct_of_total
FROM dbo.Employees
GROUP BY gender
ORDER BY headcount DESC;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 7: Hiring Trend by Year
-- ────────────────────────────────────────────────────────────
SELECT
    YEAR(date_of_joining) AS hire_year,
    COUNT(*)              AS new_hires
FROM dbo.Employees
WHERE date_of_joining IS NOT NULL
GROUP BY YEAR(date_of_joining)
ORDER BY hire_year;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 8: Manager Headcount & Attrition
-- ────────────────────────────────────────────────────────────
SELECT
    reporting_manager,
    COUNT(*)                                                      AS team_size,
    SUM(is_attrition)                                             AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
WHERE reporting_manager IS NOT NULL
GROUP BY reporting_manager
HAVING COUNT(*) >= 3           -- only managers with 3+ reports
ORDER BY attrition_rate_pct DESC;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 9: Employee Type & Category Mix
-- ────────────────────────────────────────────────────────────
SELECT
    employee_type,
    category,
    COUNT(*) AS headcount,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY employee_type, category
ORDER BY headcount DESC;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 10: Marital Status vs Attrition
-- ────────────────────────────────────────────────────────────
SELECT
    marital_status,
    COUNT(*) AS headcount,
    SUM(is_attrition) AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY marital_status
ORDER BY attrition_rate_pct DESC;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 11: Visa Type Distribution
-- ────────────────────────────────────────────────────────────
SELECT
    visa_type,
    COUNT(*) AS headcount,
    SUM(is_attrition) AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY visa_type
ORDER BY headcount DESC;
GO

-- ────────────────────────────────────────────────────────────
-- KPI 12: Stability Score Distribution
-- ────────────────────────────────────────────────────────────
SELECT
    stability,
    COUNT(*) AS headcount,
    SUM(is_attrition) AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY stability
ORDER BY stability;
GO
