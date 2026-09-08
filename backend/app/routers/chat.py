from fastapi import APIRouter
from pydantic import BaseModel
from app.services.pipeline_manager import pipeline

router = APIRouter()


class ChatIn(BaseModel):
    patient_id: str
    message: str


@router.post("")
def ask_assistant(payload: ChatIn):
    results = pipeline.rag.retrieve(payload.message, k=2)
    context = " ".join(r["text"] for r in results)
    response = f"Based on the available health knowledge base: {context}"
    return {"patient_id": payload.patient_id, "response": response, "sources": [r["id"] for r in results]}
