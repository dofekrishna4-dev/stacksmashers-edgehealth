import { useEffect, useState } from "react";
import { getPrediction, getDigitalTwin, getAlerts, acknowledgeAlert } from "../services/api";

export default function usePatientData(patientId, pollMs = 5000) {
  const [prediction, setPrediction] = useState(null);
  const [twin, setTwin] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      const [p, t, a] = await Promise.all([
        getPrediction(patientId),
        getDigitalTwin(patientId),
        getAlerts(patientId),
      ]);
      setPrediction(p);
      setTwin(t);
      setAlerts(a.alerts || []);
    } catch (err) {
      console.error("Failed to load patient data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, pollMs);
    return () => clearInterval(id);
  }, [patientId]);

  const ack = async (alert) => {
    await acknowledgeAlert(alert.id, patientId);
    refresh();
  };

  return { prediction, twin, alerts, loading, refresh, ack };
}
