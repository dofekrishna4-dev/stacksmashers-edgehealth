const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function getPrediction(patientId) {
  const res = await fetch(`${BASE_URL}/prediction?patient_id=${patientId}`);
  return res.json();
}

export async function getDigitalTwin(patientId) {
  const res = await fetch(`${BASE_URL}/digital-twin?patient_id=${patientId}`);
  return res.json();
}

export async function getAlerts(patientId) {
  const res = await fetch(`${BASE_URL}/alerts?patient_id=${patientId}`);
  return res.json();
}

export async function acknowledgeAlert(alertId, patientId) {
  const res = await fetch(`${BASE_URL}/alerts/acknowledge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ alert_id: alertId, patient_id: patientId }),
  });
  return res.json();
}

export async function askAssistant(patientId, message) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patient_id: patientId, message }),
  });
  return res.json();
}

export async function postHealthData(payload) {
  const res = await fetch(`${BASE_URL}/health-data`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}
