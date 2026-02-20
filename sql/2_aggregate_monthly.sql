DROP VIEW IF EXISTS crime_monthly_neighbourhood;

CREATE VIEW crime_monthly_neighbourhood AS
SELECT
    neighbourhood,
    year,
    month,
    COUNT(*) AS incident_count
FROM crime_incidents_raw
WHERE year BETWEEN 2016 AND 2025
GROUP BY neighbourhood, year, month
ORDER BY neighbourhood, year, month;