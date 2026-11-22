import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  UploadCloud,
  FileText,
  Sparkles,
  Trash2,
  AlertTriangle,
  ShieldAlert,
  Building,
  User,
  Phone,
  Mail,
  CreditCard,
  Globe,
  Bot,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  Share2
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export default function CheckOffer() {
  const navigate = useNavigate();
  const [offerText, setOfferText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  const sampleScamOffer = `Subject: Official Selection Letter: Software Development Internship at Apex Technologies

Dear Candidate,

Congratulations! We are delighted to inform you that you have been directly selected for the Software Development Internship at Apex Technologies (Bangalore/Remote) with a monthly stipend of ₹35,000/-.

Due to your impressive profile, no technical interview round was required.

To confirm your acceptance and secure your onboarding kit and cloud server credentials, you are required to pay a mandatory refundable registration and documentation fee of ₹999/- within 24 hours.

Payment Instructions:
Pay ₹999 via UPI to: apexpay@okhdfcbank
(This fee is 100% refundable with your first stipend payout).

Kindly WhatsApp the payment confirmation screenshot immediately to our HR Talent Lead Mr. Vikram Malhotra at +91 9876543210 or reply to recruiter.apexjobs@gmail.com.

Official Careers Portal: https://apextech-careers.site

Failure to complete payment within 24 hours will result in automatic cancellation of your internship slot.

Warm regards,
HR Talent Acquisition Team
Apex Technologies`;

  const handleUseSample = () => {
    setOfferText(sampleScamOffer);
    setFile(null);
    setError(null);
  };

  const handleClear = () => {
    setOfferText('');
    setFile(null);
    setAnalysisResult(null);
    setError(null);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!offerText.trim() && !file) {
      setError('Please paste offer text or upload a PDF/TXT file.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      let payload;
      if (file) {
        payload = new FormData();
        payload.append('file', file);
      } else {
        payload = { text: offerText };
      }

      const res = await api.analyzeOffer(payload);
      setAnalysisResult(res);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAskAssistant = () => {
    if (!analysisResult) return;
    const contextStr = encodeURIComponent(
      JSON.stringify({
        company: analysisResult.company_name,
        risk_score: analysisResult.risk_score,
        risk_category: analysisResult.risk_category,
        indicators: analysisResult.suspicious_indicators.map((i) => i.title),
        sample_excerpt: offerText.slice(0, 300)
      })
    );
    navigate(`/assistant?offer_context=${contextStr}`);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          Check an Offer
        </h2>
        <p className="text-sm text-slate-400 mt-0.5">
          Submit an internship or job offer to extract entities, calculate explainable risk scores, and check against our shared fraud network.
        </p>
      </div>

      {/* Input Card */}
      <div className="p-6 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-xl space-y-4">
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Paste Offer Letter or Message</span>
            </label>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleUseSample}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/25 text-xs font-medium transition"
              >
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                <span>Load Sample Scam Offer</span>
              </button>
              {(offerText || file) && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="p-1 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
                  title="Clear inputs"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          <textarea
            rows={7}
            placeholder="Congratulations! You have been selected for a Software Development Internship at Apex Technologies. Pay ₹999 as a registration fee to confirm your position. Contact us at apexjobs@example.com."
            value={offerText}
            onChange={(e) => {
              setOfferText(e.target.value);
              if (file) setFile(null);
            }}
            className="w-full p-4 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-400 text-sm font-sans transition"
          />

          {/* File Upload Area */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-navy-950/60 border border-dashed border-navy-800">
            <div className="flex items-center gap-3">
              <UploadCloud className="w-5 h-5 text-cyan-400 flex-shrink-0" />
              <div>
                <p className="text-xs font-medium text-slate-300">
                  {file ? file.name : 'Or upload Offer Document (.PDF or .TXT)'}
                </p>
                <p className="text-[11px] text-slate-400">
                  {file ? `${(file.size / 1024).toFixed(1)} KB ready` : 'Supports PyMuPDF text parsing'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="file"
                id="file-upload"
                accept=".pdf,.txt"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                    setOfferText('');
                  }
                }}
                className="hidden"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer px-3 py-1.5 rounded-lg bg-navy-800 hover:bg-navy-700 border border-navy-700 text-slate-300 text-xs font-medium transition"
              >
                Browse File
              </label>
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClear}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 transition"
            >
              Clear
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-sm shadow-lg shadow-cyan-500/25 transition disabled:opacity-50"
            >
              <Search className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Performing Forensic Analysis...' : 'Analyse Offer'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Analysis Results View */}
      {analysisResult && (
        <div className="space-y-6 animate-fade-in">
          {/* Top Risk Score Header Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-b from-navy-900 to-navy-900/90 border border-navy-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-20 h-20 rounded-2xl bg-navy-950 border border-navy-800 shadow-inner">
                <span
                  className={`text-2xl font-bold font-mono ${
                    analysisResult.risk_score >= 60
                      ? 'text-rose-400'
                      : analysisResult.risk_score >= 30
                      ? 'text-amber-400'
                      : 'text-emerald-400'
                  }`}
                >
                  {Math.round(analysisResult.risk_score)}
                </span>
                <span className="text-[10px] text-slate-400 font-mono absolute bottom-1.5">/100</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-bold text-white">Risk Evaluation Summary</h3>
                  <RiskBadge
                    score={analysisResult.risk_score}
                    category={analysisResult.risk_category}
                    size="md"
                    showScore={false}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Target Company:{' '}
                  <strong className="text-slate-200">
                    {analysisResult.company_name || 'Unspecified'}
                  </strong>
                  {' • '}
                  Role:{' '}
                  <span className="text-cyan-300">
                    {analysisResult.extracted_entities.job_role || 'Internship'}
                  </span>
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={handleAskAssistant}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 text-purple-300 font-medium text-xs shadow transition"
              >
                <Bot className="w-4 h-4 text-purple-400" />
                <span>Ask AI Assistant About This Offer</span>
              </button>

              {analysisResult.matched_previous_reports?.length > 0 && (
                <button
                  onClick={() => navigate('/network')}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-cyan-300 font-medium text-xs transition"
                >
                  <Share2 className="w-4 h-4 text-cyan-400" />
                  <span>Inspect in Fraud Network</span>
                </button>
              )}
            </div>
          </div>

          {/* Database Match Alert (The Main Differentiator) */}
          {analysisResult.matched_previous_reports?.length > 0 ? (
            <div className="p-5 rounded-2xl bg-rose-500/10 border border-rose-500/40 shadow-lg space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-rose-400 font-bold text-sm">
                  <ShieldAlert className="w-5 h-5 animate-pulse" />
                  <span>
                    FRAUD NETWORK MATCH: {analysisResult.matched_previous_reports.length} Linked Prior Incident(s)
                  </span>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  High Correlation Alert
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                OfferGraph matched extracted identifiers (phone number, UPI account, or email domain) to previously logged recruitment fraud complaints in our intelligence repository. This communication is linked to an existing syndicate pattern.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                {analysisResult.matched_previous_reports.map((r, i) => (
                  <div key={i} className="p-3 rounded-xl bg-navy-950/80 border border-rose-500/30 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono text-cyan-400 font-semibold">Report #{r.report_id}</span>
                      <span className="text-rose-400 font-mono text-[11px]">Risk: {Math.round(r.risk_score)}/100</span>
                    </div>
                    <p className="text-xs font-medium text-slate-200">{r.company_name} — {r.report_type}</p>
                    <p className="text-[11px] text-slate-400 line-clamp-2">{r.snippet}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-navy-900 border border-navy-800 text-xs text-slate-400 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Zero previous complaints match these exact identifiers in the database. Behavioral scoring applies below.</span>
              </div>
              <span className="text-[11px] font-mono text-slate-500">Unflagged Identifiers</span>
            </div>
          )}

          {/* Grid: Extracted Entities & Suspicious Indicators */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Extracted Structured Entities */}
            <div className="p-5 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-lg space-y-4">
              <div>
                <h4 className="font-semibold text-white text-sm flex items-center justify-between">
                  <span>Extracted Structured Entities</span>
                  <span className="text-xs font-mono text-slate-400">Regex & Heuristics</span>
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Normalized coordinates extracted from the offer letter
                </p>
              </div>

              <div className="space-y-2.5 text-xs">
                <div className="flex items-start justify-between p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <Building className="w-4 h-4 text-sky-400" /> Company:
                  </span>
                  <span className="font-semibold text-slate-200">
                    {analysisResult.extracted_entities.company_name || 'Not detected'}
                  </span>
                </div>

                <div className="flex items-start justify-between p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <User className="w-4 h-4 text-purple-400" /> Recruiter Contact:
                  </span>
                  <span className="font-semibold text-slate-200">
                    {analysisResult.extracted_entities.recruiter_name || 'Not specified'}
                  </span>
                </div>

                <div className="flex items-start justify-between p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <Phone className="w-4 h-4 text-amber-400" /> Phone Numbers:
                  </span>
                  <span className="font-mono text-slate-200">
                    {analysisResult.extracted_entities.phone_numbers?.length > 0
                      ? analysisResult.extracted_entities.phone_numbers.join(', ')
                      : 'None detected'}
                  </span>
                </div>

                <div className="flex items-start justify-between p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <Mail className="w-4 h-4 text-emerald-400" /> Recruiter Email:
                  </span>
                  <span className="font-mono text-slate-200">
                    {analysisResult.extracted_entities.recruiter_emails?.length > 0
                      ? analysisResult.extracted_entities.recruiter_emails.join(', ')
                      : 'None detected'}
                  </span>
                </div>

                <div className="flex items-start justify-between p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <CreditCard className="w-4 h-4 text-rose-400" /> UPI Identifiers:
                  </span>
                  <span className="font-mono text-rose-400 font-semibold">
                    {analysisResult.extracted_entities.upi_ids?.length > 0
                      ? analysisResult.extracted_entities.upi_ids.join(', ')
                      : 'None detected'}
                  </span>
                </div>

                <div className="flex items-start justify-between p-2.5 rounded-xl bg-navy-950 border border-navy-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <Globe className="w-4 h-4 text-pink-400" /> Domains / Websites:
                  </span>
                  <span className="font-mono text-slate-200">
                    {analysisResult.extracted_entities.domains?.length > 0
                      ? analysisResult.extracted_entities.domains.join(', ')
                      : 'None detected'}
                  </span>
                </div>
              </div>
            </div>

            {/* Suspicious Indicators (Explainable Scoring) */}
            <div className="p-5 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-lg space-y-4">
              <div>
                <h4 className="font-semibold text-white text-sm flex items-center justify-between">
                  <span>Suspicious Indicators Detected</span>
                  <span className="text-xs font-mono text-cyan-400">
                    {analysisResult.suspicious_indicators.length} Flags
                  </span>
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Explainable rule contributions adding to the overall risk score
                </p>
              </div>

              <div className="space-y-2.5 max-h-[310px] overflow-y-auto pr-1">
                {analysisResult.suspicious_indicators.length === 0 ? (
                  <p className="text-xs text-slate-400 p-4 text-center">
                    No critical suspicious indicators triggered.
                  </p>
                ) : (
                  analysisResult.suspicious_indicators.map((ind, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-navy-950 border border-navy-800 space-y-1"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-rose-300 flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                          <span>{ind.title}</span>
                        </span>
                        <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 font-mono font-bold text-[11px]">
                          +{ind.points} pts
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-tight">{ind.description}</p>
                      {ind.evidence_snippet && (
                        <p className="text-[10px] font-mono text-slate-500 bg-navy-900 px-2 py-1 rounded border border-navy-800 mt-1">
                          "{ind.evidence_snippet}"
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* AI Forensic Explanation Card */}
          <div className="p-6 rounded-2xl bg-navy-900/90 border border-navy-800 shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-navy-800 pb-3">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-purple-400" />
                <h4 className="font-semibold text-white text-base">Forensic AI Analysis</h4>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/30">
                Mode: {analysisResult.ai_mode === 'live' ? 'OpenAI GPT Live' : 'Deterministic Demo Mode'}
              </span>
            </div>

            <div className="prose prose-invert prose-sm max-w-none text-slate-300 text-xs leading-relaxed space-y-2 whitespace-pre-line">
              {analysisResult.ai_explanation}
            </div>
          </div>

          {/* Recommended Verification Steps */}
          <div className="p-5 rounded-2xl bg-navy-900/80 border border-navy-800 space-y-3">
            <h4 className="font-semibold text-white text-sm flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Recommended Verification Protocol</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300">
              {analysisResult.recommended_verification_steps.map((step, idx) => (
                <div key={idx} className="flex items-start gap-2 p-2 rounded-lg bg-navy-950/60 border border-navy-800/80">
                  <span className="text-cyan-400 font-mono font-bold">{idx + 1}.</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
