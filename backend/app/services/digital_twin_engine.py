"""Digital Twin engine: a per-patient rolling state-space model with
forward projection.

This is the core of the "predict hours ahead" capability. Each
patient's twin tracks a smoothed state (level + trend/velocity) for
each vital using a simple constant-velocity Kalman filter, updated
every ~30 seconds. Projecting the state forward in time, and
checking when the projected trajectory crosses a personalized danger
threshold, is what produces the "82% risk within 6 hours" style
output.

Deliberately dependency-free (pure numpy) so it runs unmodified on a
microcontroller-class edge hub.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field


@dataclass
class VitalKalmanState:
    """Constant-velocity Kalman filter for a single vital sign.
    State vector: [level, trend_per_minute].

    Trend noise is deliberately much smaller than level (measurement)
    noise: a single noisy reading should move the level estimate but
    should NOT be enough on its own to convince the filter of a
    sustained trend. Without this asymmetry, pure sensor noise gets
    extrapolated into a false "deterioration" over a multi-hour
    projection window -- caught by test_stable_readings_do_not_trigger_breach.
    """
    level: float
    trend: float = 0.0
    p: np.ndarray = field(default_factory=lambda: np.diag([1.0, 0.02]))
    level_process_noise: float = 0.05
    trend_process_noise: float = 0.0005
    measurement_noise: float = 1.0
    n_updates: int = 0

    def update(self, measurement: float, dt_minutes: float = 0.5):
        F = np.array([[1, dt_minutes], [0, 1]])
        x = np.array([self.level, self.trend])
        x_pred = F @ x
        Q = np.diag([self.level_process_noise, self.trend_process_noise])
        p_pred = F @ self.p @ F.T + Q

        H = np.array([[1, 0]])
        R = np.array([[self.measurement_noise]])
        y = measurement - (H @ x_pred)[0]
        S = (H @ p_pred @ H.T + R)[0, 0]
        K = (p_pred @ H.T).flatten() / S

        x_new = x_pred + K * y
        p_new = (np.eye(2) - np.outer(K, H)) @ p_pred

        self.level, self.trend = float(x_new[0]), float(x_new[1])
        self.p = p_new
        self.n_updates += 1

    def trend_significance(self) -> float:
        """z-score of the trend estimate vs. its own uncertainty. A
        trend estimate the filter isn't confident about (high variance
        relative to magnitude) shouldn't be trusted for hours-ahead
        extrapolation."""
        trend_std = np.sqrt(max(self.p[1, 1], 1e-9))
        return abs(self.trend) / trend_std

    def project(self, minutes_ahead: float, min_significance: float = 1.5,
                min_updates: int = 6) -> float:
        """Projects forward, but only applies the trend if it's
        statistically significant and backed by enough readings --
        otherwise projects flat from the current level. This is what
        keeps noisy-but-stable patients from generating false alarms
        while still letting a genuine sustained trend extrapolate."""
        if self.n_updates < min_updates or self.trend_significance() < min_significance:
            return self.level
        return self.level + self.trend * minutes_ahead


@dataclass
class DigitalTwin:
    patient_id: str
    baseline: dict  # {"hr":..,"spo2":..,"resp_rate":..,"tremor":..,"activity":..}
    danger_thresholds: dict = field(default_factory=lambda: {
        "hr": 110, "spo2_low": 90, "resp_rate": 24, "tremor": 1.2,
    })
    states: dict = field(default_factory=dict)
    version: int = 1

    def __post_init__(self):
        if not self.states:
            self.states = {
                "hr": VitalKalmanState(level=self.baseline["hr"]),
                "spo2": VitalKalmanState(level=self.baseline["spo2"], measurement_noise=0.5),
                "resp_rate": VitalKalmanState(level=self.baseline["resp_rate"]),
                "tremor": VitalKalmanState(level=self.baseline.get("tremor", 0.1), measurement_noise=0.05),
                "activity": VitalKalmanState(level=self.baseline.get("activity", 0.3), measurement_noise=0.05),
            }

    def ingest(self, measurements: dict, dt_minutes: float = 0.5):
        """measurements: {"hr":.., "spo2":.., "resp_rate":.., "tremor":.., "activity":..}"""
        for key, value in measurements.items():
            if key in self.states:
                self.states[key].update(value, dt_minutes=dt_minutes)
        self.version += 1

    def current_state(self) -> dict:
        return {k: round(s.level, 2) for k, s in self.states.items()}

    def project_forward(self, horizon_hours: float, step_minutes: float = 15) -> list[dict]:
        """Returns a list of projected states at each step up to horizon_hours."""
        steps = int((horizon_hours * 60) / step_minutes)
        trajectory = []
        for i in range(1, steps + 1):
            minutes = i * step_minutes
            point = {k: round(s.project(minutes), 2) for k, s in self.states.items()}
            point["minutes_ahead"] = minutes
            trajectory.append(point)
        return trajectory

    def time_to_threshold_breach(self, max_horizon_hours: float = 8) -> dict | None:
        """Scans the forward projection and returns the first vital/time
        that crosses a danger threshold, or None if nothing breaches
        within the horizon. This is what powers the prediction agent's
        'risk within N hours' output."""
        trajectory = self.project_forward(max_horizon_hours, step_minutes=5)
        for point in trajectory:
            breaches = []
            if point["hr"] >= self.danger_thresholds["hr"]:
                breaches.append(("hr", point["hr"]))
            if point["spo2"] <= self.danger_thresholds["spo2_low"]:
                breaches.append(("spo2", point["spo2"]))
            if point["resp_rate"] >= self.danger_thresholds["resp_rate"]:
                breaches.append(("resp_rate", point["resp_rate"]))
            if point["tremor"] >= self.danger_thresholds["tremor"]:
                breaches.append(("tremor", point["tremor"]))
            if breaches:
                return {
                    "hours_ahead": round(point["minutes_ahead"] / 60, 2),
                    "breaches": breaches,
                }
        return None
