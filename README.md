# EdgeHealth Orchestrator

🔗 **[Live demo](https://stacksmashers-edgehealth.vercel.app)**

Edge AI healthcare monitoring system for real-time respiratory and motor health tracking.

A caregiver-facing dashboard that turns raw patient telemetry into synthesised, actionable insight — built for non-specialist caregivers rather than clinicians.

## Features

- **Respiratory health module** — cough frequency, wheeze detection, 24h trend chart
- **Motor stability module** — tremor intensity, rolling stability score, hourly heat-map
- **Weekly synthetic analysis** — AI-narrated correlation between respiratory and motor recovery
- **Risk panels** — current risk assessment, live simulation risk, and predicted risk based on trend/condition
- **Alerts and encrypted logs** — real-time alerts with a hashed, exportable audit trail
- **What caregivers see** — a guided sidebar explaining each panel, with click-to-scroll navigation

## Tech stack

- **Frontend**: React, Vite, Tailwind CSS, Recharts
- **Backend**: FastAPI, SQLAlchemy, LangChain, ChromaDB
- **ML**: scikit-learn (Random Forest, Gradient Boosting), synthetic data generation, TFLite export

## Project structure

## Running locally

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://127.0.0.1:8000` (Swagger docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Both servers must be running simultaneously for the dashboard to load live patient data.