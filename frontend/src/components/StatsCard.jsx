import React from 'react';

const StatsCard = ({ title, value, icon: Icon, trend, color = "purple" }) => {
  const borderColors = {
    purple: "border-l-violet-500",
    indigo: "border-l-indigo-500",
    cyan: "border-l-cyan-400",
    pink: "border-l-pink-500",
    yellow: "border-l-amber-400",
    amber: "border-l-amber-400",
    rose: "border-l-rose-500",
    emerald: "border-l-emerald-500",
    green: "border-l-emerald-500",
    red: "border-l-rose-500",
  };

  const textColors = {
    purple: "text-violet-400",
    indigo: "text-indigo-400",
    cyan: "text-cyan-400",
    pink: "text-pink-400",
    yellow: "text-amber-400",
    amber: "text-amber-400",
    rose: "text-rose-400",
    emerald: "text-emerald-400",
    green: "text-emerald-400",
    red: "text-rose-400",
  };

  const iconBg = {
    purple: "bg-violet-500/20",
    indigo: "bg-indigo-500/20",
    cyan: "bg-cyan-500/20",
    pink: "bg-pink-500/20",
    yellow: "bg-amber-500/20",
    amber: "bg-amber-500/20",
    rose: "bg-rose-500/20",
    emerald: "bg-emerald-500/20",
    green: "bg-emerald-500/20",
    red: "bg-rose-500/20",
  };

  return (
    <div className={`p-6 rounded-2xl backdrop-blur-sm glass-card border-l-4 ${borderColors[color] || borderColors.purple} ${textColors[color] || textColors.purple} transition-all duration-300 hover:scale-[1.02]`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-slate-400">{title}</div>
          <div className="text-3xl font-bold mt-2 text-white">{value}</div>
        </div>
        <div className={`p-4 rounded-xl ${iconBg[color] || iconBg.purple}`}>
          <Icon size={28} className={textColors[color] || textColors.purple} />
        </div>
      </div>
      {trend !== undefined && trend !== 0 && (
        <div className="mt-4 flex items-center text-sm">
          <span className={trend > 0 ? "text-emerald-400" : "text-rose-400"}>
            {trend > 0 ? "+" : ""}{trend}%
          </span>
          <span className="text-slate-500 ml-2">from last batch</span>
        </div>
      )}
    </div>
  );
};

export default StatsCard;
