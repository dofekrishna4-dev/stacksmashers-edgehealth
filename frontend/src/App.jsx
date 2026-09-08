import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import PatientProfile from "./pages/PatientProfile";
import DigitalTwin from "./pages/DigitalTwin";
import Alerts from "./pages/Alerts";
import HealthReports from "./pages/HealthReports";
import AIAssistant from "./pages/AIAssistant";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/profile" element={<PatientProfile />} />
        <Route path="/digital-twin" element={<DigitalTwin />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/reports" element={<HealthReports />} />
        <Route path="/assistant" element={<AIAssistant />} />
      </Routes>
    </BrowserRouter>
  );
}
