import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import CheckOffer from './pages/CheckOffer';
import FraudNetwork from './pages/FraudNetwork';
import AiAssistant from './pages/AiAssistant';
import ReportIncident from './pages/ReportIncident';
import InvestigationHistory from './pages/InvestigationHistory';
import SafetyCentre from './pages/SafetyCentre';

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="check-offer" element={<CheckOffer />} />
            <Route path="network" element={<FraudNetwork />} />
            <Route path="assistant" element={<AiAssistant />} />
            <Route path="report" element={<ReportIncident />} />
            <Route path="history" element={<InvestigationHistory />} />
            <Route path="safety" element={<SafetyCentre />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
