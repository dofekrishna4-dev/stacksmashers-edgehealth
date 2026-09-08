import React from "react";

const TIER_DOT = { low: "bg-green-500", medium: "bg-amber-500", high: "bg-orange-500", critical: "bg-red-500" };

export default function AlertList({ alerts = [], onAcknowledge }) {
  if (!alerts.length) {
    return <div className="text-sm text-gray-500">No alerts yet.</div>;
  }
  return (
    <ul className="divide-y divide-gray-200">
      {alerts.slice().reverse().map((alert, i) => (
        <li key={i} className="py-3 flex items-start gap-3">
          <span className={`mt-1 h-2 w-2 rounded-full ${TIER_DOT[alert.tier] || "bg-gray-400"}`} />
          <div className="flex-1">
            <div className="text-sm">{alert.message}</div>
            <div className="text-xs text-gray-400 mt-1">via {alert.channel}</div>
          </div>
          {!alert.acknowledged && onAcknowledge && (
            <button
              className="text-xs px-2 py-1 rounded border border-gray-300 hover:bg-gray-50"
              onClick={() => onAcknowledge(alert)}
            >
              Acknowledge
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}
