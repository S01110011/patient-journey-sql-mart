DROP TABLE IF EXISTS mart_patient_journey;
DROP TABLE IF EXISTS mart_readmission_30d;
DROP TABLE IF EXISTS fact_lab_order;
DROP TABLE IF EXISTS fact_encounter;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_patient;

CREATE TABLE dim_patient AS
SELECT
    patient_id,
    birth_date,
    CAST((julianday('2026-01-01') - julianday(birth_date)) / 365.25 AS INTEGER) AS age_years,
    sex,
    city,
    risk_segment,
    registered_date
FROM src_patients;

CREATE TABLE dim_date AS
WITH RECURSIVE date_series(calendar_date) AS (
    SELECT DATE((SELECT MIN(admit_datetime) FROM src_encounters))
    UNION ALL
    SELECT DATE(calendar_date, '+1 day')
    FROM date_series
    WHERE calendar_date < DATE((SELECT MAX(discharge_datetime) FROM src_encounters))
)
SELECT
    calendar_date,
    CAST(strftime('%Y', calendar_date) AS INTEGER) AS year,
    CAST(strftime('%m', calendar_date) AS INTEGER) AS month,
    CAST(strftime('%W', calendar_date) AS INTEGER) AS week_of_year,
    strftime('%Y-%m', calendar_date) AS year_month
FROM date_series;

CREATE TABLE fact_encounter AS
SELECT
    e.encounter_id,
    e.patient_id,
    DATE(e.admit_datetime) AS admit_date,
    DATE(e.discharge_datetime) AS discharge_date,
    e.encounter_type,
    e.service_line,
    e.primary_diagnosis_code,
    e.discharge_disposition,
    ROUND((julianday(e.discharge_datetime) - julianday(e.admit_datetime)) * 24, 2) AS length_of_stay_hours,
    ROUND(COALESCE(c.allowed_amount, 0), 2) AS allowed_amount,
    COALESCE(c.denied_flag, 0) AS denied_flag
FROM src_encounters e
LEFT JOIN src_claims c
    ON e.encounter_id = c.encounter_id;

CREATE TABLE fact_lab_order AS
SELECT
    lab_order_id,
    encounter_id,
    patient_id,
    DATE(order_datetime) AS order_date,
    lab_test,
    result_value,
    result_status,
    CASE WHEN result_status IN ('high', 'low', 'critical') THEN 1 ELSE 0 END AS abnormal_flag
FROM src_lab_orders;

CREATE TABLE mart_readmission_30d AS
WITH ordered_encounters AS (
    SELECT
        encounter_id,
        patient_id,
        encounter_type,
        service_line,
        admit_date,
        discharge_date,
        LEAD(admit_date) OVER (
            PARTITION BY patient_id
            ORDER BY admit_date, encounter_id
        ) AS next_admit_date,
        LEAD(encounter_id) OVER (
            PARTITION BY patient_id
            ORDER BY admit_date, encounter_id
        ) AS next_encounter_id
    FROM fact_encounter
)
SELECT
    encounter_id,
    patient_id,
    encounter_type,
    service_line,
    admit_date,
    discharge_date,
    next_encounter_id,
    next_admit_date,
    CASE
        WHEN next_admit_date IS NOT NULL
         AND julianday(next_admit_date) - julianday(discharge_date) BETWEEN 1 AND 30
        THEN 1
        ELSE 0
    END AS readmitted_30d
FROM ordered_encounters;

CREATE TABLE mart_patient_journey AS
WITH encounter_rollup AS (
    SELECT
        patient_id,
        MIN(admit_date) AS first_encounter_date,
        MAX(discharge_date) AS last_encounter_date,
        COUNT(*) AS total_encounters,
        SUM(CASE WHEN encounter_type = 'emergency' THEN 1 ELSE 0 END) AS emergency_visits,
        SUM(CASE WHEN encounter_type = 'inpatient' THEN 1 ELSE 0 END) AS inpatient_stays,
        SUM(CASE WHEN encounter_type = 'outpatient' THEN 1 ELSE 0 END) AS outpatient_visits,
        SUM(length_of_stay_hours) AS total_los_hours,
        SUM(allowed_amount) AS total_cost,
        MAX(CASE WHEN discharge_disposition = 'death' THEN 1 ELSE 0 END) AS mortality_flag
    FROM fact_encounter
    GROUP BY patient_id
),
lab_rollup AS (
    SELECT
        patient_id,
        COUNT(*) AS total_lab_orders,
        SUM(abnormal_flag) AS abnormal_lab_orders
    FROM fact_lab_order
    GROUP BY patient_id
),
readmission_rollup AS (
    SELECT
        patient_id,
        MAX(readmitted_30d) AS readmitted_30d,
        SUM(readmitted_30d) AS readmission_events
    FROM mart_readmission_30d
    GROUP BY patient_id
)
SELECT
    p.patient_id,
    p.age_years,
    p.sex,
    p.city,
    p.risk_segment,
    e.first_encounter_date,
    e.last_encounter_date,
    e.total_encounters,
    e.emergency_visits,
    e.inpatient_stays,
    e.outpatient_visits,
    ROUND(e.total_los_hours / 24.0, 2) AS total_los_days,
    ROUND(e.total_cost, 2) AS total_cost,
    COALESCE(l.total_lab_orders, 0) AS total_lab_orders,
    COALESCE(l.abnormal_lab_orders, 0) AS abnormal_lab_orders,
    COALESCE(r.readmitted_30d, 0) AS readmitted_30d,
    COALESCE(r.readmission_events, 0) AS readmission_events,
    e.mortality_flag,
    CASE
        WHEN e.total_encounters >= 6 OR e.total_cost >= 45000 THEN 1
        ELSE 0
    END AS high_utilizer_flag
FROM dim_patient p
JOIN encounter_rollup e
    ON p.patient_id = e.patient_id
LEFT JOIN lab_rollup l
    ON p.patient_id = l.patient_id
LEFT JOIN readmission_rollup r
    ON p.patient_id = r.patient_id;

CREATE INDEX idx_fact_encounter_patient ON fact_encounter(patient_id);
CREATE INDEX idx_fact_encounter_date ON fact_encounter(admit_date);
CREATE INDEX idx_fact_lab_patient ON fact_lab_order(patient_id);
CREATE INDEX idx_mart_journey_risk ON mart_patient_journey(risk_segment);

