from fastapi import APIRouter, Query
from app.services.pipeline_manager import pipeline

router = APIRouter()


@router.get("")
def get_digital_twin(patient_id: str = Query(...)):
    return pipeline.get_twin_summary(patient_id)
