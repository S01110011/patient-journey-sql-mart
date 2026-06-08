import sqlite3

import pandas as pd

from patient_journey_sql_mart.database import build_database
from patient_journey_sql_mart.quality import run_quality_checks


def test_build_database_creates_expected_mart_tables(tmp_path):
    database_path = tmp_path / "patient_journey.db"
    counts = build_database(database_path, patient_count=120, seed=456)

    assert database_path.exists()
    assert counts["src_patients"] == 120
    assert counts["dim_patient"] == 120
    assert counts["mart_patient_journey"] == 120


def test_mart_supports_readmission_analytics(tmp_path):
    database_path = tmp_path / "patient_journey.db"
    build_database(database_path, patient_count=120, seed=789)

    with sqlite3.connect(database_path) as connection:
        checks = run_quality_checks(connection)
        summary = pd.read_sql_query(
            """
            SELECT
                service_line,
                COUNT(*) AS encounters,
                SUM(readmitted_30d) AS readmissions
            FROM mart_readmission_30d
            GROUP BY service_line
            """,
            connection,
        )

    assert checks["fact_encounter"] >= 120
    assert not summary.empty
    assert {"service_line", "encounters", "readmissions"}.issubset(summary.columns)

