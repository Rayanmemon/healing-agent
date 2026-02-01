import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchTickets } from '../services/api';
import { AlertCircle, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

const SeverityBadge = ({ severity }) => {
  const colors = {
    critical: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium border ${colors[severity] || colors.medium} uppercase tracking-wide`}>
      {severity}
    </span>
  );
};

const TicketList = ({ onSelectTicket }) => {
  const { data: tickets, isLoading, error } = useQuery({
    queryKey: ['tickets'],
    queryFn: fetchTickets,
    refetchInterval: 5000, // Poll every 5 seconds
  });

  if (isLoading) return <div className="text-slate-500 animate-pulse">Loading tickets...</div>;
  if (error) return <div className="text-rose-400">Error loading tickets: {error.message}</div>;

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-slate-100">Recent Tickets</h2>
        <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded-full">{tickets?.length || 0} active</span>
      </div>
      
      <div className="divide-y divide-slate-800">
        {tickets?.map((ticket) => (
          <div 
            key={ticket.ticket_id}
            onClick={() => onSelectTicket(ticket)}
            className="p-4 hover:bg-slate-800/50 transition-colors cursor-pointer group"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center space-x-3">
                <span className="text-indigo-400 font-mono text-sm">#{ticket.ticket_id}</span>
                <SeverityBadge severity={ticket.severity} />
              </div>
              <span className="text-xs text-slate-500 group-hover:text-slate-400">{ticket.migration_stage}</span>
            </div>
            
            <p className="text-slate-300 text-sm font-medium line-clamp-1">{ticket.issue}</p>
            <p className="text-slate-500 text-xs mt-1 line-clamp-1">{ticket.merchant_message}</p>
          </div>
        ))}
        
        {(!tickets || tickets.length === 0) && (
          <div className="p-8 text-center text-slate-500 text-sm">
            No tickets found.
          </div>
        )}
      </div>
    </div>
  );
};

export default TicketList;
