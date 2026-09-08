from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_prediction(patient_id: str):
    return {
        "patient_id": patient_id,
        "condition": "Stable",
        "horizon_hours": 24,
        "trend": "stable",
        "current_state": {
            "hr": 70,
            "spo2": 97,
            "resp_rate": 14,
            "tremor": 0.1,
            "activity": 0.3
        }
    }