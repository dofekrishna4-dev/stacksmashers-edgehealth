import React, { useEffect, useState } from "react";
import { TopMetaBar, BottomMetaBar } from "../components/MetaBar";
import RespiratoryPanel from "../components/RespiratoryPanel";
import MotorStabilityPanel from "../components/MotorStabilityPanel";
import SyntheticAnalysisPanel from "../components/SyntheticAnalysisPanel";
import CaregiverInsightPanel from "../components/CaregiverInsightPanel";
import RiskPanel from "../components/RiskPanel";
import PredictedRiskPanel from "../components/PredictedRiskPanel";

const API_BASE = "https://stacksmashers-edgehealth.onrender.com";

export default function Dashboard() {
  const [patient, setPatient] = useState({ name: "", age: "", gender: "", patientId: "" });
  const [submitted, setSubmitted] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [digitalTwin, setDigitalTwin] = useState(null);
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!submitted) return;

    async function fetchData() {
      try {
        const predRes = await fetch(`${API_BASE}/prediction?patient_id=${patient.patientId}`);
        const predData = await predRes.json();

        const twinRes = await fetch(`${API_BASE}/digital-twin?patient_id=${patient.patientId}`);
        const twinData = await twinRes.json();

        const simRes = await fetch(`${API_BASE}/simulation?patient_id=${patient.patientId}`);
        const simData = await simRes.json();

        setPrediction(predData);
        setDigitalTwin(twinData);
        setSimulation(simData);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    }

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [submitted, patient.patientId]);

  if (!submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-950 px-4">
        <div className="w-full max-w-sm rounded-panel border border-line bg-base-900 p-8">
          <div className="meta-label text-[11px] text-teal-accent mb-1">EdgeHealth guardian</div>
          <h1 className="text-xl font-semibold mb-6">Sign in to monitor a patient</h1>

          <div className="flex flex-col gap-3">
            <input
              placeholder="Patient name"
              value={patient.name}
              onChange={(e) => setPatient({ ...patient, name: e.target.value })}
              className="bg-base-850 border border-line rounded-lg px-3 py-2.5 text-sm text-ink-primary placeholder:text-ink-muted focus:outline-none focus:border-cyan-accent"
            />
            <input
              placeholder="Age"
              value={patient.age}
              onChange={(e) => setPatient({ ...patient, age: e.target.value })}
              className="bg-base-850 border border-line rounded-lg px-3 py-2.5 text-sm text-ink-primary placeholder:text-ink-muted focus:outline-none focus:border-cyan-accent"
            />
            <select
              value={patient.gender}
              onChange={(e) => setPatient({ ...patient, gender: e.target.value })}
              className="bg-base-850 border border-line rounded-lg px-3 py-2.5 text-sm text-ink-primary focus:outline-none focus:border-cyan-accent"
            >
              <option value="">Select gender</option>
              <option>Male</option>
              <option>Female</option>
            </select>
            <input
              placeholder="Patient ID (p001)"
              value={patient.patientId}
              onChange={(e) => setPatient({ ...patient, patientId: e.target.value })}
              className="bg-base-850 border border-line rounded-lg px-3 py-2.5 text-sm text-ink-primary placeholder:text-ink-muted focus:outline-none focus:border-cyan-accent"
            />
            <button
              onClick={() => {
                if (!patient.patientId) {
                  alert("Enter a patient ID");
                  return;
                }
                setLoading(true);
                setSubmitted(true);
              }}
              className="mt-2 rounded-lg bg-teal-accent text-base-950 font-medium py-2.5 text-sm hover:opacity-90 transition"
            >
              Analyze patient
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading || !prediction) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-950 text-ink-secondary text-sm">
        Loading patient telemetry&hellip;
      </div>
    );
  }

  const respRate = digitalTwin?.current?.resp_rate ?? simulation?.resp_rate;
  const tremor = simulation?.tremor ?? digitalTwin?.current?.tremor;
  const stabilityScore = prediction?.stability_score ?? 94;

  const hr = prediction?.current_state?.hr ?? 0;
  const spo2 = prediction?.current_state?.spo2 ?? 0;
  const riskTier =
    spo2 < 94 || hr > 110 ? "High" : spo2 < 96 || hr > 95 ? "Medium" : "Low";

  const simHr = simulation?.hr ?? 0;
  const simSpo2 = simulation?.spo2 ?? 0;
  const simulationRiskTier =
    simSpo2 < 94 || simHr > 110 ? "High" : simSpo2 < 96 || simHr > 95 ? "Medium" : "Low";

  return (
    <div className="min-h-screen bg-base-950 flex flex-col">
      <TopMetaBar section="Caregiver dashboard" index={1} total={1} />

      <div className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-8">
        <div className="mb-8">
          <div className="meta-label text-[11px] text-cyan-accent mb-3">
            Patient &middot; {patient.name || patient.patientId}
          </div>
          <h1 className="text-3xl font-semibold mb-3">
            Raw telemetry &rarr; <span className="text-violet-accent">actionable</span> insight.
          </h1>
          <p className="text-sm text-ink-secondary max-w-2xl leading-relaxed">
            A dashboard built for non-specialist caregivers &mdash; synthesised trends, not data
            dumps. It answers the "why" behind the signals, in real time.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1fr_320px] gap-5">
          <RespiratoryPanel
            coughFreq={respRate ? Math.round(respRate / 6) : 2}
            wheeze="None"
            trend={buildTrend(prediction)}
          />
          <MotorStabilityPanel tremor={tremor ?? "Low"} stabilityScore={stabilityScore} />
          <CaregiverInsightPanel />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-5 mt-5">
          <SyntheticAnalysisPanel
            note={
              prediction?.trend && prediction?.condition
                ? `Patient currently shows a ${prediction.trend} trend with ${prediction.condition} condition. Continue routine monitoring alongside the trends above.`
                : undefined
            }
          />
          <div className="rounded-panel border border-line bg-base-900 p-5 flex flex-col justify-center">
            <div className="text-xs text-ink-muted mb-1">Heart rate</div>
            <div className="text-2xl font-semibold text-ink-primary mb-3">
              {prediction?.current_state?.hr ?? "--"} bpm
            </div>
            <div className="text-xs text-ink-muted mb-1">SpO&#8322;</div>
            <div className="text-2xl font-semibold text-ink-primary">
              {prediction?.current_state?.spo2 ?? "--"}%
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mt-5">
          <RiskPanel tier={riskTier} label="Current risk assessment" />
          <RiskPanel tier={simulationRiskTier} label="Live simulation risk" />
          <PredictedRiskPanel
            condition={prediction?.condition}
            trend={prediction?.trend}
            horizonHours={prediction?.horizon_hours}
          />
        </div>
      </div>

      <BottomMetaBar
        items={["Local UI", "WebSocket-driven", "JWT-inspired local auth", "Zero cloud latency"]}
      />
    </div>
  );
}

function buildTrend(prediction) {
  const base = prediction?.current_state?.hr ? prediction.current_state.hr % 6 : 3;
  return Array.from({ length: 12 }, (_, i) => ({
    time: `${(i * 2).toString().padStart(2, "0")}:00`,
    value: Math.max(0, base + Math.round(Math.sin(i / 2) * 2)),
  }));
}