import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  History,
  Search,
  Filter,
  Building,
  Calendar,
  Share2,
  ExternalLink,
  ChevronRight,
  ShieldAlert,
  Layers,
  ArrowUpDown
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export default function InvestigationHistory() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [riskFilter, setRiskFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedReportDetail, setSelectedReportDetail] = useState(null);

  useEffect(() => {
    async function loadReports() {
      try {
        setLoading(true);
        const res = await api.getReports({
          risk_category: riskFilter !== 'All' ? riskFilter : undefined,
          report_type: typeFilter !== 'All' ? typeFilter : undefined,
          q: searchQuery.trim() || undefined,
        });
        setReports(res.reports || []);
      } catch (err) {
        setError(err.message || 'Failed to load report history');
      } finally {
        setLoading(false);
      }
    }
    loadReports();
  }, [riskFilter, typeFilter, searchQuery]);

  const handleOpenDetail = async (id) => {
    try {
      const detail = await api.getReportDetail(id);
      setSelectedReportDetail(detail);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-16">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <History className="w-6 h-6 text-cyan-400" />
          Investigation History & Dossiers
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Comprehensive repository of filed incident reports, correlated threat scores, and shared entity linkages.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-navy-900 border border-navy-800 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5 text-cyan-400" />
            <span>Risk:</span>
          </div>
          {['All', 'High Risk', 'Medium Risk', 'Low Risk'].map((r) => (
            <button
              key={r}
              onClick={() => setRiskFilter(r)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                riskFilter === r
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'bg-navy-950 text-slate-400 hover:text-slate-200 border border-navy-800'
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by company, role, or text..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 pr-3 py-1.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-400 w-full sm:w-64"
          />
        </div>
      </div>

      {/* Table of Reports */}
      <div className="rounded-2xl bg-navy-900 border border-navy-800 shadow-xl overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12 text-slate-400 text-xs gap-2">
            <div className="w-6 h-6 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
            <span>Loading intelligence history...</span>
          </div>
        ) : reports.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs space-y-2">
            <p>No incident reports matched your active filter criteria.</p>
            <button
              onClick={() => {
                setRiskFilter('All');
                setTypeFilter('All');
                setSearchQuery('');
              }}
              className="px-3 py-1.5 rounded-lg bg-navy-800 text-cyan-300 text-xs font-medium"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-navy-950/60 border-b border-navy-800 text-slate-400 font-mono text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Report ID</th>
                  <th className="py-3 px-4">Target Company</th>
                  <th className="py-3 px-4">Recruiter / Contact</th>
                  <th className="py-3 px-4">Classification</th>
                  <th className="py-3 px-4">Risk Evaluation</th>
                  <th className="py-3 px-4">Connected Nodes</th>
                  <th className="py-3 px-4">Date Logged</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-navy-850/50 transition">
                    <td className="py-3.5 px-4 font-mono font-medium text-cyan-400">#{r.id}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-200">
                      <div className="flex items-center gap-1.5">
                        <Building className="w-3.5 h-3.5 text-slate-400" />
                        <span>{r.company_name}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">{r.recruiter_name}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-navy-950 text-slate-300 border border-navy-800 text-[11px]">
                        {r.report_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <RiskBadge score={r.risk_score} category={r.risk_category} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 font-mono text-indigo-300">
                      {r.connected_entities_count} entities
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400 text-[11px]">{r.created_at}</td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <button
                        onClick={() => handleOpenDetail(r.id)}
                        className="px-2.5 py-1 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-200 border border-navy-700 text-[11px] font-medium transition"
                      >
                        Details
                      </button>
                      <button
                        onClick={() => navigate(`/network?report=${r.id}`)}
                        className="px-2.5 py-1 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-[11px] font-medium transition"
                      >
                        Graph
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Modal / Drawer */}
      {selectedReportDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/80 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-2xl rounded-2xl bg-navy-900 border border-navy-800 shadow-2xl p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-navy-800 pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400">
                  Dossier Detail
                </span>
                <h3 className="text-lg font-bold text-white">
                  Report #{selectedReportDetail.id}: {selectedReportDetail.company_name}
                </h3>
              </div>
              <RiskBadge
                score={selectedReportDetail.risk_score}
                category={selectedReportDetail.risk_category}
                size="md"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                <span className="text-slate-400 block font-mono text-[10px] uppercase">Claimed Recruiter</span>
                <span className="font-semibold text-slate-200">{selectedReportDetail.recruiter_name}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                <span className="text-slate-400 block font-mono text-[10px] uppercase">Job Role</span>
                <span className="font-semibold text-slate-200">{selectedReportDetail.job_role}</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 text-xs space-y-1">
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Incident Narrative</span>
              <p className="text-slate-300 leading-relaxed text-[11px]">{selectedReportDetail.description}</p>
            </div>

            {/* Connected entities */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-300 block">Correlated Identifiers in Graph:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {selectedReportDetail.connected_entities?.map((ce, i) => (
                  <div key={i} className="p-2 rounded-lg bg-navy-950 border border-navy-800 flex items-center justify-between">
                    <span className="text-slate-400 capitalize">{ce.entity_type}</span>
                    <span className="font-mono text-cyan-300">{ce.display_value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-navy-800">
              <button
                onClick={() => setSelectedReportDetail(null)}
                className="px-4 py-2 rounded-xl bg-navy-800 hover:bg-navy-700 text-slate-300 text-xs font-medium transition"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const id = selectedReportDetail.id;
                  setSelectedReportDetail(null);
                  navigate(`/network?report=${id}`);
                }}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition shadow"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Open in Network Graph</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
