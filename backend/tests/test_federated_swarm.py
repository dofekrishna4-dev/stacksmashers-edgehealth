import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "edge", "mesh"))
import numpy as np
from federated_swarm import LocalModel, BLEMeshTransport, FederatedSwarmCoordinator


class TestFederatedSwarm(unittest.TestCase):
    def test_sync_reduces_average_distance_to_ground_truth(self):
        rng = np.random.default_rng(0)
        true_weights = rng.normal(0, 1, 5)
        transport = BLEMeshTransport()
        coordinator = FederatedSwarmCoordinator(transport, group_id="test_group")

        devices = [
            LocalModel(f"hub_{i}", weights=true_weights + rng.normal(0, 0.6, 5), local_samples_seen=20 + i * 5)
            for i in range(3)
        ]
        for d in devices:
            coordinator.register(d)

        def err(m):
            return float(np.linalg.norm(m.weights - true_weights))

        before = np.mean([err(d) for d in devices])
        coordinator.sync_round()
        after = np.mean([err(d) for d in devices])

        self.assertLess(after, before)

    def test_no_raw_data_only_weights_in_transport_log(self):
        transport = BLEMeshTransport()
        coordinator = FederatedSwarmCoordinator(transport, group_id="g")
        m1 = LocalModel("a", weights=np.zeros(3), local_samples_seen=10)
        m2 = LocalModel("b", weights=np.ones(3), local_samples_seen=10)
        coordinator.register(m1)
        coordinator.register(m2)
        log = coordinator.sync_round()
        for device_id, entry in log.items():
            self.assertIn("weights_after", entry)
            self.assertNotIn("raw_reading", entry)
            self.assertNotIn("patient_id", entry)


if __name__ == "__main__":
    unittest.main()
