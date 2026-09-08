# API design

Base URL (local dev): `http://localhost:8000`

### `POST /health-data`
Ingest a batch of derived health metrics from an edge hub.

Request:
```json
{
  "patient_id": "b3f1...e2",
  "recorded_at": "2026-09-04T10:15:00Z",
  "heart_rate_avg": 74.2,
  "spo2_avg": 95.1,
  "resp_rate_avg": 19.0,
  "tremor_score": 0.6,
  "activity_level": 0.3,
  "data_quality": 0.92
}
```

Response:
```json
{ "received": true, "patient_id": "b3f1...e2" }
```

### `GET /prediction?patient_id=...`
Latest risk prediction for a patient, mirroring the on-device prediction agent.

Response:
```json
{
  "patient_id": "b3f1...e2",
  "condition": "respiratory_distress",
  "risk_score": 82,
  "horizon_hours": 6,
  "contributing_agents": {
    "prediction_agent": 0.85,
    "risk_assessment_agent": 0.79,
    "correlation_agent": 0.81
  },
  "explanation": "Respiratory rate variability has trended upward for 3 hours, correlated with reduced activity level versus personal baseline."
}
```

### `GET /alerts?patient_id=...`
List of alerts for a patient.

Response:
```json
{ "patient_id": "b3f1...e2", "alerts": [] }
```

### `POST /alerts/acknowledge`
Request:
```json
{ "alert_id": "a91c...44" }
```
Response:
```json
{ "alert_id": "a91c...44", "acknowledged": true }
```

### `GET /digital-twin?patient_id=...`
Response:
```json
{
  "patient_id": "b3f1...e2",
  "baseline": { "heart_rate": 68, "spo2": 97, "resp_rate": 14, "tremor": 0.2 },
  "current": { "heart_rate": 74, "spo2": 95, "resp_rate": 19, "tremor": 0.6 },
  "projection": { "horizon_hours": 6, "trend": "worsening", "confidence": 0.81 }
}
```

### `POST /chat`
Request:
```json
{ "patient_id": "b3f1...e2", "message": "Why did the alert fire this morning?" }
```
Response:
```json
{
  "patient_id": "b3f1...e2",
  "response": "The alert fired because respiratory rate variability rose steadily over three hours while activity stayed below your normal baseline — a pattern the system has learned often precedes respiratory distress for this patient."
}
```
