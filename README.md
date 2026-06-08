# Patient Journey SQL Mart

Patient Journey SQL Mart is a professional healthtech data engineering project that builds an analytical SQL mart for longitudinal patient journeys.

It uses Python to generate safe synthetic healthcare data, load it into SQLite, execute versioned SQL transformations and export analytics-ready tables. The SQL layer models the journey across appointments, encounters, lab orders, admissions, discharges, readmissions and claims.

## Clinical And Hospital Challenge

Hospitals and healthtechs often store patient activity across fragmented operational systems. This project consolidates those events into a patient-centered analytical mart to answer questions such as:

- Which patients had emergency visits followed by admission?
- What is the 30-day readmission rate by service line?
- How long does it take from first appointment to diagnosis?
- Which patients have high utilization across care settings?
- What is the longitudinal timeline of each patient's care journey?

## What This Project Demonstrates

- Healthcare data modeling
- Dimensional SQL mart design
- Synthetic EHR-like data generation
- SQLite-based local analytics warehouse
- Reproducible ETL orchestration in Python
- Versioned SQL transformations
- Data quality checks and automated tests
- GitHub Actions CI

## Project Structure

```text
patient-journey-sql-mart/
├── data/
│   └── README.md
├── docs/
│   ├── data_dictionary.md
│   └── mart_design.md
├── sql/
│   ├── 01_schema.sql
│   ├── 02_mart.sql
│   └── 03_analytics.sql
├── src/
│   └── patient_journey_sql_mart/
│       ├── __init__.py
│       ├── config.py
│       ├── data.py
│       ├── database.py
│       ├── quality.py
│       └── reporting.py
├── tests/
│   ├── test_data.py
│   └── test_mart.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── pyproject.toml
└── README.md
```

## Quickstart

From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Build the SQLite mart:

```powershell
python -m patient_journey_sql_mart.database --database data/patient_journey.db --patients 1500
```

Export analytics tables:

```powershell
python -m patient_journey_sql_mart.reporting --database data/patient_journey.db --output data/exports
```

Run tests and lint:

```powershell
python -m pytest
python -m ruff check .
```

## Example SQL

Open the SQLite database with your preferred SQL client and query:

```sql
SELECT *
FROM mart_patient_journey
WHERE readmitted_30d = 1
ORDER BY total_cost DESC
LIMIT 20;
```

## Portfolio Note

This project uses synthetic data only. It is safe for public GitHub and demonstrates the structure, practices and analytical thinking expected in healthcare data engineering roles.

