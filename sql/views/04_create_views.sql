-- ============================================================
--  HR Analytics — Reusable SQL Views for Power BI
--  Connect Power BI directly to these views.
-- ============================================================

USE HRAnalytics;
GO

-- ── View 1: Active Employees ──────────────────────────────────
CREATE OR ALTER VIEW vw_ActiveEmployees AS
SELECT *
FROM dbo.Employees
WHERE is_attrition = 0;
GO

-- ── View 2: Department KPIs ───────────────────────────────────
CREATE OR ALTER VIEW vw_DepartmentKPIs AS
SELECT
    department,
    COUNT(*)                                                      AS headcount,
    SUM(is_attrition)                                             AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct,
    CAST(AVG(tenure_years) AS DECIMAL(5,2))                       AS avg_tenure_years,
    CAST(AVG(age)          AS DECIMAL(5,1))                       AS avg_age
FROM dbo.Employees
GROUP BY department;
GO

-- ── View 3: Attrition Analysis ────────────────────────────────
CREATE OR ALTER VIEW vw_AttritionAnalysis AS
SELECT
    department,
    grade,
    age_group,
    tenure_band,
    marital_status,
    gender,
    visa_type,
    employee_type,
    COUNT(*)          AS headcount,
    SUM(is_attrition) AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct
FROM dbo.Employees
GROUP BY
    department, grade, age_group, tenure_band,
    marital_status, gender, visa_type, employee_type;
GO

-- ── View 4: Hiring Trend ──────────────────────────────────────
CREATE OR ALTER VIEW vw_HiringTrend AS
SELECT
    YEAR(date_of_joining)  AS hire_year,
    MONTH(date_of_joining) AS hire_month,
    department,
    employee_type,
    COUNT(*)               AS new_hires,
    SUM(is_attrition)      AS already_left
FROM dbo.Employees
WHERE date_of_joining IS NOT NULL
GROUP BY
    YEAR(date_of_joining),
    MONTH(date_of_joining),
    department,
    employee_type;
GO

-- ── View 5: Manager Scoreboard ────────────────────────────────
CREATE OR ALTER VIEW vw_ManagerScoreboard AS
SELECT
    reporting_manager,
    COUNT(*)                                                      AS team_size,
    SUM(is_attrition)                                             AS attritions,
    CAST(AVG(CAST(is_attrition AS FLOAT)) * 100 AS DECIMAL(5,2)) AS attrition_rate_pct,
    CAST(AVG(tenure_years) AS DECIMAL(5,2))                       AS avg_team_tenure
FROM dbo.Employees
WHERE reporting_manager IS NOT NULL
GROUP BY reporting_manager;
GO

PRINT 'All views created successfully.';
GO
