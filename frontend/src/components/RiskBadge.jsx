import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function RiskBadge({ score, category, size = 'md', showScore = true }) {
  const numScore = Math.round(Number(score) || 0);

  let colorClasses = {
    bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    dot: 'bg-emerald-400',
    icon: ShieldCheck,
  };

  if (category === 'High Risk' || numScore >= 60) {
    colorClasses = {
      bg: 'bg-rose-500/10 border-rose-500/40 text-rose-400 shadow-[0_0_12px_rgba(244,63,94,0.2)]',
      dot: 'bg-rose-500 animate-pulse',
      icon: ShieldAlert,
    };
  } else if (category === 'Medium Risk' || numScore >= 30) {
    colorClasses = {
      bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      dot: 'bg-amber-400',
      icon: AlertTriangle,
    };
  }

  const Icon = colorClasses.icon;
  const isSm = size === 'sm';
  const isLg = size === 'lg';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium border rounded-full ${
        isSm ? 'px-2 py-0.5 text-xs' : isLg ? 'px-4 py-1.5 text-base' : 'px-2.5 py-1 text-sm'
      } ${colorClasses.bg}`}
    >
      <span className={`w-2 h-2 rounded-full ${colorClasses.dot}`} />
      <Icon className={isSm ? 'w-3 h-3' : isLg ? 'w-5 h-5' : 'w-4 h-4'} />
      <span>{category || (numScore >= 60 ? 'High Risk' : numScore >= 30 ? 'Medium Risk' : 'Low Risk')}</span>
      {showScore && <span className="opacity-75 font-mono ml-0.5">({numScore}/100)</span>}
    </span>
  );
}
