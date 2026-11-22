import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  Share2,
  FileText,
  AlertTriangle,
  Layers,
  ArrowRight,
  TrendingUp,
  Phone,
  Mail,
  Globe,
  CreditCard,
  Building,
  Sparkles,
  Info
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis
} from 'recharts';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentReports, setRecentReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [statsData, reportsData] = await Promise.all([
          api.getDashboardStats(),
          api.getRecentReports(6),
        ]);
        setStats(statsData);
        setRecentReports(reportsData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
        <p className="text-sm text-slate-400 font-mono">Aggregating Graph Intelligence...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300">
        <h3 className="font-semibold text-lg flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-rose-400" />
          Error Loading Intelligence Dashboard
        </h3>
        <p className="text-sm mt-1 text-rose-300/80">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const riskData = [
    { name: 'High Risk', value: stats?.high_risk_reports || 0, color: '#ef4444' },
    { name: 'Medium Risk', value: stats?.medium_risk_reports || 0, color: '#f59e0b' },
    { name: 'Low Risk', value: stats?.low_risk_reports || 0, color: '#10b981' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Synthetic Data Banner */}
      <div className="flex items-center justify-between p-3.5 px-4 rounded-xl bg-navy-900 border border-indigo-500/30 shadow-lg text-xs">
        <div className="flex items-center gap-2.5">
          <Info className="w-4 h-4 text-indigo-400 flex-shrink-0" />
          <span className="text-slate-300">
            <strong className="text-indigo-300 font-semibold uppercase tracking-wider">
              Synthetic Demonstration Data Active:
            </strong>{' '}
            All company names, recruiters, and contact identifiers displayed here are synthetic benchmarks created for hackathon evaluation and do not represent real individuals or live complaints.
          </span>
        </div>
        <button
          onClick={() => navigate('/check-offer')}
          className="hidden sm:flex items-center gap-1.5 font-medium text-cyan-400 hover:text-cyan-300 transition whitespace-nowrap ml-4"
        >
          <span>Test Live Offer</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Header & Tagline */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Fraud Intelligence Dashboard
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Don't just detect suspicious offers.{' '}
            <span className="text-cyan-400 font-medium">Connect the evidence.</span>
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => navigate('/check-offer')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-sm shadow-lg shadow-cyan-500/20 transition"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Check an Offer</span>
          </button>
          <button
            onClick={() => navigate('/network')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-700 border border-navy-700 text-slate-200 font-medium text-sm transition"
          >
            <Share2 className="w-4 h-4 text-purple-400" />
            <span>Open Fraud Graph</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="p-4 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Reports</span>
            <FileText className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2 font-mono">{stats?.total_reports || 0}</p>
          <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <span className="text-emerald-400 font-medium">100%</span> correlated in DB
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>High Risk Incidents</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-400 mt-2 font-mono">{stats?.high_risk_reports || 0}</p>
          <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <span className="text-rose-400 font-medium">&gt;60/100</span> severity score
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Connected Entities</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-indigo-300 mt-2 font-mono">{stats?.connected_entities || 0}</p>
          <p className="text-[11px] text-slate-400 mt-1">Phones, UPIs, Domains</p>
        </div>

        <div className="p-4 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-md">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Syndicate Clusters</span>
            <Share2 className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-purple-300 mt-2 font-mono">
            {stats?.suspicious_clusters_count || 0}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">Multi-report rings</p>
        </div>

        <div className="p-4 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-md col-span-2 md:col-span-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Graph Correlation</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400 mt-2 font-mono">87.5%</p>
          <p className="text-[11px] text-slate-400 mt-1">Cross-report overlap</p>
        </div>
      </div>

      {/* Middle Row: Risk Distribution & Top Connected Fraud Identifiers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Chart */}
        <div className="p-5 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-white text-base flex items-center justify-between">
              <span>Threat Distribution</span>
              <span className="text-xs text-slate-400 font-mono">Total: {stats?.total_reports}</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Incidents classified by explainable risk threshold
            </p>
          </div>

          <div className="h-48 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#0b1120" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '12px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-navy-800 text-xs">
            <div>
              <p className="text-rose-400 font-bold font-mono text-base">{stats?.high_risk_reports || 0}</p>
              <p className="text-[11px] text-slate-400">High Risk</p>
            </div>
            <div>
              <p className="text-amber-400 font-bold font-mono text-base">{stats?.medium_risk_reports || 0}</p>
              <p className="text-[11px] text-slate-400">Medium Risk</p>
            </div>
            <div>
              <p className="text-emerald-400 font-bold font-mono text-base">{stats?.low_risk_reports || 0}</p>
              <p className="text-[11px] text-slate-400">Low Risk</p>
            </div>
          </div>
        </div>

        {/* Top Connected Fraud Identifiers */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white text-base">Top Correlated Identifiers</h3>
              <span className="text-xs text-cyan-400 font-mono">Shared Across Multiple Reports</span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Identifiers appearing repeatedly across supposedly unrelated company postings
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 my-3">
            {/* Phone */}
            <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
              <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 mb-2">
                <Phone className="w-3.5 h-3.5" />
                <span>Frequently Reported Phones</span>
              </div>
              <div className="space-y-1.5">
                {(stats?.top_entities?.phones || []).slice(0, 3).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-200">{item.value}</span>
                    <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 font-mono text-[11px] border border-amber-500/20">
                      {item.count} reports
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* UPI */}
            <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
              <div className="flex items-center gap-2 text-xs font-semibold text-rose-400 mb-2">
                <CreditCard className="w-3.5 h-3.5" />
                <span>Flagged UPI Virtual Addresses</span>
              </div>
              <div className="space-y-1.5">
                {(stats?.top_entities?.upis || []).slice(0, 3).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-200">{item.value}</span>
                    <span className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 font-mono text-[11px] border border-rose-500/20">
                      {item.count} reports
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Email */}
            <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 mb-2">
                <Mail className="w-3.5 h-3.5" />
                <span>Shared Recruiter Webmail</span>
              </div>
              <div className="space-y-1.5">
                {(stats?.top_entities?.emails || []).slice(0, 3).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-200 truncate max-w-[170px]">{item.value}</span>
                    <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono text-[11px] border border-emerald-500/20">
                      {item.count} reports
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Domains */}
            <div className="p-3 rounded-xl bg-navy-950/70 border border-navy-800">
              <div className="flex items-center gap-2 text-xs font-semibold text-pink-400 mb-2">
                <Globe className="w-3.5 h-3.5" />
                <span>Suspicious Domains</span>
              </div>
              <div className="space-y-1.5">
                {(stats?.top_entities?.domains || []).slice(0, 3).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-200 truncate max-w-[170px]">{item.value}</span>
                    <span className="px-1.5 py-0.5 rounded bg-pink-500/10 text-pink-400 font-mono text-[11px] border border-pink-500/20">
                      {item.count} reports
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={() => navigate('/network')}
            className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-navy-800 hover:bg-navy-750 text-cyan-300 font-medium text-xs border border-navy-700 transition"
          >
            <span>Explore All Entity Linkages in Network Graph</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Recent Incident Reports Table */}
      <div className="p-5 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h3 className="font-semibold text-white text-base">Recent Incident Dossiers</h3>
            <p className="text-xs text-slate-400">
              Latest submissions analyzed and indexed in the graph
            </p>
          </div>
          <button
            onClick={() => navigate('/history')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
          >
            <span>View All Records</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-navy-800 text-slate-400 font-mono text-[11px] uppercase tracking-wider">
              <tr>
                <th className="pb-3 px-3">Report ID</th>
                <th className="pb-3 px-3">Target Company</th>
                <th className="pb-3 px-3">Recruiter</th>
                <th className="pb-3 px-3">Category</th>
                <th className="pb-3 px-3">Risk Assessment</th>
                <th className="pb-3 px-3">Date</th>
                <th className="pb-3 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-800/60">
              {recentReports.map((r) => (
                <tr key={r.id} className="hover:bg-navy-850/50 transition">
                  <td className="py-3 px-3 font-mono text-cyan-400 font-medium">#{r.id}</td>
                  <td className="py-3 px-3 font-medium text-slate-200">
                    <div className="flex items-center gap-1.5">
                      <Building className="w-3.5 h-3.5 text-slate-400" />
                      <span>{r.company_name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-3 text-slate-300">{r.recruiter_name}</td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded-full bg-navy-800 text-slate-300 border border-navy-700 text-[11px]">
                      {r.report_type}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <RiskBadge score={r.risk_score} category={r.risk_category} size="sm" />
                  </td>
                  <td className="py-3 px-3 text-slate-400 font-mono text-[11px]">{r.created_at}</td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => navigate(`/network?report=${r.id}`)}
                      className="px-2.5 py-1 rounded-lg bg-navy-800 hover:bg-navy-700 text-cyan-300 font-medium text-[11px] border border-navy-700 transition"
                    >
                      Inspect Graph
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
