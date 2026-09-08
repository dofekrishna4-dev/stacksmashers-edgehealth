"""Autonomously escalates a critical, unacknowledged alert -- the
'autonomous decision system' piece. In the hackathon demo this
prepares the EMS-ready handoff summary; wiring to a real dialer/SMS
gateway is a deployment-time integration, not a code change here."""
from .base_agent import BaseAgent


class EmergencyAgent(BaseAgent):
    name = "emergency_agent"

    def handle(self, event: dict) -> dict:
        if event["tier"] != "critical" or event.get("acknowledged"):
            return {"escalated": False}

        handoff = {
            "patient_id": event["patient_id"],
            "escalated": True,
            "condition": event.get("condition"),
            "predicted_hours_ahead": event.get("hours_ahead"),
            "summary": event.get("message", ""),
            "action": "emergency_contact_chain_initiated",
        }
        self.bus.publish("emergency.escalated", handoff)
        return handoff
