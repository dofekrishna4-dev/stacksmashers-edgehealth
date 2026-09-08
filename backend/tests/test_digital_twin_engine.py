"""Tests for the digital twin Kalman-filter engine.
Run: python3 -m pytest backend/tests -v  (or python3 -m unittest)
"""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from app.services.digital_twin_engine import DigitalTwin


class TestDigitalTwin(unittest.TestCase):
    def setUp(self):
        self.baseline = {"hr": 68, "spo2": 97, "resp_rate": 14, "tremor": 0.1, "activity": 0.35}
        self.twin = DigitalTwin(patient_id="TEST", baseline=self.baseline)

    def test_initial_state_matches_baseline(self):
        state = self.twin.current_state()
        self.assertAlmostEqual(state["hr"], self.baseline["hr"], delta=0.5)

    def test_stable_readings_do_not_trigger_breach(self):
        rng = np.random.default_rng(0)
        for _ in range(50):
            self.twin.ingest({
                "hr": float(rng.normal(68, 1)), "spo2": float(rng.normal(97, 0.3)),
                "resp_rate": float(rng.normal(14, 0.5)), "tremor": float(rng.normal(0.1, 0.02)),
                "activity": float(rng.normal(0.35, 0.02)),
            }, dt_minutes=5)
        breach = self.twin.time_to_threshold_breach()
        self.assertIsNone(breach)

    def test_deteriorating_trend_triggers_breach(self):
        rng = np.random.default_rng(1)
        for i in range(30):
            sev = i / 30
            self.twin.ingest({
                "hr": float(rng.normal(68 + sev * 30, 2)), "spo2": float(rng.normal(97 - sev * 8, 0.5)),
                "resp_rate": float(rng.normal(14 + sev * 12, 1)), "tremor": float(rng.normal(0.1, 0.02)),
                "activity": float(rng.normal(0.35 - sev * 0.2, 0.02)),
            }, dt_minutes=10)
        breach = self.twin.time_to_threshold_breach(max_horizon_hours=8)
        self.assertIsNotNone(breach)
        self.assertIn("hours_ahead", breach)
        self.assertGreaterEqual(breach["hours_ahead"], 0)

    def test_version_increments_on_ingest(self):
        v0 = self.twin.version
        self.twin.ingest({"hr": 70, "spo2": 96, "resp_rate": 15, "tremor": 0.1, "activity": 0.3})
        self.assertEqual(self.twin.version, v0 + 1)


if __name__ == "__main__":
    unittest.main()
