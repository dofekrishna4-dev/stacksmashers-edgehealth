"""Flags sensor faults / motion-corrupted windows before they reach
the digital twin. Rejects readings with an implausible jump versus
the last known value, which is a common wearable failure mode
(sensor slip, disconnection glitch)."""
from .base_agent import BaseAgent


class ValidationAgent(BaseAgent):
    name = "validation_agent"
    MAX_JUMP = {"hr": 40, "spo2": 15, "resp_rate": 15, "tremor": 3.0, "activity": 1.0}

    def __init__(self, bus):
        super().__init__(bus)
        self._last_reading: dict = {}

    def handle(self, event: dict) -> dict:
        reading = event["reading"]
        pid = event["patient_id"]
        last = self._last_reading.get(pid)
        valid = True
        if last:
            for key, max_jump in self.MAX_JUMP.items():
                if abs(reading[key] - last[key]) > max_jump:
                    valid = False
                    break
        self._last_reading[pid] = reading
        out = {"patient_id": pid, "reading": reading, "valid": valid, "quality": event.get("quality", 1.0)}
        if valid:
            self.bus.publish("reading.validated", out)
        return out
