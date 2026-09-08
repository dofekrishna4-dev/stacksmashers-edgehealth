"""In-process manager that wires the 8 agents together and keeps
per-patient state, for the FastAPI backend to call into. This is the
same agent graph used in edge/run_simulation.py -- the backend
version exists so the caregiver dashboard API can query live state
in a demo/dev environment without needing real edge hardware
attached. In production, this logic runs on the edge hub itself and
the backend only ever receives already-computed summaries."""
from __future__ import annotations

from app.services.event_bus import EventBus
from app.services.rag_service import RAGService
from app.agents.sensor_agent import SensorAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.digital_twin_agent import DigitalTwinAgent
from app.agents.prediction_agent import PredictionAgent
from app.agents.risk_assessment_agent import RiskAssessmentAgent
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.medical_knowledge_agent import MedicalKnowledgeAgent
from app.agents.alert_agent import AlertAgent
from app.agents.emergency_agent import EmergencyAgent


class PipelineManager:
    def __init__(self):
        self.bus = EventBus()
        self.rag = RAGService()
        self.baselines: dict[str, dict] = {}
        self.twin_agent = DigitalTwinAgent(self.bus, baselines={})
        self.sensor_agent = SensorAgent(self.bus)
        self.validation_agent = ValidationAgent(self.bus)
        self.prediction_agent = PredictionAgent(self.bus, self.twin_agent)
        self.risk_agent = RiskAssessmentAgent(self.bus)
        self.coordinator = CoordinatorAgent(self.bus)
        self.knowledge_agent = MedicalKnowledgeAgent(self.bus, self.rag)
        self.alert_agent = AlertAgent(self.bus)
        self.emergency_agent = EmergencyAgent(self.bus)
        self.alerts: dict[str, list[dict]] = {}

    def ensure_patient(self, patient_id: str, baseline: dict | None = None):
        if patient_id not in self.twin_agent.twins:
            from app.services.digital_twin_engine import DigitalTwin
            b = baseline or {"hr": 70, "spo2": 97, "resp_rate": 14, "tremor": 0.1, "activity": 0.3}
            self.twin_agent.twins[patient_id] = DigitalTwin(patient_id=patient_id, baseline=b)
            self.alerts.setdefault(patient_id, [])

    def ingest_reading(self, patient_id: str, reading: dict, dt_minutes: float = 0.5) -> dict:
        self.ensure_patient(patient_id)
        cleaned = self.sensor_agent.handle({"patient_id": patient_id, "reading": reading})
        validated = self.validation_agent.handle(cleaned)
        if not validated["valid"]:
            return {"accepted": False}

        validated["dt_minutes"] = dt_minutes
        twin_out = self.twin_agent.handle(validated)
        prediction = self.prediction_agent.handle({"patient_id": patient_id})
        risk = self.risk_agent.handle(prediction)
        decision = self.coordinator.decide(prediction, risk)

        result = {"accepted": True, "twin_state": twin_out["twin_state"], "decision": decision}

        if decision["consensus_reached"]:
            explanation = self.knowledge_agent.handle(decision)
            decision["explanation"] = explanation["explanation"]
            alert = self.alert_agent.handle(decision)
            self.alerts[patient_id].append(alert)
            result["alert"] = alert

            escalation = self.emergency_agent.handle(alert)
            if escalation.get("escalated"):
                result["escalation"] = escalation

        return result

    def get_twin_summary(self, patient_id: str) -> dict:
        self.ensure_patient(patient_id)
        twin = self.twin_agent.get_twin(patient_id)
        breach = twin.time_to_threshold_breach()
        return {
            "patient_id": patient_id,
            "baseline": twin.baseline,
            "current": twin.current_state(),
            "projection": {
                "horizon_hours": breach["hours_ahead"] if breach else None,
                "trend": "worsening" if breach else "stable",
                "breaches": breach["breaches"] if breach else [],
            },
        }

    def get_alerts(self, patient_id: str) -> list[dict]:
        self.ensure_patient(patient_id)
        return self.alerts.get(patient_id, [])


# module-level singleton for the demo backend (a real deployment would
# scope this per edge-hub process, not per API server)
pipeline = PipelineManager()
