"""Project configuration."""

from pathlib import Path

RANDOM_STATE = 42
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = PROJECT_ROOT / "sql"
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "patient_journey.db"
DEFAULT_EXPORT_DIR = PROJECT_ROOT / "data" / "exports"

SOURCE_TABLES = ["src_patients", "src_encounters", "src_lab_orders", "src_claims"]
MART_TABLES = [
    "dim_patient",
    "dim_date",
    "fact_encounter",
    "fact_lab_order",
    "mart_readmission_30d",
    "mart_patient_journey",
]

