import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  PhoneCall,
  ExternalLink,
  Lock,
  FileCheck,
  CreditCard,
  Building,
  Info,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { api } from '../services/api';

export default function SafetyCentre() {
  const [resources, setResources] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedGuide, setExpandedGuide] = useState('spot_fake_internship');

  useEffect(() => {
    async function fetchSafetyData() {
      try {
        const data = await api.getSafetyResources();
        setResources(data);
      } catch (err) {
        console.error('Failed to load safety resources', err);
      } finally {
        setLoading(false);
      }
    }
    fetchSafetyData();
  }, []);

  const toggleGuide = (id) => {
    setExpandedGuide(expandedGuide === id ? null : id);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          Safety Centre & Incident Response
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Authoritative verification checklists, statutory protections, and emergency steps for victims of recruitment fraud.
        </p>
      </div>

      {/* Emergency Incident Banner (National Helpline 1930 & Portal) */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-rose-950/70 via-navy-900 to-navy-900 border border-rose-500/40 shadow-2xl relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-300 font-mono text-[11px] border border-rose-500/30">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
              <span>India National Cybercrime Helpline</span>
            </div>
            <h3 className="text-2xl font-bold text-white flex items-center gap-3">
              <span>Dial</span>
              <a
                href="tel:1930"
                className="font-mono text-3xl font-extrabold text-rose-400 hover:text-rose-300 transition"
              >
                1930
              </a>
              <span className="text-sm font-normal text-slate-300">(Toll-Free, 24x7)</span>
            </h3>
            <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
              If you transferred money via UPI, NetBanking, or card to a suspicious recruiter within the last few hours, dial <strong>1930</strong> immediately. The Citizen Financial Cyber Fraud Reporting System can freeze recipient accounts in the 'Golden Hour'.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row md:flex-col gap-2.5 flex-shrink-0">
            <a
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-lg shadow-rose-600/30 transition"
            >
              <span>National Cyber Crime Portal</span>
              <ExternalLink className="w-4 h-4" />
            </a>
            <span className="text-[10px] text-center text-slate-400 font-mono">
              Official portal: cybercrime.gov.in
            </span>
          </div>
        </div>
      </div>

      {/* Legal & Platform Disclaimer */}
      <div className="p-4 rounded-xl bg-navy-900 border border-navy-800 text-xs text-slate-400 flex items-start gap-3">
        <Info className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong>Notice & Disclaimer:</strong> OfferGraph is an academic and investigative intelligence platform built for hackathon demonstration. It correlates reported fraud patterns and public identifiers to aid candidate awareness. OfferGraph is not a law-enforcement authority or statutory judicial body.
        </p>
      </div>

      {/* Safety Guides Accordion / Cards */}
      <div className="space-y-3">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <span>Forensic Verification Guides</span>
        </h3>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading resources...</div>
        ) : (
          (resources?.guides || []).map((guide) => {
            const isExpanded = expandedGuide === guide.id;
            return (
              <div
                key={guide.id}
                className="rounded-2xl border border-navy-800 bg-navy-900 overflow-hidden shadow-lg transition"
              >
                <button
                  onClick={() => toggleGuide(guide.id)}
                  className="w-full p-4 text-left flex items-center justify-between hover:bg-navy-850/50 transition"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-navy-950 text-cyan-400 border border-navy-800 uppercase">
                        {guide.category}
                      </span>
                      <h4 className="font-semibold text-white text-sm">{guide.title}</h4>
                    </div>
                    <p className="text-xs text-slate-400">{guide.summary}</p>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </button>

                {isExpanded && (
                  <div className="px-5 pb-5 pt-2 border-t border-navy-800/60 bg-navy-950/40 space-y-2.5">
                    <ul className="space-y-2 text-xs text-slate-300">
                      {guide.points.map((pt, idx) => (
                        <li key={idx} className="flex items-start gap-2.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 flex-shrink-0" />
                          <span className="leading-relaxed">{pt}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Indian IT Act & Statutory Framework Card */}
      <div className="p-6 rounded-2xl bg-navy-900 border border-navy-800 shadow-xl space-y-3">
        <h4 className="font-semibold text-white text-base flex items-center gap-2">
          <Lock className="w-4 h-4 text-purple-400" />
          <span>Statutory Protection & Legal Remedies in India</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-300 pt-1">
          <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 space-y-1">
            <span className="font-mono text-cyan-400 font-bold block">IT Act Section 66D</span>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              Punishment for cheating by personation by using computer resource (up to 3 years imprisonment and fine).
            </p>
          </div>

          <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 space-y-1">
            <span className="font-mono text-purple-400 font-bold block">BNS / IPC Section 420</span>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              Cheating and dishonestly inducing delivery of property (covers advance recruitment registration fee theft).
            </p>
          </div>

          <div className="p-3 rounded-xl bg-navy-950 border border-navy-800 space-y-1">
            <span className="font-mono text-emerald-400 font-bold block">Ministry of Labour Guidelines</span>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              Recruitment agents charging fees to candidates without official license violate statutory placement norms.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
