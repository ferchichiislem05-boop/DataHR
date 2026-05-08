-- ============================================================
--  HR Analytics — SQL Server Schema
--  Run this ONCE to create the database and table.
--  Then import hr_cleaned.csv using SSMS Import Wizard or BULK INSERT.
-- ============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HRAnalytics')
BEGIN
    CREATE DATABASE HRAnalytics;
    PRINT 'Database HRAnalytics created.';
END
GO

USE HRAnalytics;
GO

-- Drop if re-running
IF OBJECT_ID('dbo.Employees', 'U') IS NOT NULL DROP TABLE dbo.Employees;

CREATE TABLE dbo.Employees (
    employee_id         NVARCHAR(50)   NOT NULL,
    employee_name       NVARCHAR(150),
    employee_status     NVARCHAR(50),
    movement            NVARCHAR(50),
    date_of_joining     DATE,
    reporting_manager   NVARCHAR(150),
    employee_type       NVARCHAR(50),
    category            NVARCHAR(100),
    date_of_birth       DATE,
    marital_status      NVARCHAR(50),
    grade               NVARCHAR(20),
    department          NVARCHAR(100),
    experience          NVARCHAR(50),
    stability           NVARCHAR(50),
    visa_type           NVARCHAR(50),
    gender              NVARCHAR(20),
    age                 DECIMAL(5,1),
    tenure_years        DECIMAL(6,2),
    age_group           NVARCHAR(20),
    tenure_band         NVARCHAR(20),
    is_attrition        TINYINT        DEFAULT 0,
    CONSTRAINT PK_Employees PRIMARY KEY (employee_id)
);
GO

PRINT 'Table dbo.Employees created successfully.';
GO
