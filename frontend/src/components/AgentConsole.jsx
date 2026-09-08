import React from "react";

/**
 * Shows the multi-agent consensus vote -- the "agents deliberating"
 * panel that's the highest-visual-impact moment in a live demo.
 */
export default function AgentConsole({ votingAgents = {}, consensusReached }) {
  const agentLabels = {
    prediction_agent: "Prediction agent",
    risk_assessment_agent: "Risk assessment agent",
  };

  return (
    <div className="rounded-xl border border-gray-200 p-4">
      <div className="text-sm font-medium mb-3">Agent consensus</div>
      <div className="space-y-2">
        {Object.entries(votingAgents).map(([key, vote]) => (
          <div key={key} className="flex items-center justify-between text-sm">
            <span>{agentLabels[key] || key}</span>
            <span className={vote ? "text-red-600 font-medium" : "text-gray-400"}>
              {vote ? "flags risk" : "no concern"}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-3 pt-3 border-t text-sm font-medium">
        {consensusReached ? (
          <span className="text-red-600">Consensus reached — alert dispatched</span>
        ) : (
          <span className="text-gray-500">No consensus — no alert fired</span>
        )}
      </div>
    </div>
  );
}
