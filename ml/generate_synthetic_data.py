"""Generates a synthetic multi-modal wearable dataset for EdgeHealth
Guardian, simulating both healthy patients and patients heading
toward a respiratory-distress or tremor-escalation event.

This exists because real labeled wearable-to-outcome datasets
(MIMIC waveform subsets, PhysioNet, WESAD, SisFall) require
licensed access and heavy preprocessing before a hackathon can use
them. This generator produces physiologically-plausible windows with
ground-truth labels and time-to-event, enough to prove the full
pipeline (features -> classifier -> digital twin -> prediction) end
to end. Swap in real datasets using the same `features.py` interface
for a production model.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from features import build_feature_vector, FEATURE_NAMES

RNG = np.random.default_rng(42)


def simulate_patient_baseline():
    return {
        "hr": RNG.normal(68, 4),
        "spo2": RNG.normal(97, 0.8),
        "resp_rate": RNG.normal(14, 1.2),
        "activity": RNG.normal(0.35, 0.08),
    }


def simulate_window(baseline: dict, severity: float, condition: str, fs=50, secs=60):
    """severity in [0,1]: 0 = healthy baseline, 1 = full crisis.
    condition: 'respiratory_distress' | 'tremor_escalation' | 'healthy'
    """
    n_hr = secs
    n_accel = secs * fs
    n_resp = secs

    hr = RNG.normal(baseline["hr"] + severity * 22, 3 + severity * 4, n_hr)
    spo2 = np.clip(RNG.normal(baseline["spo2"] - severity * 6, 0.8 + severity * 0.6, n_hr), 70, 100)
    resp_rate = RNG.normal(baseline["resp_rate"] + severity * 10, 1.2 + severity * 2.5, n_resp)
    activity = np.clip(RNG.normal(baseline["activity"] - severity * 0.2, 0.08, n_hr), 0, 1)

    t = np.arange(n_accel) / fs
    if condition == "tremor_escalation":
        tremor_amp = severity * 1.8
        accel = tremor_amp * np.sin(2 * np.pi * 5.0 * t) + RNG.normal(0, 0.3, n_accel)
    else:
        accel = RNG.normal(0, 0.3 + severity * 0.1, n_accel)

    resp_signal = np.sin(2 * np.pi * (resp_rate.mean() / 60) * np.arange(n_resp)) + RNG.normal(0, 0.2, n_resp)

    return {"hr": hr, "spo2": spo2, "resp_rate": resp_rate, "resp": resp_signal,
            "accel": accel, "activity": activity}


def generate_dataset(n_patients=40, windows_per_patient=30) -> pd.DataFrame:
    rows = []
    conditions = ["healthy", "respiratory_distress", "tremor_escalation"]

    for pid in range(n_patients):
        baseline = simulate_patient_baseline()
        condition = RNG.choice(conditions, p=[0.4, 0.3, 0.3])

        if condition == "healthy":
            severities = RNG.uniform(0, 0.15, windows_per_patient)
            severities.sort()
            hours_to_event = [None] * windows_per_patient
        else:
            # ramp severity up over the window sequence, simulating the
            # hours-ahead deterioration trajectory the twin should catch
            severities = np.linspace(0.05, 0.95, windows_per_patient) ** 1.5
            total_hours = RNG.uniform(4, 8)
            hours_to_event = list(np.linspace(total_hours, 0, windows_per_patient))

        for i, sev in enumerate(severities):
            window = simulate_window(baseline, sev, condition)
            vec = build_feature_vector(window, baseline)
            label = 0 if condition == "healthy" or sev < 0.35 else 1
            row = dict(zip(FEATURE_NAMES, vec))
            row.update({
                "patient_id": f"P{pid:03d}",
                "condition": condition,
                "severity": sev,
                "label": label,
                "hours_to_event": hours_to_event[i],
            })
            rows.append(row)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_dataset()
    out_path = "data/synthetic_dataset.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")
    print(df["label"].value_counts())
    print(df["condition"].value_counts())
