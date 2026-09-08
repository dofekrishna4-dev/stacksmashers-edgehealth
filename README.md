# EdgeHealth Guardian Network

**Predicting medical emergencies hours before they happen — entirely offline.**

EdgeHealth Guardian Network is a privacy-first, multi-agent AI health platform that runs completely on edge devices. It builds a personalized "Digital Twin" of each patient's physiology, uses a crew of cooperating on-device AI agents to reason about it, and predicts respiratory distress, falls, cardiac abnormalities, and fatigue-related incidents hours before they occur — with zero cloud dependency for the core detection path.

## Why this is different

Most health-monitoring systems detect problems *after* they start and require constant cloud connectivity to do even that. EdgeHealth Guardian:

- Runs 100% on edge hardware — works with no internet at all.
- Uses **multi-agent consensus**, not a single model, before firing an alert — reducing false positives.
- Predicts **2-6 hours ahead** using a personal digital twin, not just detects in the moment.
- Improves the whole device network via **federated learning** without ever sending raw health data anywhere.

## Architecture

Sensors → Edge device → Data processing → Multi-agent layer → Digital twin layer → Prediction layer → Alert layer → Caregiver dashboard.

See [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) for the full architecture, agent design, ML pipeline, and RAG assistant details.

## Repo structure

```
edgehealth-guardian/
├── docs/               # Full technical blueprint
├── database/           # PostgreSQL schema
├── backend/            # FastAPI caregiver-dashboard API
│   └── app/
│       ├── agents/     # Agent base class + implementations
│       ├── routers/    # REST endpoints
│       ├── models/     # DB models
│       ├── core/       # Config, security
│       └── services/   # Business logic
├── frontend/           # React + Tailwind dashboard
│   └── src/
│       ├── pages/      # Dashboard, Digital Twin, Alerts, AI Assistant, etc.
│       ├── components/
│       ├── services/   # API client
│       └── hooks/
├── edge/                # Edge-device (TinyML) inference code
└── deployment/          # Docker / deployment configs
```

## Tech stack

- **Frontend:** React, Tailwind CSS
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Vector DB:** ChromaDB
- **AI/ML:** TensorFlow / TensorFlow Lite Micro, scikit-learn, XGBoost, LightGBM, LangChain, a quantized local LLM
- **Federated learning:** Flower (flwr)
- **Edge hardware:** ESP32-S3 / nRF5340 wearable node, Raspberry Pi 4 / Jetson Nano hub
- **Deployment:** Docker

## Getting started

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database
psql -f database/schema.sql
```

## Team

Built for [Hackathon Name] by [Team Name].

## License

MIT


## What's actually implemented (not just described)

This isn't only documentation — the ML pipeline, digital twin engine,
all 8 multi-agent implementations, the RAG service, and the federated
swarm sync protocol are real, tested Python code that runs end to end
in this repo. See [`BUILD_STATUS.md`](BUILD_STATUS.md) for exactly
what's been executed and verified versus what needs a dependency or
hardware this environment doesn't have (TensorFlow, Node.js, real BLE
radios, network access). Quick proof:

```bash
cd backend && python3 -m unittest discover -s tests -v   # 12 tests, all passing
python3 edge/run_simulation.py                            # full agent pipeline, live output
python3 edge/mesh/federated_swarm.py                       # federated sync demo
```
