"""Data quality checks for the SQL mart."""

from __future__ import annotations

import sqlite3

from patient_journey_sql_mart.config import MART_TABLES, SOURCE_TABLES


def table_count(connection: sqlite3.Connection, table_name: str) -> int:
    cursor = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
    return int(cursor.fetchone()[0])


def run_quality_checks(connection: sqlite3.Connection) -> dict[str, int]:
    """Run basic data quality checks and raise on failed invariants."""
    counts = {table: table_count(connection, table) for table in SOURCE_TABLES + MART_TABLES}

    if counts["src_patients"] <= 0:
        raise ValueError("No patients loaded.")
    if counts["src_encounters"] < counts["src_patients"]:
        raise ValueError("Encounter count should be at least patient count.")
    if counts["dim_patient"] != counts["src_patients"]:
        raise ValueError("dim_patient row count must match src_patients.")
    if counts["fact_encounter"] != counts["src_encounters"]:
        raise ValueError("fact_encounter row count must match src_encounters.")
    if counts["mart_patient_journey"] != counts["src_patients"]:
        raise ValueError("mart_patient_journey row count must match src_patients.")

    invalid_readmission = connection.execute(
        """
        SELECT COUNT(*)
        FROM mart_readmission_30d
        WHERE readmitted_30d NOT IN (0, 1)
        """
    ).fetchone()[0]
    if invalid_readmission:
        raise ValueError("Invalid readmission flags found.")

    return counts

