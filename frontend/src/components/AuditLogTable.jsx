import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchAuditLog, clearAuditLog } from '../services/api';
import { CheckCircle, Clock, User, Cpu, AlertCircle, Trash2 } from 'lucide-react';

const AuditLogTable = () => {
  const queryClient = useQueryClient();
  
  const { data: auditLog, isLoading } = useQuery({
    queryKey: ['audit-log'],
    queryFn: fetchAuditLog,
    refetchInterval: 5000
  });

  const clearMutation = useMutation({
    mutationFn: clearAuditLog,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit-log'] });
    }
  });

  const handleClear = () => {
    if (window.confirm('Are you sure you want to clear the audit log?')) {
      clearMutation.mutate();
    }
  };

  if (isLoading) return <div className="text-slate-500 text-sm">Loading audit history...</div>;

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden mt-6">
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Action Audit Log</h2>
        {auditLog && auditLog.length > 0 && (
          <button
            onClick={handleClear}
            disabled={clearMutation.isPending}
            className="text-slate-400 hover:text-rose-400 text-sm flex items-center transition-colors disabled:opacity-50"
          >
            <Trash2 size={14} className="mr-1" />
            {clearMutation.isPending ? 'Clearing...' : 'Clear Log'}
          </button>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-400">
          <thead className="bg-slate-800/50 uppercase text-xs font-semibold text-slate-500">
            <tr>
              <th className="px-6 py-3">Time</th>
              <th className="px-6 py-3">Ticket</th>
              <th className="px-6 py-3">Action</th>
              <th className="px-6 py-3">Triggered By</th>
              <th className="px-6 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {auditLog?.slice().reverse().map((log, idx) => (
              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap font-mono text-xs">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </td>
                <td className="px-6 py-4 text-indigo-400 font-medium">
                  {log.ticket_id}
                </td>
                <td className="px-6 py-4 text-slate-300">
                  {log.action}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    {log.triggered_by === 'human' ? (
                      <User size={14} className="text-amber-400" />
                    ) : (
                      <Cpu size={14} className="text-indigo-400" />
                    )}
                    <span className="capitalize">{log.triggered_by}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  {log.status === 'executed' ? (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle size={12} className="mr-1" /> Executed
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <Clock size={12} className="mr-1" /> Pending
                    </span>
                  )}
                </td>
              </tr>
            ))}
            {(!auditLog || auditLog.length === 0) && (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-slate-600">
                  No actions recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditLogTable;
