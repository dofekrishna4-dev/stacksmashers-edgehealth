"""End-to-end EdgeHealth Guardian simulation.

Wires all 8 agents together over the local event bus, streams
simulated deteriorating sensor readings for one patient, and prints
each stage of the pipeline: sensor -> validation -> digital twin ->
prediction -> risk assessment -> coordinator consensus -> RAG
explanation -> tiered alert -> (if critical) autonomous emergency
escalation.

Run: python3 edge/run_simulation.py
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import numpy as np
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

PATIENT_ID = "P001"
BASELINE = {"hr": 68, "spo2": 97, "resp_rate": 14, "tremor": 0.1, "activity": 0.35}


def build_agents(bus):
    rag = RAGService()
    return {
        "sensor": SensorAgent(bus),
        "validation": ValidationAgent(bus),
        "twin": DigitalTwinAgent(bus, baselines={PATIENT_ID: BASELINE}),
        "prediction": None,  # built after twin agent exists
        "risk": RiskAssessmentAgent(bus),
        "coordinator": CoordinatorAgent(bus),
        "knowledge": MedicalKnowledgeAgent(bus, rag),
        "alert": AlertAgent(bus),
        "emergency": EmergencyAgent(bus),
    }


def run():
    bus = EventBus()
    agents = build_agents(bus)
    agents["prediction"] = PredictionAgent(bus, agents["twin"], horizon_hours=8)

    rng = np.random.default_rng(7)
    print(f"Simulating deterioration for patient {PATIENT_ID} (respiratory distress)\n")

    last_tier = "low"
    for step in range(0, 361, 20):  # every 20 "ticks" = every 10 sim-minutes
        sev = min(1.0, step / 360)
        raw_reading = {
            "hr": float(rng.normal(68 + sev * 22, 2)),
            "spo2": float(rng.normal(97 - sev * 6, 0.5)),
            "resp_rate": float(rng.normal(14 + sev * 10, 1)),
            "tremor": float(rng.normal(0.1, 0.05)),
            "activity": float(rng.normal(0.35 - sev * 0.15, 0.03)),
        }

        cleaned = agents["sensor"].handle({"patient_id": PATIENT_ID, "reading": raw_reading})
        validated = agents["validation"].handle(cleaned)
        if not validated["valid"]:
            continue

        validated["dt_minutes"] = 10  # readings arrive every 10 sim-minutes in this demo
        twin_out = agents["twin"].handle(validated)
        prediction = agents["prediction"].handle({"patient_id": PATIENT_ID})
        risk = agents["risk"].handle(prediction)
        decision = agents["coordinator"].decide(prediction, risk)

        sim_minutes = step * 0.5
        print(f"t={sim_minutes:5.0f}min  twin={twin_out['twin_state']}  "
              f"tier={decision['tier']:8s}  consensus={decision['consensus_reached']}")

        if decision["tier"] != last_tier:
            last_tier = decision["tier"]
            if decision["consensus_reached"]:
                explanation = agents["knowledge"].handle(decision)
                decision["explanation"] = explanation["explanation"]
                alert = agents["alert"].handle(decision)
                print(f"    -> ALERT [{alert['tier']}] via {alert['channel']}: {alert['message'][:120]}...")

                escalation = agents["emergency"].handle(alert)
                if escalation.get("escalated"):
                    print(f"    -> AUTONOMOUS ESCALATION: {escalation}")

    print(f"\nTotal events on bus: {len(bus.log)}")


if __name__ == "__main__":
    run()
