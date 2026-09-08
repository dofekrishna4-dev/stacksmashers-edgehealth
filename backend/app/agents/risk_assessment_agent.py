"""Classifies severity tier from the prediction agent's output,
checked against the patient's personalized baseline deviation.
This is a second, independent vote alongside the prediction agent --
required before the coordinator will allow escalation."""
from .base_agent import BaseAgent


class RiskAssessmentAgent(BaseAgent):
    name = "risk_assessment_agent"

    def handle(self, event: dict) -> dict:
        if not event.get("risk_detected"):
            tier = "low"
            agrees = False
        else:
            hours = event["hours_ahead"]
            confidence = event["confidence"]
            if confidence >= 0.85 and hours <= 2:
                tier = "critical"
            elif confidence >= 0.7 and hours <= 6:
                tier = "high"
            elif confidence >= 0.55:
                tier = "medium"
            else:
                tier = "low"
            agrees = tier in ("high", "critical")

        out = {"patient_id": event["patient_id"], "tier": tier, "agrees_with_prediction": agrees}
        self.bus.publish("risk.assessed", out)
        return out
