-- High-utilization patients by total cost and encounter volume.
SELECT
    patient_id,
    risk_segment,
    total_encounters,
    emergency_visits,
    inpatient_stays,
    total_cost,
    readmitted_30d,
    high_utilizer_flag
FROM mart_patient_journey
WHERE high_utilizer_flag = 1
ORDER BY total_cost DESC, total_encounters DESC
LIMIT 25;

-- 30-day readmission rate by service line.
SELECT
    service_line,
    COUNT(*) AS index_encounters,
    SUM(readmitted_30d) AS readmissions_30d,
    ROUND(1.0 * SUM(readmitted_30d) / COUNT(*), 4) AS readmission_rate
FROM mart_readmission_30d
GROUP BY service_line
ORDER BY readmission_rate DESC;

-- Monthly encounter volume and cost.
SELECT
    d.year_month,
    f.service_line,
    COUNT(*) AS encounters,
    ROUND(SUM(f.allowed_amount), 2) AS allowed_amount
FROM fact_encounter f
JOIN dim_date d
    ON f.admit_date = d.calendar_date
GROUP BY d.year_month, f.service_line
ORDER BY d.year_month, f.service_line;

