from fastapi import APIRouter
import random

router = APIRouter()

@router.get("/")
def simulate_patient(patient_id: str):

    return {
        "patient_id": patient_id,
        "hr": random.randint(65, 120),
        "spo2": random.randint(90, 100),
        "resp_rate": random.randint(12, 22),
        "tremor": round(random.uniform(0.0, 1.0), 2),
        "activity": round(random.uniform(0.0, 1.0), 2),
    }