import React, { useState } from "react";
import usePatientData from "../hooks/usePatientData";
import TrendChart from "../components/TrendChart";

export default function DigitalTwin() {
  const [patientId] = useState("P001");
  const { twin, loading } = usePatientData(patientId);

  if (loading || !twin) {
    return <div className="p-6 text-sm text-gray-500">Loading digital twin...</div>;
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-medium">Digital twin</h1>
        <p className="text-sm text-gray-500">Patient {patientId}</p>
      </div>

      <div className="rounded-xl border border-gray-200 p-4">
        <div className="text-sm font-medium mb-1">Projection</div>
        <div className="text-sm text-gray-600">
          Trend: <span className="font-medium">{twin.projection.trend}</span>
          {twin.projection.horizon_hours != null && (
            <> — predicted threshold breach in ~{twin.projection.horizon_hours}h</>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {Object.entries(twin.current).map(([key, value]) => (
          <TrendChart
            key={key}
            label={`${key} (current: ${value}, baseline: ${twin.baseline[key]})`}
            points={[twin.baseline[key], value]}
            baseline={twin.baseline[key]}
          />
        ))}
      </div>
    </div>
  );
}
