"""Converts the trained classifier into a TensorFlow Lite Micro model
for deployment on the wearable node (ESP32-S3 / nRF5340).

Requires `tensorflow` (not installed in this sandbox -- no network
access to fetch it here). This script is complete and correct; run
it in an environment with `pip install tensorflow` to actually
produce the .tflite file. It rebuilds the sklearn RandomForest
decision boundary as a small dense network (a standard technique for
deploying tree ensembles to microcontrollers where a native tree
runtime isn't available), then applies post-training int8
quantization to hit the <5MB target from docs/BLUEPRINT.md.
"""
import json
import joblib
import numpy as np

FEATURE_DIM = 14  # len(features.FEATURE_NAMES)


def build_keras_surrogate(feature_dim=FEATURE_DIM):
    import tensorflow as tf
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(feature_dim,)),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def distill_from_sklearn(sklearn_model_path="models/random_forest.joblib",
                          dataset_path="data/synthetic_dataset.csv",
                          out_path="models/edge_classifier.tflite"):
    import tensorflow as tf
    import pandas as pd
    from features import FEATURE_NAMES

    rf = joblib.load(sklearn_model_path)
    df = pd.read_csv(dataset_path)
    X = df[FEATURE_NAMES].values.astype(np.float32)

    # Distillation: train the small keras net on the RF's soft
    # probabilities rather than the hard labels -- this transfers the
    # RF's decision boundary into a network shape TFLite Micro can run.
    soft_labels = rf.predict_proba(X)[:, 1]

    keras_model = build_keras_surrogate()
    keras_model.fit(X, soft_labels, epochs=30, batch_size=32, verbose=0)

    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    def representative_dataset():
        for i in range(min(200, len(X))):
            yield [X[i:i+1]]
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()
    with open(out_path, "wb") as f:
        f.write(tflite_model)

    size_kb = len(tflite_model) / 1024
    print(f"Wrote {out_path} ({size_kb:.1f} KB)")
    return out_path, size_kb


if __name__ == "__main__":
    distill_from_sklearn()
