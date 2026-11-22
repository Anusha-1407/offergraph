import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  Share2,
  Bot,
  Flag,
  History,
  ShieldCheck,
  Menu,
  X,
  RefreshCw,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Database
} from 'lucide-react';
import { api } from '../services/api';

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/check-offer', label: 'Check an Offer', icon: Search, badge: 'Core' },
    { path: '/network', label: 'Fraud Network', icon: Share2, badge: 'Graph' },
    { path: '/assistant', label: 'AI Assistant', icon: Bot, badge: 'Agent' },
    { path: '/report', label: 'Report Incident', icon: Flag },
    { path: '/history', label: 'Investigation History', icon: History },
    { path: '/safety', label: 'Safety Centre', icon: ShieldCheck },
  ];

  const handleResetDemoData = async () => {
    try {
      setResetting(true);
      await api.resetDemoData();
      setToastMessage('Demonstration database reset successfully!');
      setTimeout(() => {
        window.location.reload();
      }, 800);
    } catch (err) {
      setToastMessage('Error resetting database: ' + err.message);
    } finally {
      setResetting(false);
      setTimeout(() => setToastMessage(null), 3500);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-navy-950 text-slate-100">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-5 right-5 z-50 flex items-center gap-3 bg-navy-800 border border-cyber-cyan/40 px-4 py-3 rounded-lg shadow-2xl backdrop-blur text-sm text-cyan-200 animate-fade-in">
          <Sparkles className="w-4 h-4 text-cyber-cyan animate-spin" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Sidebar */}
      <aside
        className={`flex flex-col border-r border-navy-800 bg-navy-900/90 backdrop-blur transition-all duration-300 z-30 ${
          collapsed ? 'w-20' : 'w-64'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between p-4 border-b border-navy-800/80">
          {!collapsed ? (
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-purple-600 shadow-lg shadow-cyan-500/20">
                <Share2 className="w-5 h-5 text-white" />
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-navy-900" />
              </div>
              <div>
                <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                  OfferGraph
                </h1>
                <p className="text-[10px] text-slate-400 font-mono tracking-wider uppercase">
                  Fraud Intelligence
                </p>
              </div>
            </div>
          ) : (
            <div className="mx-auto">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-purple-600 flex items-center justify-center">
                <Share2 className="w-5 h-5 text-white" />
              </div>
            </div>
          )}

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-navy-800 transition"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/15 to-indigo-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800/60'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <Icon
                  className={`w-5 h-5 flex-shrink-0 transition-colors ${
                    isActive ? 'text-cyber-cyan' : 'text-slate-400 group-hover:text-slate-200'
                  }`}
                />
                {!collapsed && (
                  <div className="flex items-center justify-between w-full">
                    <span>{item.label}</span>
                    {item.badge && (
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-navy-800 text-slate-400 border border-navy-700">
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Demo Mode & Quick Reset Controls */}
        <div className="p-3 border-t border-navy-800/80 bg-navy-950/40">
          {!collapsed ? (
            <div className="rounded-xl border border-navy-800 bg-navy-900/60 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  Network Live
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Demo Active
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                Seeded with coordinated syndicate clusters for live demo.
              </p>
              <button
                onClick={handleResetDemoData}
                disabled={resetting}
                className="w-full flex items-center justify-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-navy-800 hover:bg-navy-700 text-slate-200 border border-navy-700 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${resetting ? 'animate-spin text-cyan-400' : ''}`} />
                {resetting ? 'Resetting...' : 'Reset Demo Data'}
              </button>
            </div>
          ) : (
            <button
              onClick={handleResetDemoData}
              disabled={resetting}
              className="w-full p-2.5 rounded-lg bg-navy-800 text-slate-300 hover:text-white flex justify-center"
              title="Reset Demo Data"
            >
              <RefreshCw className={`w-4 h-4 ${resetting ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          )}

          {/* User profile footer */}
          <div className="mt-3 flex items-center gap-3 pt-2">
            <div className="w-8 h-8 rounded-full bg-navy-800 border border-navy-700 flex items-center justify-center text-xs font-bold text-cyan-400">
              AG
            </div>
            {!collapsed && (
              <div className="text-left overflow-hidden">
                <p className="text-xs font-medium text-slate-200 truncate">Investigator Desk</p>
                <p className="text-[10px] text-slate-400 font-mono truncate">analyst@offergraph</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header */}
        <header className="h-14 border-b border-navy-800/80 bg-navy-900/60 backdrop-blur px-6 flex items-center justify-between z-20">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <span className="text-slate-500">OfferGraph</span>
              <span>/</span>
              <span className="text-cyan-400 font-medium">
                {navItems.find((n) => n.path === location.pathname)?.label || 'Intelligence'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-navy-800/80 border border-navy-700/80 text-xs text-slate-300">
              <Database className="w-3.5 h-3.5 text-cyber-cyan" />
              <span>Shared Graph Intelligence</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            </div>

            <a
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 text-xs text-rose-300 hover:text-rose-200 bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 rounded-lg transition"
            >
              <span>Cyber Helpline 1930</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </header>

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto bg-navy-950 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
