import React from "react";

const TIER_STYLES = {
  Low: {
    text: "text-teal-accent",
    bg: "bg-base-850",
    border: "border-teal-accent",
  },
  Medium: {
    text: "text-amber-400",
    bg: "bg-base-850",
    border: "border-amber-400",
  },
  High: {
    text: "text-red-400",
    bg: "bg-base-850",
    border: "border-red-400",
  },
};

export default function RiskPanel({ tier = "Low", label = "Current risk" }) {
  const style = TIER_STYLES[tier] || TIER_STYLES.Low;

  return (
    <div
      className={`rounded-panel border ${style.border} ${style.bg} p-5 flex flex-col justify-center`}
    >
      <div className="text-xs text-ink-muted mb-1">{label}</div>
      <div className={`text-2xl font-semibold ${style.text}`}>{tier} risk</div>
    </div>
  );
}