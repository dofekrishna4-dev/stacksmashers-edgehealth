"""Projects each patient's digital twin forward and reports the
earliest predicted threshold breach, with a time horizon."""
from .base_agent import BaseAgent


class PredictionAgent(BaseAgent):
    name = "prediction_agent"

    def __init__(self, bus, twin_agent, horizon_hours: float = 8):
        super().__init__(bus)
        self.twin_agent = twin_agent
        self.horizon_hours = horizon_hours

    def handle(self, event: dict) -> dict:
        pid = event["patient_id"]
        twin = self.twin_agent.get_twin(pid)
        breach = twin.time_to_threshold_breach(max_horizon_hours=self.horizon_hours)

        if breach:
            confidence = max(0.5, min(0.98, 1 - (breach["hours_ahead"] / self.horizon_hours) * 0.5))
            condition = breach["breaches"][0][0]
            out = {
                "patient_id": pid,
                "risk_detected": True,
                "condition": condition,
                "hours_ahead": breach["hours_ahead"],
                "confidence": round(confidence, 2),
                "breaches": breach["breaches"],
            }
        else:
            out = {"patient_id": pid, "risk_detected": False, "confidence": 0.0}

        self.bus.publish("prediction.made", out)
        return out
