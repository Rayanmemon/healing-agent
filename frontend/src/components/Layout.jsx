import React from 'react';
import { LayoutDashboard, FileText, Settings, Activity } from 'lucide-react';

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <div 
    className={`flex items-center space-x-3 px-4 py-3 rounded-lg cursor-pointer transition-colors ${
      active ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
    }`}
    onClick={onClick}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </div>
);

const Layout = ({ children, currentPage, onNavigate }) => {
  const pageTitle = {
    dashboard: 'Overview',
    settings: 'Settings',
    audit: 'Audit Log'
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col p-4">
        <div className="flex items-center space-x-2 px-2 mb-8">
          <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
            <Activity className="text-white" size={20} />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
            HealingAgent
          </span>
        </div>

        <nav className="flex-1 space-y-1">
          <SidebarItem 
            icon={LayoutDashboard} 
            label="Dashboard" 
            active={currentPage === 'dashboard'} 
            onClick={() => onNavigate('dashboard')}
          />
          <SidebarItem 
            icon={FileText} 
            label="Audit Log" 
            active={currentPage === 'audit'} 
            onClick={() => onNavigate('audit')}
          />
          <SidebarItem 
            icon={Settings} 
            label="Settings" 
            active={currentPage === 'settings'} 
            onClick={() => onNavigate('settings')}
          />
        </nav>

        <div className="pt-4 border-t border-slate-800">
          <div className="px-4 py-2">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <p className="text-xs text-slate-400 font-mono">Agent: ONLINE</p>
            </div>
            <p className="text-xs text-slate-600 mt-1">v1.0.0 • Groq LLM</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-slate-950">
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
          <h1 className="text-xl font-semibold text-slate-100">{pageTitle[currentPage] || 'Overview'}</h1>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-slate-800 rounded-full px-3 py-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-xs text-slate-300">System Healthy</span>
            </div>
            <img 
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=Admin" 
              alt="User" 
              className="w-8 h-8 rounded-full border border-slate-700 bg-slate-800"
            />
          </div>
        </header>

        <main className="p-8 max-w-7xl mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
