import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Share2,
  AlertTriangle,
  Layers,
  Building,
  User,
  Phone,
  Mail,
  CreditCard,
  Globe,
  FileText,
  Calendar,
  ExternalLink,
  Bot,
  Info,
  Maximize2,
  RefreshCw,
  X
} from 'lucide-react';
import { api } from '../services/api';
import NetworkGraph from '../components/NetworkGraph';
import RiskBadge from '../components/RiskBadge';

export default function FraudNetwork() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const filterReportId = searchParams.get('report');

  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [graphStats, setGraphStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedNode, setSelectedNode] = useState(null);
  const [investigationData, setInvestigationData] = useState(null);
  const [investigating, setInvestigating] = useState(false);

  useEffect(() => {
    async function fetchGraph() {
      try {
        setLoading(true);
        const res = await api.getGraph(filterReportId);
        setGraphData(res.elements || { nodes: [], edges: [] });
        setGraphStats(res.stats);
      } catch (err) {
        setError(err.message || 'Failed to fetch graph data');
      } finally {
        setLoading(false);
      }
    }
    fetchGraph();
  }, [filterReportId]);

  // When a node is selected, fetch deep entity or report details
  const handleNodeSelect = async (nodeData) => {
    setSelectedNode(nodeData);
    if (!nodeData) {
      setInvestigationData(null);
      return;
    }

    try {
      setInvestigating(true);
      if (nodeData.type === 'report') {
        const rep = await api.getReportDetail(nodeData.db_id);
        setInvestigationData({
          isReport: true,
          ...rep,
        });
      } else {
        const ent = await api.getEntityConnections(nodeData.db_id);
        setInvestigationData({
          isReport: false,
          ...ent,
        });
      }
    } catch (err) {
      console.error('Error fetching node details:', err);
    } finally {
      setInvestigating(false);
    }
  };

  const handleAskAssistant = () => {
    if (!selectedNode) return;
    const query = selectedNode.type === 'report'
      ? `Investigate Report #${selectedNode.db_id}`
      : `Are there other reports connected to ${selectedNode.display_value || selectedNode.label}?`;
    navigate(`/assistant?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto pb-8 flex flex-col h-[calc(100vh-5.5rem)]">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Share2 className="w-6 h-6 text-cyan-400" />
            Fraud Intelligence Network Graph
          </h2>
          <p className="text-xs text-slate-400">
            Interactive visualization linking suspicious incidents through shared phones, emails, UPI IDs, and domains.
          </p>
        </div>

        {filterReportId && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            <span>Filtered to Report #{filterReportId} Cluster</span>
            <button
              onClick={() => navigate('/network')}
              className="p-0.5 hover:text-white transition"
              title="Clear Filter"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Main Layout: Graph on Left, Side Panel on Right */}
      <div className="flex-1 flex flex-col lg:flex-row gap-4 min-h-0">
        {/* Left: Cytoscape Canvas */}
        <div className="flex-1 flex flex-col min-h-[420px] rounded-2xl overflow-hidden border border-navy-800 bg-navy-950 shadow-2xl relative">
          {loading ? (
            <div className="flex flex-col items-center justify-center flex-1 gap-2">
              <div className="w-8 h-8 border-3 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
              <p className="text-xs text-slate-400 font-mono">Loading Graph Topology...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center flex-1 p-6 text-rose-400">
              <AlertTriangle className="w-8 h-8 mb-2" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          ) : (
            <NetworkGraph
              elements={graphData}
              onNodeSelect={handleNodeSelect}
              selectedNodeId={filterReportId ? `report_${filterReportId}` : undefined}
              height="100%"
            />
          )}
        </div>

        {/* Right: Forensic Investigation Dossier Panel */}
        <div className="w-full lg:w-96 flex flex-col rounded-2xl border border-navy-800 bg-navy-900/95 backdrop-blur shadow-2xl overflow-hidden">
          <div className="p-4 border-b border-navy-800 flex items-center justify-between">
            <h3 className="font-semibold text-white text-sm flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>Entity Dossier Panel</span>
            </h3>
            {selectedNode && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-navy-800 text-slate-300 border border-navy-700 capitalize">
                {selectedNode.type}
              </span>
            )}
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {!selectedNode ? (
              <div className="flex flex-col items-center justify-center h-full text-center p-6 space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-navy-800/80 border border-navy-700 flex items-center justify-center text-slate-400">
                  <Share2 className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-slate-200">No Entity Selected</h4>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    Click any node in the graph (diamond reports or circle identifiers) to inspect shared connections and syndicate links.
                  </p>
                </div>
              </div>
            ) : investigating ? (
              <div className="flex flex-col items-center justify-center py-12 gap-2 text-xs text-slate-400">
                <RefreshCw className="w-5 h-5 text-cyan-400 animate-spin" />
                <span>Querying Entity Linkages...</span>
              </div>
            ) : investigationData ? (
              <div className="space-y-4 text-xs">
                {/* Node Identity Card */}
                <div className="p-3.5 rounded-xl bg-navy-950 border border-navy-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
                      {investigationData.isReport ? 'Incident Report' : 'Correlated Identifier'}
                    </span>
                    {investigationData.isReport && (
                      <RiskBadge
                        score={investigationData.risk_score}
                        category={investigationData.risk_category}
                        size="sm"
                      />
                    )}
                  </div>
                  <h4 className="font-bold text-white text-base break-words">
                    {investigationData.isReport
                      ? `Report #${investigationData.id}: ${investigationData.company_name}`
                      : investigationData.masked_identifier}
                  </h4>
                </div>

                {/* Report Specific Details */}
                {investigationData.isReport ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded-lg bg-navy-950/70 border border-navy-800/80">
                        <span className="text-slate-400 text-[10px] uppercase font-mono">Recruiter</span>
                        <p className="text-slate-200 font-medium truncate">{investigationData.recruiter_name}</p>
                      </div>
                      <div className="p-2.5 rounded-lg bg-navy-950/70 border border-navy-800/80">
                        <span className="text-slate-400 text-[10px] uppercase font-mono">Job Role</span>
                        <p className="text-slate-200 font-medium truncate">{investigationData.job_role}</p>
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-navy-950/70 border border-navy-800/80 space-y-1">
                      <span className="text-slate-400 text-[10px] uppercase font-mono">Incident Allegation</span>
                      <p className="text-slate-300 leading-relaxed text-[11px]">{investigationData.description}</p>
                    </div>

                    {/* Connected entities to this report */}
                    <div className="space-y-1.5">
                      <span className="text-slate-400 text-[11px] font-semibold">Attached Graph Entities:</span>
                      <div className="space-y-1">
                        {investigationData.connected_entities?.map((ce, i) => (
                          <div key={i} className="flex items-center justify-between p-2 rounded bg-navy-950 border border-navy-800 text-[11px]">
                            <span className="text-slate-400 capitalize">{ce.entity_type}:</span>
                            <span className="font-mono text-cyan-300">{ce.display_value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  /* Entity Specific Details (Phone, Email, UPI, Domain) */
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded-lg bg-navy-950/70 border border-navy-800/80">
                        <span className="text-slate-400 text-[10px] uppercase font-mono">Linked Reports</span>
                        <p className="text-cyan-400 font-bold font-mono text-base">
                          {investigationData.linked_reports_count}
                        </p>
                      </div>
                      <div className="p-2.5 rounded-lg bg-navy-950/70 border border-navy-800/80">
                        <span className="text-slate-400 text-[10px] uppercase font-mono">Associated Fronts</span>
                        <p className="text-purple-400 font-bold font-mono text-base">
                          {investigationData.connected_companies?.length || 0}
                        </p>
                      </div>
                    </div>

                    {investigationData.connected_companies?.length > 0 && (
                      <div className="p-2.5 rounded-lg bg-navy-950 border border-navy-800">
                        <span className="text-slate-400 text-[10px] uppercase font-mono">Mentioned Companies</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {investigationData.connected_companies.map((c, i) => (
                            <span key={i} className="px-2 py-0.5 rounded bg-sky-500/15 text-sky-300 border border-sky-500/30 text-[11px]">
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Supporting Incident Reports List */}
                    <div className="space-y-1.5">
                      <span className="text-slate-400 text-[11px] font-semibold">Corroborating Reports:</span>
                      <div className="space-y-1.5">
                        {investigationData.supporting_reports?.map((sr) => (
                          <div
                            key={sr.report_id}
                            className="p-2.5 rounded-xl bg-navy-950 border border-navy-800 hover:border-cyan-500/40 transition cursor-pointer"
                            onClick={() => navigate(`/network?report=${sr.report_id}`)}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-mono text-cyan-400 font-semibold">Report #{sr.report_id}</span>
                              <RiskBadge score={sr.risk_score} category={sr.risk_category} size="sm" />
                            </div>
                            <p className="text-slate-300 mt-1 font-medium">{sr.company_name}</p>
                            <span className="text-[10px] text-slate-500 font-mono">{sr.created_at}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </div>

          {/* Bottom Action Footer */}
          {selectedNode && (
            <div className="p-3 border-t border-navy-800 bg-navy-950/80">
              <button
                onClick={handleAskAssistant}
                className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-xs shadow-lg shadow-purple-500/20 transition"
              >
                <Bot className="w-4 h-4" />
                <span>Investigate in AI Assistant</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
