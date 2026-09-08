"""Generates the plain-language caregiver explanation. Uses the
RAG service (retrieval over an offline knowledge base + the
patient's own anomaly history) -- see rag_service.py."""
from .base_agent import BaseAgent


class MedicalKnowledgeAgent(BaseAgent):
    name = "medical_knowledge_agent"

    def __init__(self, bus, rag_service):
        super().__init__(bus)
        self.rag = rag_service

    def handle(self, event: dict) -> dict:
        explanation = self.rag.explain(
            condition=event.get("condition", "unknown"),
            tier=event["tier"],
            hours_ahead=event.get("hours_ahead"),
        )
        out = {"patient_id": event["patient_id"], "explanation": explanation}
        self.bus.publish("explanation.generated", out)
        return out
