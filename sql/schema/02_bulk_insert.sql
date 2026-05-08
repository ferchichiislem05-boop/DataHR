-- ============================================================
--  HR Analytics — Import cleaned CSV into SQL Server
--  Edit the file path below to match your machine.
-- ============================================================

USE HRAnalytics;
GO

BULK INSERT dbo.Employees
FROM 'C:\Users\ferch\OneDrive\Desktop\Data\hr-analytics\data\processed\hr_cleaned.csv'
WITH (
    FORMAT          = 'CSV',
    FIRSTROW        = 2,           -- skip header row
    FIELDTERMINATOR = ',',
    ROWTERMINATOR   = '\n',
    TABLOCK
);
GO

-- Quick sanity check
SELECT TOP 10 * FROM dbo.Employees;
SELECT COUNT(*) AS total_rows FROM dbo.Employees;
GO
