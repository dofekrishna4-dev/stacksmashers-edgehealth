import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services.event_bus import EventBus
from app.services.rag_service import RAGService
from app.agents.sensor_agent import SensorAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.digital_twin_agent import DigitalTwinAgent
from app.agents.prediction_agent import PredictionAgent
from app.agents.risk_assessment_agent import RiskAssessmentAgent
from app.agents.coordinator_agent import CoordinatorAgent


class TestAgentPipeline(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()
        self.sensor = SensorAgent(self.bus)
        self.validation = ValidationAgent(self.bus)
        self.twin_agent = DigitalTwinAgent(self.bus, baselines={
            "P1": {"hr": 68, "spo2": 97, "resp_rate": 14, "tremor": 0.1, "activity": 0.35}
        })
        self.prediction = PredictionAgent(self.bus, self.twin_agent)
        self.risk = RiskAssessmentAgent(self.bus)
        self.coordinator = CoordinatorAgent(self.bus)

    def test_sensor_agent_clips_out_of_range_values(self):
        out = self.sensor.handle({"patient_id": "P1", "reading": {
            "hr": 999, "spo2": -5, "resp_rate": 14, "tremor": 0.1, "activity": 0.3
        }})
        self.assertEqual(out["reading"]["hr"], 220)
        self.assertEqual(out["reading"]["spo2"], 50)

    def test_validation_agent_rejects_implausible_jump(self):
        self.validation.handle({"patient_id": "P1", "reading": {
            "hr": 70, "spo2": 97, "resp_rate": 14, "tremor": 0.1, "activity": 0.3}, "quality": 1.0})
        out = self.validation.handle({"patient_id": "P1", "reading": {
            "hr": 200, "spo2": 97, "resp_rate": 14, "tremor": 0.1, "activity": 0.3}, "quality": 1.0})
        self.assertFalse(out["valid"])

    def test_healthy_patient_no_consensus(self):
        for _ in range(10):
            validated = {"patient_id": "P1", "reading": {
                "hr": 68, "spo2": 97, "resp_rate": 14, "tremor": 0.1, "activity": 0.35},
                "dt_minutes": 10}
            self.twin_agent.handle(validated)
        prediction = self.prediction.handle({"patient_id": "P1"})
        risk = self.risk.handle(prediction)
        decision = self.coordinator.decide(prediction, risk)
        self.assertFalse(decision["consensus_reached"])
        self.assertEqual(decision["tier"], "low")

    def test_deteriorating_patient_reaches_consensus(self):
        for i in range(30):
            sev = i / 30
            validated = {"patient_id": "P1", "reading": {
                "hr": 68 + sev * 30, "spo2": 97 - sev * 8, "resp_rate": 14 + sev * 12,
                "tremor": 0.1, "activity": 0.35 - sev * 0.2}, "dt_minutes": 10}
            self.twin_agent.handle(validated)
        prediction = self.prediction.handle({"patient_id": "P1"})
        risk = self.risk.handle(prediction)
        decision = self.coordinator.decide(prediction, risk)
        self.assertTrue(decision["consensus_reached"])
        self.assertIn(decision["tier"], ("high", "critical"))


class TestRAGService(unittest.TestCase):
    def test_retrieval_returns_condition_relevant_context(self):
        rag = RAGService()
        results = rag.retrieve("respiratory rate rising", condition="respiratory_distress", k=1)
        self.assertEqual(len(results), 1)
        self.assertIn(results[0]["condition"], ("respiratory_distress", "general"))

    def test_explain_produces_nonempty_string(self):
        rag = RAGService()
        text = rag.explain("tremor_escalation", "high", 3.0)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 20)


if __name__ == "__main__":
    unittest.main()
