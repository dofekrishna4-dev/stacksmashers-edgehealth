import React, { useState } from "react";
import { askAssistant } from "../services/api";

export default function AIAssistant() {
  const [patientId] = useState("P001");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setSending(true);
    try {
      const res = await askAssistant(patientId, userMsg.text);
      setMessages((m) => [...m, { role: "assistant", text: res.response }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto flex flex-col h-full">
      <h1 className="text-xl font-medium mb-4">AI assistant</h1>
      <div className="flex-1 space-y-3 mb-4 overflow-y-auto">
        {messages.map((m, i) => (
          <div key={i} className={`text-sm p-3 rounded-lg ${m.role === "user" ? "bg-blue-50 ml-auto max-w-[80%]" : "bg-gray-50 max-w-[80%]"}`}>
            {m.text}
          </div>
        ))}
        {sending && <div className="text-sm text-gray-400">Thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
          value={input}
          placeholder="Ask about this patient's patterns..."
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button
          className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm disabled:opacity-50"
          onClick={send}
          disabled={sending}
        >
          Send
        </button>
      </div>
    </div>
  );
}
