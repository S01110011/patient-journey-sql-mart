# Mart Design

The mart follows a lightweight dimensional model suitable for analytics and BI tools.

## Grain

The primary grains are:

- One row per patient in `dim_patient`
- One row per encounter in `fact_encounter`
- One row per lab order in `fact_lab_order`
- One row per patient in `mart_patient_journey`

## Modeling Choices

SQLite is used so the project runs locally without external services. The SQL files are intentionally separated:

- `01_schema.sql` creates source and mart tables
- `02_mart.sql` builds analytical tables
- `03_analytics.sql` contains reusable reporting queries

## Analytical Use Cases

The mart supports:

- Longitudinal patient timelines
- 30-day readmission analytics
- Emergency-to-inpatient conversion analysis
- High-utilization patient identification
- Service-line cost and outcome summaries
- Lab abnormality burden by journey

