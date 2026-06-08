# Data Dictionary

## Source Tables

### src_patients

Synthetic patient demographics and registration attributes.

Key fields:

- `patient_id`
- `birth_date`
- `sex`
- `city`
- `risk_segment`

### src_encounters

Clinical encounters across outpatient, emergency and inpatient settings.

Key fields:

- `encounter_id`
- `patient_id`
- `encounter_type`
- `service_line`
- `admit_datetime`
- `discharge_datetime`
- `primary_diagnosis_code`
- `discharge_disposition`

### src_lab_orders

Laboratory orders and abnormal result flags.

Key fields:

- `lab_order_id`
- `encounter_id`
- `lab_test`
- `result_status`
- `result_value`

### src_claims

Synthetic financial claim records linked to encounters.

Key fields:

- `claim_id`
- `encounter_id`
- `payer`
- `allowed_amount`
- `denied_flag`

## Mart Tables

### dim_patient

One row per patient.

### dim_date

Calendar dimension generated from encounter dates.

### fact_encounter

One row per clinical encounter with duration, diagnosis, discharge and cost fields.

### fact_lab_order

One row per lab order.

### mart_patient_journey

Patient-level longitudinal summary for care journey analytics.

### mart_readmission_30d

Encounter-level readmission detection table.

