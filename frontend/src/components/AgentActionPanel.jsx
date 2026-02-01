import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { approveAction } from '../services/api';
import { Check, X, AlertTriangle, Brain, GitPullRequest, Play, CheckCircle } from 'lucide-react';

const AgentActionPanel = ({ ticket, analysis, decision, onActionComplete, onReject }) => {
  const queryClient = useQueryClient();
  const [feedback, setFeedback] = useState(null);
  const [isExecuted, setIsExecuted] = useState(false);

  // Reset executed state when ticket changes
  useEffect(() => {
    setIsExecuted(false);
    setFeedback(null);
  }, [ticket?.ticket_id]);

  const [executionData, setExecutionData] = useState(null);

  const mutation = useMutation({
    mutationFn: approveAction,
    onSuccess: (data) => {
      setIsExecuted(true);
      setExecutionData(data.data?.action_details || data.action_details || null);
      setFeedback({ type: 'success', message: `Action approved and executed successfully!` });
      queryClient.invalidateQueries({ queryKey: ['audit-log'] });
      onActionComplete();
    },
    onError: (err) => {
      setFeedback({ type: 'error', message: `Failed: ${err.message}` });
    }
  });

  // No ticket selected at all
  if (!ticket) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-500 p-8 border border-dashed border-slate-800 rounded-xl">
        <Brain size={48} className="mb-4 opacity-50" />
        <p>Select a ticket to view Agent Analysis</p>
      </div>
    );
  }

  // Ticket selected but analysis not yet run
  if (!analysis) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col">
        <div className="flex items-center space-x-3 mb-6">
          <div className="bg-indigo-500/20 p-2 rounded-lg">
            <Brain className="text-indigo-400" size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100">Agent Analysis</h2>
            <p className="text-sm text-slate-400">Powered by Llama 3.3 (Groq)</p>
          </div>
        </div>

        {/* Ticket Info Preview */}
        <div className="bg-slate-800/50 rounded-lg p-4 mb-6">
          <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-2">Selected Ticket</h3>
          <p className="text-indigo-400 font-mono text-lg mb-1">#{ticket.ticket_id}</p>
          <p className="text-slate-300 text-sm mb-2">{ticket.issue}</p>
          <p className="text-slate-500 text-xs">{ticket.merchant_message}</p>
        </div>

        {/* Pending Analysis State */}
        <div className="flex-1 flex flex-col items-center justify-center text-center border border-dashed border-slate-700 rounded-lg p-8">
          <Play size={32} className="text-indigo-400 mb-4 opacity-70" />
          <p className="text-slate-400 mb-2">Analysis not yet run</p>
          <p className="text-slate-600 text-sm">Click <strong className="text-indigo-400">"Run Agent"</strong> to analyze this ticket</p>
        </div>
      </div>
    );
  }

  const confidenceColor = analysis.confidence > 80 ? 'text-emerald-400' : analysis.confidence > 50 ? 'text-amber-400' : 'text-rose-400';

  // Severity badge colors
  const severityColors = {
    critical: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    low: 'bg-blue-500/20 text-blue-400 border-blue-500/30'
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col overflow-auto">
      <div className="flex items-center space-x-3 mb-6">
        <div className="bg-indigo-500/20 p-2 rounded-lg">
          <Brain className="text-indigo-400" size={24} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-100">Agent Analysis</h2>
          <p className="text-sm text-slate-400">Powered by Llama 3.3 (Groq)</p>
        </div>
      </div>

      {/* Ticket Information Section */}
      <div className="bg-slate-800/50 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Ticket Information</h3>
          <span className={`text-xs px-2 py-1 rounded border ${severityColors[ticket.severity] || severityColors.medium}`}>
            {ticket.severity?.toUpperCase()}
          </span>
        </div>
        
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-slate-500">Ticket ID:</span>
            <span className="ml-2 text-slate-200 font-mono">{ticket.ticket_id}</span>
          </div>
          
          <div>
            <span className="text-slate-500">Category:</span>
            <span className="ml-2 text-indigo-400">{ticket.category?.replace(/_/g, ' ')}</span>
          </div>
          
          {ticket.merchant_id && (
            <div>
              <span className="text-slate-500">Merchant:</span>
              <span className="ml-2 text-slate-300 font-mono">{ticket.merchant_id}</span>
            </div>
          )}
          
          {ticket.error_type && (
            <div>
              <span className="text-slate-500">Error Type:</span>
              <span className="ml-2 text-rose-400 font-mono">{ticket.error_type}</span>
            </div>
          )}
          
          {ticket.checkout_failures !== undefined && (
            <div>
              <span className="text-slate-500">Checkout Failures:</span>
              <span className="ml-2 text-amber-400">{ticket.checkout_failures}</span>
            </div>
          )}
          
          {ticket.migration_stage && (
            <div>
              <span className="text-slate-500">Migration Stage:</span>
              <span className="ml-2 text-cyan-400">{ticket.migration_stage}</span>
            </div>
          )}
        </div>
        
        {ticket.description && (
          <div className="mt-3 pt-3 border-t border-slate-700">
            <p className="text-sm text-slate-400 leading-relaxed">{ticket.description}</p>
          </div>
        )}
      </div>

      <div className="space-y-6 flex-1">
        {/* Root Cause Section */}
        <div className="bg-slate-800/50 rounded-lg p-4">
          <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-2">Identified Root Cause</h3>
          <div className="flex items-center justify-between mb-2">
            <span className="text-lg font-mono text-indigo-300 font-medium">{analysis.root_cause}</span>
            <span className={`text-xl font-bold ${confidenceColor}`}>{analysis.confidence}%</span>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">{analysis.root_cause_explanation}</p>
        </div>

        {/* Decision/Action Section */}
        {decision && (
          <div className="bg-slate-800/50 rounded-lg p-4 relative overflow-hidden">
            {decision.requires_approval && (
              <div className="absolute top-0 right-0 bg-amber-500 text-slate-900 text-xs font-bold px-2 py-1 rounded-bl-lg flex items-center">
                <AlertTriangle size={12} className="mr-1" /> HITL REQUIRED
              </div>
            )}
            
            <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-2">Recommended Action</h3>
            <p className="text-white font-medium mb-1">{decision.action}</p>
            <p className="text-xs text-slate-400 mb-4">{decision.reasoning}</p>

            <div className="flex items-center space-x-4 text-xs text-slate-500 mb-4">
              <span className="flex items-center border border-slate-700 px-2 py-1 rounded">
                Risk Level: <span className={`ml-1 font-bold ${decision.risk_level >= 7 ? 'text-rose-400' : 'text-emerald-400'}`}>{decision.risk_level}/10</span>
              </span>
              <span className="flex items-center border border-slate-700 px-2 py-1 rounded">
                Merchants: <span className="ml-1 text-slate-300">{analysis.affected_merchants}</span>
              </span>
            </div>

            {isExecuted || feedback?.type === 'success' ? (
              <div className="mt-4 space-y-4">
                <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-3 rounded-lg flex items-center text-sm">
                  <CheckCircle size={16} className="mr-2" />
                  {feedback?.message || 'Action approved and executed successfully'}
                </div>
                
                {/* Execution Details */}
                {executionData && (
                  <div className="bg-slate-800/70 rounded-lg p-4 space-y-3">
                    <h4 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">Execution Details</h4>
                    
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {executionData.type && (
                        <div>
                          <span className="text-slate-500">Type:</span>
                          <span className="ml-2 text-indigo-400 font-mono">{executionData.type.replace(/_/g, ' ')}</span>
                        </div>
                      )}
                      
                      {executionData.execution_time && (
                        <div>
                          <span className="text-slate-500">Execution Time:</span>
                          <span className="ml-2 text-emerald-400">{executionData.execution_time}</span>
                        </div>
                      )}
                      
                      {executionData.to && (
                        <div className="col-span-2">
                          <span className="text-slate-500">Email Sent To:</span>
                          <span className="ml-2 text-slate-300">{executionData.to}</span>
                        </div>
                      )}
                      
                      {executionData.subject && (
                        <div className="col-span-2">
                          <span className="text-slate-500">Subject:</span>
                          <span className="ml-2 text-slate-300">{executionData.subject}</span>
                        </div>
                      )}
                      
                      {executionData.jira_ticket && (
                        <div>
                          <span className="text-slate-500">JIRA:</span>
                          <span className="ml-2 text-amber-400 font-mono">{executionData.jira_ticket}</span>
                        </div>
                      )}
                      
                      {executionData.priority && (
                        <div>
                          <span className="text-slate-500">Priority:</span>
                          <span className="ml-2 text-rose-400">{executionData.priority}</span>
                        </div>
                      )}
                      
                      {executionData.assigned_to && (
                        <div className="col-span-2">
                          <span className="text-slate-500">Assigned To:</span>
                          <span className="ml-2 text-slate-300">{executionData.assigned_to}</span>
                        </div>
                      )}
                      
                      {executionData.assigned_team && (
                        <div className="col-span-2">
                          <span className="text-slate-500">Team:</span>
                          <span className="ml-2 text-slate-300">{executionData.assigned_team}</span>
                        </div>
                      )}
                      
                      {executionData.notification_sent && (
                        <div className="col-span-2">
                          <span className="text-slate-500">Notification:</span>
                          <span className="ml-2 text-cyan-400">{executionData.notification_sent}</span>
                        </div>
                      )}
                      
                      {executionData.sla && (
                        <div>
                          <span className="text-slate-500">SLA:</span>
                          <span className="ml-2 text-amber-400">{executionData.sla}</span>
                        </div>
                      )}
                      
                      {executionData.kb_article && (
                        <div className="col-span-2">
                          <span className="text-slate-500">KB Article:</span>
                          <a href={executionData.kb_article} target="_blank" rel="noopener noreferrer" className="ml-2 text-blue-400 hover:underline">
                            {executionData.kb_article}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : decision.requires_approval ? (
              <div className="flex space-x-3 mt-4">
                <button 
                  onClick={() => mutation.mutate(ticket.ticket_id)}
                  disabled={mutation.isPending}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white py-2 rounded-lg font-medium flex items-center justify-center transition-colors disabled:opacity-50"
                >
                  {mutation.isPending ? 'Executing...' : (
                    <>
                      <Check size={18} className="mr-2" /> Approve & Execute
                    </>
                  )}
                </button>
                <button 
                  onClick={() => onReject && onReject(ticket.ticket_id)}
                  className="flex-1 bg-rose-600/20 hover:bg-rose-600/40 text-rose-400 border border-rose-600/30 py-2 rounded-lg font-medium flex items-center justify-center transition-colors"
                >
                  <X size={18} className="mr-2" /> Reject
                </button>
              </div>
            ) : (
              <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-3 rounded-lg flex items-center text-sm">
                <CheckCircle size={16} className="mr-2" />
                Action auto-executed by system
              </div>
            )}
          </div>
        )}
      </div>

      {feedback && (
        <div className={`mt-4 p-3 rounded-lg text-sm font-medium ${feedback.type === 'success' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
          {feedback.message}
        </div>
      )}
    </div>
  );
};

export default AgentActionPanel;
