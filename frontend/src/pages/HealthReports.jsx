import React from "react";

export default function HealthReports() {
  return (
    <div className="p-6 max-w-2xl mx-auto space-y-4">
      <h1 className="text-xl font-medium">Health reports</h1>
      <p className="text-sm text-gray-500">
        Exportable clinician-visit summaries generated from the patient's
        digital twin history. Wire this page to a `GET /reports` backend
        endpoint backed by the `reports` table in database/schema.sql.
      </p>
    </div>
  );
}
