import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function RespiratoryPanel({ coughFreq, wheeze, trend = [] }) {
  return (
    <div className="rounded-panel border border-line bg-base-900 p-5 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <span className="text-cyan-accent text-lg">&#9906;</span>
        <span className="text-sm font-medium tracking-wide">Respiratory health module</span>
      </div>

      <div className="flex items-center gap-2 text-xs">
        <span className="text-ink-muted">Status</span>
        <span className="text-cyan-accent font-medium">Persistent monitoring</span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <div className="text-ink-muted text-xs mb-1">Cough frequency</div>
          <div className="text-ink-primary font-medium">{coughFreq ?? "--"}/hr</div>
        </div>
        <div>
          <div className="text-ink-muted text-xs mb-1">Wheeze detection</div>
          <div className="text-ink-primary font-medium">{wheeze ?? "None"}</div>
        </div>
      </div>

      <div>
        <div className="chart-title">24h cough trend</div>
        <ResponsiveContainer width="100%" height={140}>
          <AreaChart data={trend}>
            <defs>
              <linearGradient id="coughFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3fd8e0" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#3fd8e0" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: "#5d6690", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#5d6690", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              width={24}
            />
            <Tooltip
              contentStyle={{
                background: "#0d1220",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "10px",
                fontSize: "12px",
              }}
              labelStyle={{ color: "#96a0c0" }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#3fd8e0"
              strokeWidth={2}
              fill="url(#coughFill)"
              isAnimationActive
              animationDuration={400}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}