import React, { useState } from "react";
import usePatientData from "../hooks/usePatientData";

export default function PatientProfile() {
  const [patientId] = useState("P001");
  const { twin, loading } = usePatientData(patientId);

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-4">
      <h1 className="text-xl font-medium">Patient profile</h1>
      <div className="text-sm text-gray-600">Patient ID: {patientId}</div>
      {!loading && twin && (
        <div className="rounded-xl border border-gray-200 p-4">
          <div className="text-sm font-medium mb-2">Personal baseline</div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(twin.baseline).map(([k, v]) => (
              <div key={k}>
                <span className="text-gray-500 capitalize">{k.replace("_", " ")}: </span>
                <span className="font-medium">{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
