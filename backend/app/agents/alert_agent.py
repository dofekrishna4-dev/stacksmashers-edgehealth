"""Formats and dispatches the tiered alert. Channel selection mirrors
the emergency response engine defined in docs/BLUEPRINT.md."""
from .base_agent import BaseAgent

CHANNEL_BY_TIER = {
    "low": "dashboard",
    "medium": "push",
    "high": "sms",
    "critical": "emergency_call",
}


class AlertAgent(BaseAgent):
    name = "alert_agent"

    def handle(self, event: dict) -> dict:
        tier = event["tier"]
        channel = CHANNEL_BY_TIER.get(tier, "dashboard")
        message = (
            f"[{tier.upper()}] {event.get('condition', 'anomaly')} risk for "
            f"patient {event['patient_id']}: predicted in "
            f"{event.get('hours_ahead', '?')}h. {event.get('explanation', '')}"
        )
        out = {
            "patient_id": event["patient_id"], "tier": tier, "channel": channel,
            "message": message, "acknowledged": False, "escalated": False,
        }
        self.bus.publish("alert.dispatched", out)
        return out
