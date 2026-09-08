import React from "react";

/**
 * Lightweight inline SVG sparkline -- no external chart library
 * dependency required, so it renders with zero extra install steps.
 * Swap for Recharts/Chart.js in production if richer interaction
 * (tooltips, zoom) is needed.
 */
export default function TrendChart({ points = [], baseline, label, width = 320, height = 100 }) {
  if (!points.length) return null;
  const max = Math.max(...points, baseline || 0);
  const min = Math.min(...points, baseline || 0);
  const range = max - min || 1;

  const coords = points.map((v, i) => {
    const x = (i / (points.length - 1)) * width;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  }).join(" ");

  const baselineY = baseline != null ? height - ((baseline - min) / range) * height : null;

  return (
    <div>
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <svg width={width} height={height} className="overflow-visible">
        {baselineY != null && (
          <line x1={0} y1={baselineY} x2={width} y2={baselineY}
                stroke="#9ca3af" strokeDasharray="4 4" strokeWidth="1" />
        )}
        <polyline points={coords} fill="none" stroke="#2563eb" strokeWidth="2" />
      </svg>
    </div>
  );
}
