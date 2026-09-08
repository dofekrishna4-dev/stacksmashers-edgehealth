"""Maintains each patient's DigitalTwin instance and updates it on
every validated reading."""
from .base_agent import BaseAgent
from app.services.digital_twin_engine import DigitalTwin


class DigitalTwinAgent(BaseAgent):
    name = "digital_twin_agent"

    def __init__(self, bus, baselines: dict[str, dict]):
        super().__init__(bus)
        self.twins: dict[str, DigitalTwin] = {
            pid: DigitalTwin(patient_id=pid, baseline=b) for pid, b in baselines.items()
        }

    def handle(self, event: dict) -> dict:
        pid = event["patient_id"]
        twin = self.twins[pid]
        dt_minutes = event.get("dt_minutes", 0.5)
        twin.ingest(event["reading"], dt_minutes=dt_minutes)
        out = {
            "patient_id": pid,
            "twin_state": twin.current_state(),
            "twin_version": twin.version,
        }
        self.bus.publish("twin.updated", out)
        return out

    def get_twin(self, patient_id: str) -> DigitalTwin:
        return self.twins[patient_id]
