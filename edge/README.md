# Edge inference

This directory holds the TinyML deployment artifacts that run on the
wearable node (ESP32-S3 / nRF5340) and the hub device (Raspberry Pi
4 / Jetson Nano):

- `models/` - quantized .tflite classifiers (tremor, respiratory anomaly)
- `agents/` - Python agent implementations that run on the hub
- `mesh/` - BLE mesh sync logic for federated weight-delta exchange

For the hackathon MVP, start by replaying recorded/simulated sensor
data through the classifiers before wiring up live hardware.
