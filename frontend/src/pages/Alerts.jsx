import React, { useState } from "react";
import usePatientData from "../hooks/usePatientData";
import AlertList from "../components/AlertList";

export default function Alerts() {
  const [patientId] = useState("P001");
  const { alerts, loading, ack } = usePatientData(patientId);

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <h1 className="text-xl font-medium">Alerts</h1>
      {loading ? (
        <div className="text-sm text-gray-500">Loading...</div>
      ) : (
        <AlertList alerts={alerts} onAcknowledge={ack} />
      )}
    </div>
  );
}
