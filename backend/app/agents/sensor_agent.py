"""Cleans and windows raw sensor data into the feature vector used
downstream. In production this wraps features.py; here it accepts a
pre-windowed reading dict for simplicity in the simulation."""
from .base_agent import BaseAgent


class SensorAgent(BaseAgent):
    name = "sensor_agent"

    def handle(self, event: dict) -> dict:
        reading = event["reading"]
        # basic sanity clipping -- real implementation runs full
        # artifact rejection from ml/features.py
        cleaned = {
            "hr": max(30, min(220, reading["hr"])),
            "spo2": max(50, min(100, reading["spo2"])),
            "resp_rate": max(4, min(60, reading["resp_rate"])),
            "tremor": max(0, reading["tremor"]),
            "activity": max(0, min(1, reading["activity"])),
        }
        out = {"patient_id": event["patient_id"], "reading": cleaned, "quality": 1.0}
        self.bus.publish("reading.cleaned", out)
        return out
