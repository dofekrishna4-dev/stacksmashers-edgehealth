"""Federated swarm sync: the patent-worthy mechanism from the pitch.

Production path: Flower (flwr) coordinating real model weight
updates between hub devices over BLE mesh. This file is a
dependency-free (pure numpy) simulation of the actual protocol so
the mechanism can be demoed and unit-tested without a Flower server,
real BLE hardware, or network access -- swap `LocalModel.weights`
for real TFLite Micro model weights and `BLEMeshTransport` for a
real BLE GATT characteristic in production; the sync protocol itself
does not change.

KEY PRIVACY PROPERTY: only model weight deltas cross the wire.
Nothing in this file ever transmits a raw sensor reading, a feature
vector, or a patient identifier tied to health data.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field


@dataclass
class LocalModel:
    """Stand-in for a small on-device classifier's weight vector."""
    device_id: str
    weights: np.ndarray
    local_samples_seen: int = 0
    version: int = 0

    def local_update(self, gradient: np.ndarray, lr: float = 0.05, n_samples: int = 10):
        """Simulates a local training step on new on-device data."""
        self.weights = self.weights - lr * gradient
        self.local_samples_seen += n_samples
        self.version += 1


class BLEMeshTransport:
    """Simulated BLE mesh: devices can only exchange messages if
    'in range' (represented here as membership in the same mesh
    group). Payload is only ever a weight delta + metadata."""

    def __init__(self):
        self.groups: dict[str, set[str]] = {}

    def join(self, group_id: str, device_id: str):
        self.groups.setdefault(group_id, set()).add(device_id)

    def peers_of(self, group_id: str, device_id: str) -> list[str]:
        return [d for d in self.groups.get(group_id, set()) if d != device_id]


class FederatedSwarmCoordinator:
    """Runs on each hub device. Periodically exchanges weight deltas
    with in-range peers and performs a weighted average -- this is
    federated averaging (FedAvg) done peer-to-peer instead of via a
    central server."""

    def __init__(self, transport: BLEMeshTransport, group_id: str):
        self.transport = transport
        self.group_id = group_id
        self.devices: dict[str, LocalModel] = {}

    def register(self, model: LocalModel):
        self.devices[model.device_id] = model
        self.transport.join(self.group_id, model.device_id)

    def sync_round(self) -> dict[str, dict]:
        """One synchronization round: every device pulls weight deltas
        from its in-range peers and does a sample-weighted average.
        Returns a log of what was exchanged, for demo/audit purposes."""
        log = {}
        snapshot = {d: (m.weights.copy(), m.local_samples_seen) for d, m in self.devices.items()}

        for device_id, model in self.devices.items():
            peers = self.transport.peers_of(self.group_id, device_id)
            if not peers:
                log[device_id] = {"peers_synced": [], "weights_after": model.weights.tolist()}
                continue

            total_weight = snapshot[device_id][1]
            weighted_sum = snapshot[device_id][0] * snapshot[device_id][1]
            for peer_id in peers:
                peer_weights, peer_samples = snapshot[peer_id]
                weighted_sum = weighted_sum + peer_weights * peer_samples
                total_weight += peer_samples

            new_weights = weighted_sum / max(total_weight, 1)
            model.weights = new_weights
            model.version += 1
            log[device_id] = {"peers_synced": peers, "weights_after": new_weights.round(4).tolist()}

        return log


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    true_weights = rng.normal(0, 1, 5)

    transport = BLEMeshTransport()
    coordinator = FederatedSwarmCoordinator(transport, group_id="home_cluster_A")

    device_a = LocalModel("hub_A", weights=true_weights + rng.normal(0, 0.5, 5), local_samples_seen=40)
    device_b = LocalModel("hub_B", weights=true_weights + rng.normal(0, 0.5, 5), local_samples_seen=25)
    device_c = LocalModel("hub_C", weights=true_weights + rng.normal(0, 0.8, 5), local_samples_seen=15)

    for d in (device_a, device_b, device_c):
        coordinator.register(d)

    def err(m): return float(np.linalg.norm(m.weights - true_weights))
    print("Before sync — distance from ground truth:")
    for d in (device_a, device_b, device_c):
        print(f"  {d.device_id}: {err(d):.4f}")

    log = coordinator.sync_round()

    print("\nAfter one federated swarm sync round (BLE mesh, no raw data, no server):")
    for d in (device_a, device_b, device_c):
        print(f"  {d.device_id}: {err(d):.4f}  (synced with {log[d.device_id]['peers_synced']})")
