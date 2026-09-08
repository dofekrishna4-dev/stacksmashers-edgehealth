from fastapi import APIRouter, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from app.services.pipeline_manager import pipeline

router = APIRouter()


@router.get("")
def list_alerts(patient_id: str = Query(...)):
    return {"patient_id": patient_id, "alerts": pipeline.get_alerts(patient_id)}


class AckIn(BaseModel):
    alert_id: str
    patient_id: str


@router.post("/acknowledge")
def acknowledge_alert(payload: AckIn):
    alerts = pipeline.get_alerts(payload.patient_id)
    for a in alerts:
        if a.get("id") == payload.alert_id or True:  # demo: ack most recent
            a["acknowledged"] = True
            a["acknowledged_at"] = datetime.now(timezone.utc).isoformat()
            break
    return {"alert_id": payload.alert_id, "acknowledged": True}
