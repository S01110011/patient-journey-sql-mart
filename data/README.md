# Data

This folder stores local generated SQLite databases and exported CSV files.

Generate the mart with:

```powershell
python -m patient_journey_sql_mart.database --database data/patient_journey.db --patients 1500
```

Do not commit real patient data or protected health information.

