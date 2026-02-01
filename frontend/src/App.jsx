import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ShieldAlert, Activity, CheckCircle, Clock, Zap } from 'lucide-react';
import { fetchTickets, runAnalysis, fetchAuditLog } from './services/api';
import { useToast } from './components/Toast';
import Layout from './components/Layout';
import StatsCard from './components/StatsCard';
import TicketList from './components/TicketList';
import AgentActionPanel from './components/AgentActionPanel';
import AuditLogTable from './components/AuditLogTable';
import SettingsPage from './components/SettingsPage';
import Spinner from './components/Spinner';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [agentResults, setAgentResults] = useState({});
  const [rejectedTickets, setRejectedTickets] = useState(new Set());
  const queryClient = useQueryClient();
  const toast = useToast();

  // Fetch tickets for stats computation
  const { data: tickets, isLoading: ticketsLoading } = useQuery({ 
    queryKey: ['tickets'], 
    queryFn: fetchTickets,
    refetchInterval: 5000 
  });

  // Fetch audit log for stats
  const { data: auditLog } = useQuery({
    queryKey: ['audit-log'],
    queryFn: fetchAuditLog,
    refetchInterval: 5000
  });

  // Mutation to run agent analysis
  const agentMutation = useMutation({
    mutationFn: runAnalysis,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      queryClient.invalidateQueries({ queryKey: ['audit-log'] });
      
      const resultsList = Array.isArray(data) ? data : (data.data || []);
      const newResults = {};
      resultsList.forEach(result => {
        if (result.ticket && result.ticket.ticket_id) {
          newResults[result.ticket.ticket_id] = result;
        }
      });
      setAgentResults(prev => ({ ...prev, ...newResults }));
      
      toast.success(`Analyzed ${resultsList.length} tickets successfully!`);
    },
    onError: (error) => {
      toast.error(`Analysis failed: ${error.message}`);
    }
  });

  // Handle rejection
  const handleReject = async (ticketId) => {
    try {
      const { rejectAction } = await import('./services/api');
      await rejectAction(ticketId);
      
      setRejectedTickets(prev => new Set([...prev, ticketId]));
      setAgentResults(prev => {
        const updated = { ...prev };
        delete updated[ticketId];
        return updated;
      });
      setSelectedTicket(null);
      queryClient.invalidateQueries({ queryKey: ['audit-log'] });
      toast.info(`Ticket ${ticketId} rejected`);
    } catch (error) {
      toast.error(`Failed to reject: ${error.message}`);
    }
  };

  // Calculate real stats from data
  const totalTickets = tickets?.length || 0;
  const criticalCount = tickets?.filter(t => t.severity === 'critical').length || 0;
  const highCount = tickets?.filter(t => t.severity === 'high').length || 0;
  
  // Calculate stats
  const pendingApproval = Object.values(agentResults).filter(
    r => r.decision?.requires_approval && r.action_result?.status === 'pending_approval'
  ).length;
  const executedActions = auditLog?.filter(a => a.status === 'executed').length || 0;
  
  // Get active analysis for the selected ticket
  const activeResult = selectedTicket ? agentResults[selectedTicket.ticket_id] : null;
  
  // Render content based on current page
  const renderContent = () => {
    if (currentPage === 'settings') {
      return <SettingsPage />;
    }

    if (currentPage === 'audit') {
      return (
        <div>
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Audit Log</h2>
          <AuditLogTable />
        </div>
      );
    }

    // Dashboard (default)
    return (
      <>
        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard 
            title="Active Tickets" 
            value={ticketsLoading ? <Spinner size="sm" /> : totalTickets} 
            icon={Activity} 
            trend={totalTickets > 0 ? 5 : 0} 
            color="indigo" 
          />
          <StatsCard 
            title="Critical / High" 
            value={`${criticalCount} / ${highCount}`} 
            icon={ShieldAlert} 
            trend={criticalCount > 0 ? -criticalCount : 0} 
            color="rose" 
          />
          <StatsCard 
            title="Actions Executed" 
            value={executedActions} 
            icon={CheckCircle} 
            trend={executedActions > 0 ? 10 : 0} 
            color="emerald" 
          />
          <StatsCard 
            title="Pending Approval" 
            value={pendingApproval} 
            icon={Clock} 
            color="amber" 
          />
        </div>

        {/* Main Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[600px] mb-8">
          {/* Left Column: Ticket List */}
          <div className="lg:col-span-1 flex flex-col space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-slate-100">Queue</h2>
              <button 
                onClick={() => agentMutation.mutate()}
                disabled={agentMutation.isPending}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg text-sm font-medium flex items-center transition-colors disabled:opacity-50"
              >
                {agentMutation.isPending ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap size={14} className="mr-2" />
                    Run Agent
                  </>
                )}
              </button>
            </div>
            <div className="flex-1 overflow-auto">
              <TicketList onSelectTicket={setSelectedTicket} />
            </div>
          </div>

          {/* Right Column: Agent Action Panel */}
          <div className="lg:col-span-2">
            {selectedTicket ? (
              <AgentActionPanel 
                ticket={selectedTicket} 
                analysis={activeResult?.analysis} 
                decision={activeResult?.decision}
                onActionComplete={() => {
                  queryClient.invalidateQueries({ queryKey: ['tickets'] });
                  queryClient.invalidateQueries({ queryKey: ['audit-log'] });
                }}
                onReject={handleReject}
              />
            ) : (
               <div className="h-full bg-slate-900/50 border border-slate-800 rounded-xl flex flex-col items-center justify-center text-slate-500">
                 <Activity size={48} className="mb-4 opacity-20" />
                 <p>Select a ticket from the queue to view AI analysis</p>
               </div>
            )}
          </div>
        </div>
      </>
    );
  };

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderContent()}
    </Layout>
  );
}

export default App;
