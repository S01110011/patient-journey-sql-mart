"""Export reusable analytics tables from the SQL mart."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from patient_journey_sql_mart.config import DEFAULT_DATABASE_PATH, DEFAULT_EXPORT_DIR
from patient_journey_sql_mart.database import build_database


REPORT_QUERIES = {
    "patient_journey": "SELECT * FROM mart_patient_journey",
    "readmission_by_service_line": """
        SELECT
            service_line,
            COUNT(*) AS index_encounters,
            SUM(readmitted_30d) AS readmissions_30d,
            ROUND(1.0 * SUM(readmitted_30d) / COUNT(*), 4) AS readmission_rate
        FROM mart_readmission_30d
        GROUP BY service_line
        ORDER BY readmission_rate DESC
    """,
    "high_utilizers": """
        SELECT *
        FROM mart_patient_journey
        WHERE high_utilizer_flag = 1
        ORDER BY total_cost DESC, total_encounters DESC
    """,
}


def export_reports(database_path: Path, output_dir: Path) -> list[Path]:
    if not database_path.exists():
        build_database(database_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    exported_paths = []
    with sqlite3.connect(database_path) as connection:
        for report_name, query in REPORT_QUERIES.items():
            frame = pd.read_sql_query(query, connection)
            output_path = output_dir / f"{report_name}.csv"
            frame.to_csv(output_path, index=False)
            exported_paths.append(output_path)
    return exported_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Patient Journey SQL Mart report tables.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_EXPORT_DIR)
    args = parser.parse_args()

    paths = export_reports(args.database, args.output)
    for path in paths:
        print(f"Exported {path}")


if __name__ == "__main__":
    main()

