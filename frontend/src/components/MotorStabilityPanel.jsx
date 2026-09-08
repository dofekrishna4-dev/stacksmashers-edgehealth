import React from "react";

function stabilityColor(v) {
  if (v > 0.75) return "#34d399";
  if (v > 0.5) return "#5fbf8a";
  if (v > 0.25) return "#8a9d5f";
  return "#c9603a";
}

export default function MotorStabilityPanel({ tremor, stabilityScore, cells = [] }) {
  const grid = cells.length ? cells : Array.from({ length: 24 }, () => Math.random() * 0.6 + 0.35);

  return (
    <div className="rounded-panel border border-line bg-base-900 p-5 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <span className="text-teal-accent text-lg">&#9749;</span>
        <span className="text-sm font-medium tracking-wide">Motor stability module</span>
      </div>

      <div className="flex items-center gap-2 text-xs">
        <span className="text-ink-muted">Status</span>
        <span className="text-teal-accent font-medium">Real-time active</span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <div className="text-ink-muted text-xs mb-1">Tremor intensity</div>
          <div className="text-ink-primary font-medium">{tremor ?? "Low"}</div>
        </div>
        <div>
          <div className="text-ink-muted text-xs mb-1">Stability score</div>
          <div className="text-ink-primary font-medium">{stabilityScore ?? "--"}%</div>
        </div>
      </div>

      <div>
        <div className="chart-title">Motor stability map</div>
        <div className="flex items-stretch gap-3">
          <div className="flex flex-col justify-between text-[10px] text-ink-muted py-1">
            <span>High</span>
            <span>Low</span>
          </div>
          <div className="grid grid-cols-8 gap-1 flex-1">
            {grid.map((v, i) => (
              <div
                key={i}
                className="aspect-square rounded-sm"
                style={{ background: stabilityColor(v) }}
                title={`Hour ${i}: ${Math.round(v * 100)}% stability`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}