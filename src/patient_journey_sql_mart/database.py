"""SQLite database build orchestration."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from patient_journey_sql_mart.config import DEFAULT_DATABASE_PATH, SQL_DIR
from patient_journey_sql_mart.data import SourceData, generate_source_data
from patient_journey_sql_mart.quality import run_quality_checks


def read_sql_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def execute_sql_file(connection: sqlite3.Connection, path: Path) -> None:
    connection.executescript(read_sql_file(path))


def load_source_tables(connection: sqlite3.Connection, source_data: SourceData) -> None:
    source_data.patients.to_sql("src_patients", connection, if_exists="append", index=False)
    source_data.encounters.to_sql("src_encounters", connection, if_exists="append", index=False)
    source_data.lab_orders.to_sql("src_lab_orders", connection, if_exists="append", index=False)
    source_data.claims.to_sql("src_claims", connection, if_exists="append", index=False)


def build_database(database_path: Path, patient_count: int = 1500, seed: int = 42) -> dict[str, int]:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()

    source_data = generate_source_data(patient_count=patient_count, seed=seed)
    with sqlite3.connect(database_path) as connection:
        execute_sql_file(connection, SQL_DIR / "01_schema.sql")
        load_source_tables(connection, source_data)
        execute_sql_file(connection, SQL_DIR / "02_mart.sql")
        checks = run_quality_checks(connection)
        connection.commit()
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Patient Journey SQL Mart SQLite database.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--patients", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    checks = build_database(args.database, patient_count=args.patients, seed=args.seed)
    print(f"Built database at {args.database}")
    for name, value in checks.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()

