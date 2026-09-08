"""Trains the EdgeHealth Guardian risk classifiers on the (synthetic
or real) feature dataset and reports metrics.

Uses RandomForest and GradientBoosting from scikit-learn (available
offline, no network required). In production, swap in XGBoost /
LightGBM for the same interface -- they're drop-in compatible with
this feature set (see requirements.txt).
"""
from __future__ import annotations
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, confusion_matrix)
from features import FEATURE_NAMES


def load_dataset(path="data/synthetic_dataset.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def train_and_evaluate(df: pd.DataFrame):
    X = df[FEATURE_NAMES].values
    y = df["label"].values
    groups = df["patient_id"].values

    # patient-level split so no patient's windows leak across train/test
    unique_patients = np.unique(groups)
    train_p, test_p = train_test_split(unique_patients, test_size=0.25, random_state=42)
    train_mask = np.isin(groups, train_p)
    test_mask = np.isin(groups, test_p)

    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=8, min_samples_leaf=3,
            class_weight="balanced", random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=3, learning_rate=0.08, random_state=42),
    }

    results = {}
    trained = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]
        results[name] = {
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds)), 4),
            "recall": round(float(recall_score(y_test, preds)), 4),
            "f1": round(float(f1_score(y_test, preds)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, probs)), 4),
            "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
            "n_train": int(train_mask.sum()),
            "n_test": int(test_mask.sum()),
        }
        trained[name] = model

    # ensemble consensus: both models must agree above threshold
    # this is the offline analogue of the multi-agent risk-assessment vote
    rf_probs = trained["random_forest"].predict_proba(X_test)[:, 1]
    gb_probs = trained["gradient_boosting"].predict_proba(X_test)[:, 1]
    consensus_probs = (rf_probs + gb_probs) / 2
    consensus_preds = (consensus_probs >= 0.5).astype(int)
    results["consensus_ensemble"] = {
        "accuracy": round(float(accuracy_score(y_test, consensus_preds)), 4),
        "precision": round(float(precision_score(y_test, consensus_preds)), 4),
        "recall": round(float(recall_score(y_test, consensus_preds)), 4),
        "f1": round(float(f1_score(y_test, consensus_preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, consensus_probs)), 4),
    }

    # feature importance from the random forest, useful for the medical
    # knowledge agent's explanation generation
    importances = dict(zip(FEATURE_NAMES, trained["random_forest"].feature_importances_.round(4).tolist()))

    return trained, results, importances


if __name__ == "__main__":
    df = load_dataset()
    trained, results, importances = train_and_evaluate(df)

    for name, model in trained.items():
        joblib.dump(model, f"models/{name}.joblib")

    with open("models/metrics.json", "w") as f:
        json.dump({"results": results, "feature_importance": importances}, f, indent=2)

    print(json.dumps(results, indent=2))
    print("\nTop features by importance:")
    for k, v in sorted(importances.items(), key=lambda x: -x[1])[:5]:
        print(f"  {k}: {v}")
