import React from "react";

export default function SyntheticAnalysisPanel({ respiratoryDelta, tremorDelta, note }) {
  const summary =
    note ||
    `Analysis identifies a ${respiratoryDelta ?? 5}% improvement in respiratory stability following a ${tremorDelta ?? 12}% reduction in high-frequency tremors during night cycles. Correlation suggests improved lung recovery during deeper rest states.`;

  return (
    <div className="rounded-panel border border-line bg-base-900 p-5">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-violet-accent text-lg">&#10024;</span>
        <span className="text-sm font-medium tracking-wide text-violet-accent">
          Weekly synthetic analysis &mdash; AI core
        </span>
      </div>

      <p className="text-sm text-ink-secondary leading-relaxed mb-5">{summary}</p>

      <div className="flex items-center justify-center gap-8">
        <div className="flex flex-col items-center gap-1">
          <span className="text-cyan-accent text-xl">&#9906;</span>
          <span className="text-[11px] text-ink-muted text-center">Respiratory<br />stability</span>
        </div>
        <div className="flex flex-col items-center gap-1 text-violet-accent text-xs meta-label">
          <span className="text-lg leading-none">&#8644;</span>
          Correlation
        </div>
        <div className="flex flex-col items-center gap-1">
          <span className="text-teal-accent text-xl">&#9749;</span>
          <span className="text-[11px] text-ink-muted text-center">Motor<br />stability</span>
        </div>
      </div>
    </div>
  );
}