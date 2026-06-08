PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS src_claims;
DROP TABLE IF EXISTS src_lab_orders;
DROP TABLE IF EXISTS src_encounters;
DROP TABLE IF EXISTS src_patients;

CREATE TABLE src_patients (
    patient_id TEXT PRIMARY KEY,
    birth_date DATE NOT NULL,
    sex TEXT NOT NULL,
    city TEXT NOT NULL,
    risk_segment TEXT NOT NULL,
    registered_date DATE NOT NULL
);

CREATE TABLE src_encounters (
    encounter_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    encounter_type TEXT NOT NULL,
    service_line TEXT NOT NULL,
    admit_datetime TEXT NOT NULL,
    discharge_datetime TEXT NOT NULL,
    primary_diagnosis_code TEXT NOT NULL,
    discharge_disposition TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES src_patients(patient_id)
);

CREATE TABLE src_lab_orders (
    lab_order_id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    order_datetime TEXT NOT NULL,
    lab_test TEXT NOT NULL,
    result_value REAL NOT NULL,
    result_status TEXT NOT NULL,
    FOREIGN KEY (encounter_id) REFERENCES src_encounters(encounter_id),
    FOREIGN KEY (patient_id) REFERENCES src_patients(patient_id)
);

CREATE TABLE src_claims (
    claim_id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    payer TEXT NOT NULL,
    allowed_amount REAL NOT NULL,
    denied_flag INTEGER NOT NULL,
    FOREIGN KEY (encounter_id) REFERENCES src_encounters(encounter_id),
    FOREIGN KEY (patient_id) REFERENCES src_patients(patient_id)
);

CREATE INDEX idx_src_encounters_patient ON src_encounters(patient_id);
CREATE INDEX idx_src_encounters_admit ON src_encounters(admit_datetime);
CREATE INDEX idx_src_labs_patient ON src_lab_orders(patient_id);
CREATE INDEX idx_src_claims_encounter ON src_claims(encounter_id);

