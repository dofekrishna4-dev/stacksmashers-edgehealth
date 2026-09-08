from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.services.pipeline_manager import pipeline

router = APIRouter()


class HealthDataIn(BaseModel):
    patient_id: str
    recorded_at: datetime
    heart_rate_avg: float
    spo2_avg: float
    resp_rate_avg: float
    tremor_score: float
    activity_level: float
    data_quality: float


@router.post("")
def ingest_health_data(payload: HealthDataIn):
    reading = {
        "hr": payload.heart_rate_avg,
        "spo2": payload.spo2_avg,
        "resp_rate": payload.resp_rate_avg,
        "tremor": payload.tremor_score,
        "activity": payload.activity_level,
    }
    result = pipeline.ingest_reading(payload.patient_id, reading)
    return {"received": True, "patient_id": payload.patient_id, "pipeline_result": result}
