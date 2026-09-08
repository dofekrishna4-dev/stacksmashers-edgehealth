"""Feature engineering for EdgeHealth Guardian classifiers.

Turns windowed raw-ish sensor signals into the engineered feature
vector used by both the tabular classifiers (RandomForest/XGBoost)
and the digital twin's anomaly scoring.
"""
from __future__ import annotations
import numpy as np

FEATURE_NAMES = [
    "hr_mean", "hr_std", "hr_dev_from_baseline",
    "spo2_mean", "spo2_min", "spo2_dev_from_baseline",
    "resp_rate_mean", "resp_rate_std", "resp_rate_dev_from_baseline",
    "tremor_band_power", "tremor_dominant_freq",
    "activity_level", "activity_dev_from_baseline",
    "breath_tremor_correlation",
]


def hrv_features(hr_window: np.ndarray) -> dict:
    """Simple heart-rate-variability-style stats from a beat-rate window."""
    return {
        "hr_mean": float(np.mean(hr_window)),
        "hr_std": float(np.std(hr_window)),
    }


def tremor_band_power(accel_window: np.ndarray, fs: float = 50.0,
                       band=(3.0, 7.0)) -> tuple[float, float]:
    """FFT-based band power in the Parkinsonian tremor band (3-7 Hz)
    plus the dominant frequency in that band."""
    n = len(accel_window)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    spectrum = np.abs(np.fft.rfft(accel_window - np.mean(accel_window))) ** 2
    band_mask = (freqs >= band[0]) & (freqs <= band[1])
    band_power = float(np.sum(spectrum[band_mask])) if band_mask.any() else 0.0
    if band_mask.any() and spectrum[band_mask].sum() > 0:
        dominant_freq = float(freqs[band_mask][np.argmax(spectrum[band_mask])])
    else:
        dominant_freq = 0.0
    return band_power, dominant_freq


def breath_tremor_correlation(resp_window: np.ndarray, accel_window: np.ndarray) -> float:
    """Cross-modal correlation feature used by the correlation agent to
    catch overlap conditions (e.g. respiratory distress co-occurring
    with new tremor onset)."""
    n = min(len(resp_window), len(accel_window))
    if n < 2:
        return 0.0
    r = np.corrcoef(resp_window[:n], accel_window[:n])[0, 1]
    return float(0.0 if np.isnan(r) else r)


def build_feature_vector(window: dict, baseline: dict) -> np.ndarray:
    """window: dict of raw arrays for this time window
       baseline: dict of the patient's personal baseline scalars
       Returns a feature vector in FEATURE_NAMES order.
    """
    hr = hrv_features(window["hr"])
    band_power, dom_freq = tremor_band_power(window["accel"])
    corr = breath_tremor_correlation(window["resp"], window["accel"])

    spo2_mean = float(np.mean(window["spo2"]))
    spo2_min = float(np.min(window["spo2"]))
    resp_mean = float(np.mean(window["resp_rate"]))
    resp_std = float(np.std(window["resp_rate"]))
    activity = float(np.mean(window["activity"]))

    vec = [
        hr["hr_mean"], hr["hr_std"], hr["hr_mean"] - baseline["hr"],
        spo2_mean, spo2_min, spo2_mean - baseline["spo2"],
        resp_mean, resp_std, resp_mean - baseline["resp_rate"],
        band_power, dom_freq,
        activity, activity - baseline["activity"],
        corr,
    ]
    return np.array(vec, dtype=np.float32)
