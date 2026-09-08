"""The consensus coordinator. Requires the prediction agent AND the
risk assessment agent to independently agree something is wrong
before anything reaches a caregiver -- this is the mechanism that
suppresses single-model false positives, and the actual
implementation of the 'agent consensus' claim in the pitch."""
from .base_agent import BaseAgent


class CoordinatorAgent(BaseAgent):
    name = "coordinator_agent"

    def decide(self, prediction: dict, risk: dict) -> dict:
        consensus_reached = prediction.get("risk_detected", False) and risk.get("agrees_with_prediction", False)
        decision = {
            "patient_id": prediction["patient_id"],
            "consensus_reached": consensus_reached,
            "tier": risk["tier"],
            "condition": prediction.get("condition"),
            "hours_ahead": prediction.get("hours_ahead"),
            "confidence": prediction.get("confidence"),
            "voting_agents": {
                "prediction_agent": prediction.get("risk_detected", False),
                "risk_assessment_agent": risk.get("agrees_with_prediction", False),
            },
        }
        self.bus.publish("coordinator.decided", decision)
        return decision

    def handle(self, event: dict) -> dict:
        raise NotImplementedError("CoordinatorAgent uses decide(), not handle()")
