import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Bot,
  User,
  Send,
  Sparkles,
  Trash2,
  Copy,
  Check,
  ShieldAlert,
  Share2,
  Terminal,
  ExternalLink,
  HelpCircle,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export default function AiAssistant() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialQuery = searchParams.get('q');
  const offerContextParam = searchParams.get('offer_context');

  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      message: `### Welcome to OfferGraph AI Investigator 👋\n\nI am your dedicated cyber fraud intelligence analyst. I query our **live entity graph and incident database** in real-time to uncover recruitment scam syndicates, analyze suspicious offers, and trace coordinated identifiers.\n\n**Select a query below or ask any question:**`,
      tool_calls_executed: [],
      evidence_references: [],
      suggested_actions: [
        'Has +91 9876543210 appeared in previous reports?',
        'Are there other reports connected to apexpay@okhdfcbank?',
        'Show reports connected to Apex Technologies',
        'Should I pay a ₹999 recruitment registration fee?',
        'What should I do if I already transferred money to a recruiter?'
      ],
      ai_mode: 'system'
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 11));
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Handle incoming query or offer context on load
  useEffect(() => {
    if (initialQuery) {
      sendMessage(initialQuery);
    } else if (offerContextParam) {
      try {
        const ctx = JSON.parse(decodeURIComponent(offerContextParam));
        const prompt = `Please review this analysed offer from ${ctx.company} (Risk Score: ${Math.round(ctx.risk_score)}/100, ${ctx.risk_category}). Warning flags detected: ${ctx.indicators.join(', ')}. What evidence connects this to known fraud patterns in OfferGraph?`;
        sendMessage(prompt, ctx);
      } catch (e) {
        console.error('Failed to parse offer context', e);
      }
    }
  }, [initialQuery, offerContextParam]);

  const sendMessage = async (textToSend, context = null) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg = {
      id: 'usr_' + Date.now(),
      role: 'user',
      message: text
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.sendChatMessage(text, sessionId, context);
      const assistantMsg = {
        id: 'ast_' + Date.now(),
        role: 'assistant',
        message: res.message,
        ai_mode: res.ai_mode,
        tool_calls_executed: res.tool_calls_executed || [],
        evidence_references: res.evidence_references || [],
        suggested_actions: res.suggested_actions || []
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: 'err_' + Date.now(),
          role: 'assistant',
          message: `⚠️ Investigation query failed: ${err.message}. Please verify the backend connection.`,
          tool_calls_executed: [],
          evidence_references: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClear = () => {
    setMessages([
      {
        id: 'welcome-cleared',
        role: 'assistant',
        message: 'Investigation session cleared. How can I assist your fraud inquiry today?',
        tool_calls_executed: [],
        evidence_references: [],
        suggested_actions: [
          'Has +91 9876543210 appeared in previous reports?',
          'Are there other reports connected to apexpay@okhdfcbank?',
          'Show reports connected to Apex Technologies'
        ],
        ai_mode: 'system'
      }
    ]);
  };

  return (
    <div className="max-w-5xl mx-auto flex flex-col h-[calc(100vh-5.5rem)] pb-4 space-y-4">
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-2 border-b border-navy-800">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-purple-400" />
            OfferGraph AI Investigator
          </h2>
          <p className="text-xs text-slate-400">
            Conversational intelligence agent querying the OfferGraph graph repository with tool execution.
          </p>
        </div>

        <button
          onClick={handleClear}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-navy-800 hover:bg-navy-750 text-slate-400 hover:text-slate-200 text-xs font-medium border border-navy-700 transition"
          title="Reset conversation"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((m) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={m.id}
              className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center flex-shrink-0 mt-1 shadow">
                  <Bot className="w-4 h-4 text-purple-300" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-4 text-xs space-y-3 ${
                  isUser
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md'
                    : 'bg-navy-900 border border-navy-800 text-slate-200 shadow-xl'
                }`}
              >
                {/* Tool Executions Badge */}
                {m.tool_calls_executed && m.tool_calls_executed.length > 0 && (
                  <div className="p-2 rounded-lg bg-navy-950 border border-navy-800 space-y-1 font-mono text-[11px] text-cyan-300">
                    <div className="flex items-center gap-1.5 text-slate-400 text-[10px] uppercase font-bold">
                      <Terminal className="w-3 h-3 text-cyan-400" />
                      <span>Executed Graph Database Tools</span>
                    </div>
                    {m.tool_calls_executed.map((tc, idx) => (
                      <div key={idx} className="truncate">
                        • {tc}
                      </div>
                    ))}
                  </div>
                )}

                {/* Main Message Content */}
                <div className="whitespace-pre-line leading-relaxed">
                  {m.message}
                </div>

                {/* Evidence References */}
                {m.evidence_references && m.evidence_references.length > 0 && (
                  <div className="pt-2 border-t border-navy-800 space-y-1.5">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block">
                      Supporting Graph Citations:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.evidence_references.map((ev, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 font-mono text-[10px]"
                        >
                          {ev.id} ({ev.company})
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggested Action Chips */}
                {m.suggested_actions && m.suggested_actions.length > 0 && (
                  <div className="pt-2 border-t border-navy-800 space-y-1.5">
                    <span className="text-[10px] font-mono text-slate-400 block">Suggested Inquiries:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.suggested_actions.map((act, idx) => (
                        <button
                          key={idx}
                          onClick={() => sendMessage(act)}
                          className="text-left px-2.5 py-1 rounded-lg bg-navy-950 hover:bg-navy-800 border border-navy-700/80 text-cyan-300 hover:text-white transition text-[11px]"
                        >
                          {act}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Footer / Copy */}
                {!isUser && (
                  <div className="flex items-center justify-between pt-1 text-[10px] text-slate-500 font-mono">
                    <span>
                      {m.ai_mode === 'live' ? 'Live OpenAI Integration' : 'Forensic Investigator Engine'}
                    </span>
                    <button
                      onClick={() => handleCopy(m.message, m.id)}
                      className="hover:text-slate-300 transition flex items-center gap-1"
                    >
                      {copiedId === m.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-xl bg-cyan-600/30 border border-cyan-500/40 flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-cyan-300" />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex gap-3 justify-start items-center">
            <div className="w-8 h-8 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-purple-300" />
            </div>
            <div className="p-3 rounded-2xl bg-navy-900 border border-navy-800 flex items-center gap-2 text-xs text-slate-400">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" />
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]" />
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]" />
              </div>
              <span className="font-mono text-[11px]">Correlating entities in graph...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}
        className="relative flex items-center gap-2 pt-2"
      >
        <input
          type="text"
          placeholder="Ask AI Investigator about recruiters, phone numbers, UPI IDs, or safety rules..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          className="flex-1 p-3.5 pl-4 pr-12 rounded-xl bg-navy-900 border border-navy-800 text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-400 shadow-xl transition"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 mt-1 p-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-30 transition shadow"
          title="Send message"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
