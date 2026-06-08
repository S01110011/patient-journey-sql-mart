from patient_journey_sql_mart.data import generate_source_data


def test_generate_source_data_has_relational_integrity():
    data = generate_source_data(patient_count=100, seed=123)

    assert len(data.patients) == 100
    assert len(data.encounters) >= 100
    assert data.encounters["patient_id"].isin(data.patients["patient_id"]).all()
    assert data.lab_orders["encounter_id"].isin(data.encounters["encounter_id"]).all()
    assert data.claims["encounter_id"].isin(data.encounters["encounter_id"]).all()

