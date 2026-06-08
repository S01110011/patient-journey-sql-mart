"""Synthetic source data generation for patient journey analytics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from patient_journey_sql_mart.config import RANDOM_STATE


@dataclass(frozen=True)
class SourceData:
    patients: pd.DataFrame
    encounters: pd.DataFrame
    lab_orders: pd.DataFrame
    claims: pd.DataFrame


def generate_source_data(patient_count: int = 1500, seed: int = RANDOM_STATE) -> SourceData:
    """Generate relational synthetic healthcare source data."""
    rng = np.random.default_rng(seed)
    patients = _generate_patients(patient_count, rng)
    encounters = _generate_encounters(patients, rng)
    lab_orders = _generate_lab_orders(encounters, rng)
    claims = _generate_claims(encounters, rng)
    return SourceData(patients=patients, encounters=encounters, lab_orders=lab_orders, claims=claims)


def _generate_patients(patient_count: int, rng: np.random.Generator) -> pd.DataFrame:
    base_date = datetime(2026, 1, 1)
    ages = np.clip(rng.normal(56, 22, patient_count), 0, 96).round().astype(int)
    birth_dates = [base_date - timedelta(days=int(age * 365.25)) for age in ages]
    cities = ["Sao Paulo", "Campinas", "Santos", "Sorocaba", "Guarulhos", "Osasco"]
    risk_segments = ["low", "moderate", "high", "complex"]

    return pd.DataFrame(
        {
            "patient_id": [f"PAT-{idx:06d}" for idx in range(1, patient_count + 1)],
            "birth_date": [item.date().isoformat() for item in birth_dates],
            "sex": rng.choice(["F", "M"], patient_count, p=[0.53, 0.47]),
            "city": rng.choice(cities, patient_count),
            "risk_segment": rng.choice(risk_segments, patient_count, p=[0.42, 0.34, 0.18, 0.06]),
            "registered_date": [
                (datetime(2024, 1, 1) + timedelta(days=int(offset))).date().isoformat()
                for offset in rng.integers(0, 650, patient_count)
            ],
        }
    )


def _generate_encounters(patients: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    service_lines = ["primary_care", "cardiology", "oncology", "orthopedics", "emergency", "surgery"]
    diagnosis_codes = ["I10", "E11", "J18", "I50", "C80", "S72", "N39", "R07", "K35", "O80"]
    rows = []
    encounter_index = 1

    risk_visit_lambda = {"low": 1.5, "moderate": 2.3, "high": 3.5, "complex": 5.0}
    for patient in patients.itertuples(index=False):
        encounter_count = int(np.clip(rng.poisson(risk_visit_lambda[patient.risk_segment]) + 1, 1, 10))
        start_day = int(rng.integers(0, 120))
        current_date = datetime(2025, 1, 1) + timedelta(days=start_day)

        for _ in range(encounter_count):
            encounter_type = rng.choice(
                ["outpatient", "emergency", "inpatient"],
                p=_encounter_type_probabilities(patient.risk_segment),
            )
            service_line = rng.choice(service_lines, p=[0.30, 0.17, 0.08, 0.12, 0.22, 0.11])
            if encounter_type == "emergency":
                service_line = "emergency"

            los_hours = _length_of_stay_hours(encounter_type, patient.risk_segment, rng)
            admit_dt = current_date + timedelta(hours=int(rng.integers(7, 22)))
            discharge_dt = admit_dt + timedelta(hours=float(los_hours))
            disposition = _discharge_disposition(encounter_type, patient.risk_segment, rng)

            rows.append(
                {
                    "encounter_id": f"ENC-{encounter_index:08d}",
                    "patient_id": patient.patient_id,
                    "encounter_type": encounter_type,
                    "service_line": service_line,
                    "admit_datetime": admit_dt.isoformat(sep=" "),
                    "discharge_datetime": discharge_dt.isoformat(sep=" "),
                    "primary_diagnosis_code": rng.choice(diagnosis_codes),
                    "discharge_disposition": disposition,
                }
            )
            encounter_index += 1
            gap_days = int(rng.integers(7, 95))
            if disposition != "death":
                current_date = discharge_dt + timedelta(days=gap_days)

    return pd.DataFrame(rows)


def _encounter_type_probabilities(risk_segment: str) -> list[float]:
    return {
        "low": [0.76, 0.18, 0.06],
        "moderate": [0.62, 0.26, 0.12],
        "high": [0.48, 0.32, 0.20],
        "complex": [0.34, 0.35, 0.31],
    }[risk_segment]


def _length_of_stay_hours(
    encounter_type: str, risk_segment: str, rng: np.random.Generator
) -> float:
    risk_multiplier = {"low": 0.85, "moderate": 1.0, "high": 1.25, "complex": 1.55}[risk_segment]
    if encounter_type == "outpatient":
        return float(np.clip(rng.normal(1.2, 0.4), 0.3, 6))
    if encounter_type == "emergency":
        return float(np.clip(rng.normal(7.5, 3.0) * risk_multiplier, 1, 36))
    return float(np.clip(rng.gamma(2.4, 34) * risk_multiplier, 12, 720))


def _discharge_disposition(
    encounter_type: str, risk_segment: str, rng: np.random.Generator
) -> str:
    death_probability = {
        "low": 0.002,
        "moderate": 0.006,
        "high": 0.018,
        "complex": 0.045,
    }[risk_segment]
    if encounter_type == "inpatient" and rng.random() < death_probability:
        return "death"
    return rng.choice(["home", "home_health", "transfer"], p=[0.78, 0.14, 0.08])


def _generate_lab_orders(encounters: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    lab_tests = ["cbc", "creatinine", "troponin", "glucose", "lactate", "crp"]
    rows = []
    lab_index = 1

    for encounter in encounters.itertuples(index=False):
        order_count = int(
            rng.poisson({"outpatient": 1.0, "emergency": 2.2, "inpatient": 4.0}[encounter.encounter_type])
        )
        for _ in range(order_count):
            lab_test = rng.choice(lab_tests)
            result_status = rng.choice(["normal", "high", "low", "critical"], p=[0.73, 0.14, 0.10, 0.03])
            result_value = _lab_result_value(lab_test, result_status, rng)
            rows.append(
                {
                    "lab_order_id": f"LAB-{lab_index:09d}",
                    "encounter_id": encounter.encounter_id,
                    "patient_id": encounter.patient_id,
                    "order_datetime": encounter.admit_datetime,
                    "lab_test": lab_test,
                    "result_value": result_value,
                    "result_status": result_status,
                }
            )
            lab_index += 1

    return pd.DataFrame(rows)


def _lab_result_value(lab_test: str, result_status: str, rng: np.random.Generator) -> float:
    normal_ranges = {
        "cbc": (4.5, 11.0),
        "creatinine": (0.6, 1.2),
        "troponin": (0.0, 0.04),
        "glucose": (70, 140),
        "lactate": (0.5, 2.0),
        "crp": (0, 5),
    }
    low, high = normal_ranges[lab_test]
    if result_status == "normal":
        return round(float(rng.uniform(low, high)), 2)
    if result_status == "low":
        return round(float(max(0, low * rng.uniform(0.35, 0.85))), 2)
    if result_status == "critical":
        return round(float(high * rng.uniform(2.0, 4.0)), 2)
    return round(float(high * rng.uniform(1.1, 2.0)), 2)


def _generate_claims(encounters: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    payer_options = ["commercial", "medicare", "medicaid", "self_pay"]
    base_cost = {"outpatient": 180, "emergency": 1200, "inpatient": 9500}

    rows = []
    for idx, encounter in enumerate(encounters.itertuples(index=False), start=1):
        los_hours = (
            datetime.fromisoformat(encounter.discharge_datetime)
            - datetime.fromisoformat(encounter.admit_datetime)
        ).total_seconds() / 3600
        amount = base_cost[encounter.encounter_type] + los_hours * rng.uniform(45, 190)
        denied_flag = int(rng.random() < 0.055)
        rows.append(
            {
                "claim_id": f"CLM-{idx:09d}",
                "encounter_id": encounter.encounter_id,
                "patient_id": encounter.patient_id,
                "payer": rng.choice(payer_options, p=[0.48, 0.27, 0.18, 0.07]),
                "allowed_amount": round(float(amount), 2),
                "denied_flag": denied_flag,
            }
        )

    return pd.DataFrame(rows)

