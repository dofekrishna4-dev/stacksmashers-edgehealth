import React from "react";

export default function PredictedRiskPanel({ condition, trend, horizonHours }) {
  const hasForecast = condition || trend;

  return (
    <div className="rounded-panel border border-violet-accent bg-base-850 p-5 flex flex-col justify-center">
      <div className="text-xs text-ink-muted mb-1">
        Predicted risk{horizonHours ? ` (next ${horizonHours}h)` : ""}
      </div>
      {hasForecast ? (
        <>
          <div className="text-2xl font-semibold text-violet-accent capitalize mb-1">
            {condition || "Unknown"}
          </div>
          {trend && (
            <div className="text-xs text-ink-secondary">Trend: {trend}</div>
          )}
        </>
      ) : (
        <div className="text-sm text-ink-muted">No forecast data yet</div>
      )}
    </div>
  );
}