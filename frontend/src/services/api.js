// Centralized API client for OfferGraph

const API_BASE = '/api';

export const api = {
  // Dashboard
  async getDashboardStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to load dashboard stats');
    return res.json();
  },

  async getRecentReports(limit = 6) {
    const res = await fetch(`${API_BASE}/dashboard/recent-reports?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to load recent reports');
    return res.json();
  },

  async resetDemoData() {
    const res = await fetch(`${API_BASE}/dashboard/reset-demo-data`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset demo data');
    return res.json();
  },

  // Offer Analysis
  async analyzeOffer(formDataOrJson) {
    let options = {};
    if (formDataOrJson instanceof FormData) {
      options = {
        method: 'POST',
        body: formDataOrJson,
      };
    } else {
      const form = new FormData();
      form.append('text', formDataOrJson.text || '');
      options = {
        method: 'POST',
        body: form,
      };
    }
    const res = await fetch(`${API_BASE}/analyze`, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(err.detail || 'Analysis request failed');
    }
    return res.json();
  },

  async getAnalysisById(analysisId) {
    const res = await fetch(`${API_BASE}/analyze/${analysisId}`);
    if (!res.ok) throw new Error('Failed to load analysis record');
    return res.json();
  },

  // Incident Reports
  async submitReport(reportData) {
    const res = await fetch(`${API_BASE}/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to submit report' }));
      throw new Error(err.detail || 'Failed to submit report');
    }
    return res.json();
  },

  async getReports(params = {}) {
    const query = new URLSearchParams();
    if (params.risk_category) query.append('risk_category', params.risk_category);
    if (params.report_type) query.append('report_type', params.report_type);
    if (params.q) query.append('q', params.q);
    if (params.limit) query.append('limit', params.limit);
    if (params.offset) query.append('offset', params.offset);

    const res = await fetch(`${API_BASE}/reports?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to load reports');
    return res.json();
  },

  async getReportDetail(reportId) {
    const res = await fetch(`${API_BASE}/reports/${reportId}`);
    if (!res.ok) throw new Error('Failed to load report detail');
    return res.json();
  },

  // Graph Elements
  async getGraph(reportId = null) {
    const url = reportId ? `${API_BASE}/graph?report_id=${reportId}` : `${API_BASE}/graph`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to load graph elements');
    return res.json();
  },

  // Entity Details
  async getEntityConnections(entityId) {
    const res = await fetch(`${API_BASE}/entities/${entityId}/connections`);
    if (!res.ok) throw new Error('Failed to load entity connections');
    return res.json();
  },

  async searchEntities(q) {
    const res = await fetch(`${API_BASE}/entities/search?q=${encodeURIComponent(q)}`);
    if (!res.ok) throw new Error('Failed to search entities');
    return res.json();
  },

  // Chat
  async sendChatMessage(message, sessionId, context = null) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context,
      }),
    });
    if (!res.ok) throw new Error('Failed to process message with AI Investigator');
    return res.json();
  },

  async getChatHistory(sessionId) {
    const res = await fetch(`${API_BASE}/chat/history/${sessionId}`);
    if (!res.ok) throw new Error('Failed to load chat history');
    return res.json();
  },

  // Safety Resources
  async getSafetyResources() {
    const res = await fetch(`${API_BASE}/safety/resources`);
    if (!res.ok) throw new Error('Failed to load safety resources');
    return res.json();
  },
};
