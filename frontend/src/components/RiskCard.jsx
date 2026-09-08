import React from "react";

const TIER_COLORS = {
  low: "bg-green-100 text-green-800 border-green-300",
  medium: "bg-amber-100 text-amber-800 border-amber-300",
  high: "bg-orange-100 text-orange-800 border-orange-300",
  critical: "bg-red-100 text-red-800 border-red-300",
};

export default function RiskCard({ condition, horizonHours, trend, tier = "low" }) {
  const colorClass = TIER_COLORS[tier] || TIER_COLORS.low;
  return (
    <div className={`rounded-xl border p-6 ${colorClass}`}>
      <div className="text-sm uppercase tracking-wide opacity-70">Current risk tier</div>
      <div className="text-3xl font-semibold mt-1 capitalize">{tier}</div>
      {condition && (
        <div className="mt-3 text-sm">
          Predicted <span className="font-medium">{condition.replace("_", " ")}</span>
          {horizonHours != null && (
            <> within approximately <span className="font-medium">{horizonHours}h</span></>
          )}
        </div>
      )}
      {trend && <div className="mt-1 text-sm opacity-80">Trend: {trend}</div>}
    </div>
  );
}
