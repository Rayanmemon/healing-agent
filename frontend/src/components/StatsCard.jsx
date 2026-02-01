import React from 'react';

const StatsCard = ({ title, value, icon: Icon, trend, color = "indigo" }) => {
  const colorMap = {
    indigo: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    rose: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  };

  return (
    <div className={`p-6 rounded-xl border bg-slate-800/50 backdrop-blur-sm ${colorMap[color].split(' ')[2]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <p className="text-2xl font-bold mt-2 text-slate-100">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorMap[color]}`}>
          <Icon size={24} />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center text-xs">
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
