import React from 'react';
import { LayoutDashboard, FileText, Settings, Activity, Shield } from 'lucide-react';

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <div 
    className={`flex items-center space-x-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-300 ${
      active 
        ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-lg shadow-violet-500/20' 
        : 'text-slate-400 hover:bg-violet-500/10 hover:text-white'
    }`}
    onClick={onClick}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </div>
);

const Layout = ({ children, currentPage, onNavigate }) => {
  const pageTitle = {
    dashboard: 'Dashboard',
    settings: 'Settings',
    audit: 'Audit Log'
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Gradient top bar */}
      <div className="gradient-bar fixed top-0 left-0 right-0 z-50" />
      
      {/* Sidebar */}
      <div className="w-64 sidebar flex flex-col p-4 pt-6">
        <div className="flex items-center space-x-3 px-2 mb-10">
          <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Shield className="text-white" size={22} />
          </div>
          <div>
            <span className="text-lg font-bold gradient-text">
              Aegis
            </span>
            <p className="text-xs text-slate-500">AI Support Agent</p>
          </div>
        </div>

        <nav className="flex-1 space-y-2">
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

        <div className="pt-4 border-t border-violet-500/10">
          <div className="glass-card p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-lg shadow-emerald-500/50"></span>
              <p className="text-sm text-slate-300 font-medium">Agent Online</p>
            </div>
            <p className="text-xs text-slate-500">Powered by Groq • Llama 3.3</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto pt-1">
        <header className="h-16 flex items-center justify-between px-8 sticky top-0 z-10 backdrop-blur-xl bg-transparent">
          <div>
            <h1 className="text-2xl font-bold text-white">{pageTitle[currentPage] || 'Dashboard'}</h1>
            <p className="text-sm text-slate-400">Monitoring & managing support tickets</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="glass-card flex items-center space-x-2 px-4 py-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-sm text-slate-300">System Healthy</span>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white font-bold shadow-lg shadow-violet-500/20">
              A
            </div>
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
