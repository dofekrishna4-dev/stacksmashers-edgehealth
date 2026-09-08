import React from "react";

const ITEMS = [
  {
    icon: "\u25C9",
    title: "System status rail",
    body: "Live orchestrator health and inference status.",
  },
  {
    icon: "\u25CB",
    title: "Respiratory health panel",
    body: "Cough frequency, wheeze detection, 24h trend line.",
  },
  {
    icon: "\u2726",
    title: "Motor stability map",
    body: "Heat-map of tremor intensity and rolling stability score.",
  },
  {
    icon: "\u2724",
    title: "Weekly synthetic analysis",
    body: "AI-narrated correlation between motor and respiratory recovery.",
  },
  {
    icon: "\u26A0",
    title: "Alerts and encrypted logs",
    body: "Real-time alerts with one-tap export of a hashed audit trail.",
  },
];

export default function CaregiverInsightPanel() {
  return (
    <div className="rounded-panel border border-line bg-base-900 p-5 flex flex-col gap-5 h-full">
      <div className="text-sm font-medium tracking-wide">What caregivers see</div>

      <div className="flex flex-col gap-4">
        {ITEMS.map((item) => (
          <div key={item.title} className="flex gap-3">
            <span className="text-cyan-accent mt-0.5 text-sm">{item.icon}</span>
            <div>
              <div className="text-sm text-ink-primary font-medium">{item.title}</div>
              <div className="text-xs text-ink-secondary leading-relaxed mt-0.5">{item.body}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-auto rounded-lg bg-base-850 border border-line p-4">
        <div className="meta-label text-[10px] text-violet-accent mb-2">
          Patient and caregiver gain
        </div>
        <p className="text-xs text-ink-secondary leading-relaxed">
          Non-clinicians read one glance-scannable status; patients get pre-symptomatic
          warnings without wearing a "spy device."
        </p>
      </div>
    </div>
  );
}