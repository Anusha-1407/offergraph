import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Flag,
  ShieldAlert,
  Building,
  User,
  Phone,
  Mail,
  Globe,
  CreditCard,
  FileText,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Share2,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';

export default function ReportIncident() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    company_name: '',
    recruiter_name: '',
    recruiter_email: '',
    phone_number: '',
    website: '',
    upi_id: '',
    job_role: '',
    report_type: 'Registration fee scam',
    description: '',
    evidence_text: '',
  });

  const [reviewMode, setReviewMode] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [submissionResult, setSubmissionResult] = useState(null);

  const categories = [
    'Registration fee scam',
    'Fake internship',
    'Fake job offer',
    'Impersonation',
    'Data theft attempt',
    'Training fee scam',
    'Other',
  ];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePreFillSynthetic = () => {
    setFormData({
      company_name: 'Apex Technologies',
      recruiter_name: 'Kunal Singhania',
      recruiter_email: 'kunal.apexcareers@gmail.com',
      phone_number: '+91 9876543210',
      website: 'https://apextech-careers.site',
      upi_id: 'apexpay@okhdfcbank',
      job_role: 'Cloud Security Intern',
      report_type: 'Registration fee scam',
      description: '[SYNTHETIC DEMO INCIDENT] Recruiter offered direct internship selection without assessment. Demanded ₹1,200 server provision fee via UPI to apexpay@okhdfcbank. Threatened to cancel offer in 12 hours.',
      evidence_text: 'Telegram chat transcripts and payment demand screenshots.',
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.description.trim()) {
      setError('Please provide a description of the suspicious incident.');
      return;
    }
    setError(null);
    setReviewMode(true);
  };

  const handleConfirmSubmit = async () => {
    try {
      setSubmitting(true);
      setError(null);
      const res = await api.submitReport(formData);
      setSubmissionResult(res);
      setReviewMode(false);
    } catch (err) {
      setError(err.message || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Flag className="w-6 h-6 text-rose-400" />
            Report a Suspicious Incident
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Log recruitment fraud identifiers into the OfferGraph shared intelligence repository to alert the community.
          </p>
        </div>

        {!submissionResult && (
          <button
            type="button"
            onClick={handlePreFillSynthetic}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/25 text-xs font-medium transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Fill Demo Incident Data</span>
          </button>
        )}
      </div>

      {submissionResult ? (
        /* Confirmation Screen */
        <div className="p-8 rounded-2xl bg-navy-900 border border-emerald-500/40 shadow-2xl text-center space-y-5 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 mx-auto flex items-center justify-center">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-emerald-400 font-semibold">
              Submission Logged Successfully
            </span>
            <h3 className="text-2xl font-bold text-white mt-1">
              Dossier Registered: Report #{submissionResult.report_id}
            </h3>
            <p className="text-xs text-slate-400 mt-1 max-w-lg mx-auto leading-relaxed">
              Extracted entities have been normalized and indexed in the graph. Status is currently marked as{' '}
              <strong className="text-amber-300 font-medium">{submissionResult.verification_status}</strong>.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
            <button
              onClick={() => navigate(`/network?report=${submissionResult.report_id}`)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-xs shadow-lg transition"
            >
              <Share2 className="w-4 h-4" />
              <span>Inspect Connected Graph</span>
            </button>
            <button
              onClick={() => {
                setSubmissionResult(null);
                setFormData({
                  company_name: '',
                  recruiter_name: '',
                  recruiter_email: '',
                  phone_number: '',
                  website: '',
                  upi_id: '',
                  job_role: '',
                  report_type: 'Registration fee scam',
                  description: '',
                  evidence_text: '',
                });
              }}
              className="px-5 py-2.5 rounded-xl bg-navy-800 hover:bg-navy-700 text-slate-300 font-medium text-xs border border-navy-700 transition"
            >
              Submit Another Report
            </button>
          </div>
        </div>
      ) : reviewMode ? (
        /* Review Confirmation Screen */
        <div className="p-6 rounded-2xl bg-navy-900 border border-navy-800 shadow-2xl space-y-5 animate-fade-in">
          <div>
            <h3 className="text-lg font-bold text-white">Review Before Indexing</h3>
            <p className="text-xs text-slate-400">
              Please confirm the extracted details below. All submitted identifiers will be correlated against the live database.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Target Company</span>
              <span className="font-semibold text-slate-200">{formData.company_name || 'N/A'}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Recruiter Name</span>
              <span className="font-semibold text-slate-200">{formData.recruiter_name || 'N/A'}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Phone Number</span>
              <span className="font-mono text-amber-300 font-semibold">{formData.phone_number || 'N/A'}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Recruiter Email</span>
              <span className="font-mono text-emerald-300 font-semibold">{formData.recruiter_email || 'N/A'}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block font-mono text-[10px] uppercase">UPI ID</span>
              <span className="font-mono text-rose-300 font-semibold">{formData.upi_id || 'N/A'}</span>
            </div>
            <div className="p-3 rounded-xl bg-navy-950 border border-navy-800">
              <span className="text-slate-400 block font-mono text-[10px] uppercase">Domain / Website</span>
              <span className="font-mono text-pink-300 font-semibold">{formData.website || 'N/A'}</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 text-xs space-y-1">
            <span className="text-slate-400 block font-mono text-[10px] uppercase">Incident Narrative</span>
            <p className="text-slate-300 leading-relaxed text-[11px]">{formData.description}</p>
          </div>

          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>
              <strong>Ethical Notice:</strong> Submitted reports are marked as <em>Unverified Submissions</em> until multiple victims independently correlate the same phone or payment identifiers. Do not submit uncorroborated private disputes.
            </span>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setReviewMode(false)}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 transition"
            >
              Back & Edit
            </button>
            <button
              type="button"
              onClick={handleConfirmSubmit}
              disabled={submitting}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs shadow-lg transition"
            >
              <span>{submitting ? 'Registering...' : 'Confirm & Index in Graph'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        /* Primary Submission Form */
        <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-navy-900 border border-navy-800 shadow-xl space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5 mb-1.5">
                <Building className="w-3.5 h-3.5 text-sky-400" />
                <span>Company Name Claimed</span>
              </label>
              <input
                type="text"
                name="company_name"
                placeholder="e.g. Apex Technologies"
                value={formData.company_name}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5 mb-1.5">
                <User className="w-3.5 h-3.5 text-purple-400" />
                <span>Recruiter Name</span>
              </label>
              <input
                type="text"
                name="recruiter_name"
                placeholder="e.g. Vikram Malhotra"
                value={formData.recruiter_name}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5 mb-1.5">
                <Phone className="w-3.5 h-3.5 text-amber-400" />
                <span>Recruiter Phone / WhatsApp</span>
              </label>
              <input
                type="text"
                name="phone_number"
                placeholder="e.g. +91 98765 43210"
                value={formData.phone_number}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5 mb-1.5">
                <Mail className="w-3.5 h-3.5 text-emerald-400" />
                <span>Recruiter Email</span>
              </label>
              <input
                type="email"
                name="recruiter_email"
                placeholder="e.g. recruiter.apexjobs@gmail.com"
                value={formData.recruiter_email}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5 mb-1.5">
                <CreditCard className="w-3.5 h-3.5 text-rose-400" />
                <span>Demanded UPI ID</span>
              </label>
              <input
                type="text"
                name="upi_id"
                placeholder="e.g. apexpay@okhdfcbank"
                value={formData.upi_id}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5 mb-1.5">
                <Globe className="w-3.5 h-3.5 text-pink-400" />
                <span>Website / Domain</span>
              </label>
              <input
                type="text"
                name="website"
                placeholder="e.g. apextech-careers.site"
                value={formData.website}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 mb-1.5 block">Job Role</label>
              <input
                type="text"
                name="job_role"
                placeholder="e.g. Software Development Intern"
                value={formData.job_role}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 mb-1.5 block">Scam Classification</label>
              <select
                name="report_type"
                value={formData.report_type}
                onChange={handleChange}
                className="w-full p-2.5 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 mb-1.5 block">
              Incident Description & Warning Signs *
            </label>
            <textarea
              name="description"
              rows={4}
              placeholder="Detail what happened: how the recruiter contacted you, what payment or documents were requested, and what deadlines were given..."
              value={formData.description}
              onChange={handleChange}
              required
              className="w-full p-3 rounded-xl bg-navy-950 border border-navy-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end pt-2">
            <button
              type="submit"
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-xs shadow-lg shadow-cyan-500/20 transition"
            >
              <span>Review Incident Report</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
