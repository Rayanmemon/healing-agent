import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings as SettingsIcon, Save, RotateCcw, Server, Brain, Bell, Shield, Ticket, RefreshCcw } from 'lucide-react';
import { useToast } from './Toast';
import Spinner from './Spinner';
import { generateTickets } from '../services/api';

const SettingsPage = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  
  const [settings, setSettings] = useState({
    apiUrl: 'http://localhost:5000',
    llmModel: 'llama-3.3-70b-versatile',
    autoApproveThreshold: 85,
    enableNotifications: true,
    darkMode: true,
    pollingInterval: 5000,
    hitlRequiredRisk: 7,
    ticketCount: 5,
  });

  const [isGenerating, setIsGenerating] = useState(false);

  const [isSaving, setIsSaving] = useState(false);

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate save - in real app would persist to backend
    await new Promise(r => setTimeout(r, 800));
    localStorage.setItem('agentSettings', JSON.stringify(settings));
    setIsSaving(false);
    toast.success('Settings saved successfully');
  };

  const handleReset = () => {
    setSettings({
      apiUrl: 'http://localhost:5000',
      llmModel: 'llama-3.3-70b-versatile',
      autoApproveThreshold: 85,
      enableNotifications: true,
      darkMode: true,
      pollingInterval: 5000,
      hitlRequiredRisk: 7,
      ticketCount: 5,
    });
    toast.info('Settings reset to defaults');
  };

  const handleGenerateTickets = async () => {
    setIsGenerating(true);
    try {
      await generateTickets(settings.ticketCount);
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      toast.success(`Generated ${settings.ticketCount} new tickets`);
    } catch (error) {
      toast.error(`Failed to generate tickets: ${error.message}`);
    }
    setIsGenerating(false);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center space-x-3 mb-8">
        <div className="bg-slate-800 p-3 rounded-lg">
          <SettingsIcon className="text-slate-400" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Settings</h1>
          <p className="text-sm text-slate-400">Configure agent behavior and preferences</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* API Configuration */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Server size={18} className="text-indigo-400" />
            <h2 className="text-lg font-semibold text-slate-100">API Configuration</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">Backend URL</label>
              <input
                type="text"
                value={settings.apiUrl}
                onChange={(e) => handleChange('apiUrl', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-slate-400 mb-2">Polling Interval (ms)</label>
              <input
                type="number"
                value={settings.pollingInterval}
                onChange={(e) => handleChange('pollingInterval', parseInt(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* AI Configuration */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Brain size={18} className="text-emerald-400" />
            <h2 className="text-lg font-semibold text-slate-100">AI Configuration</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">LLM Model</label>
              <select
                value={settings.llmModel}
                onChange={(e) => handleChange('llmModel', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="llama-3.3-70b-versatile">Llama 3.3 70B (Groq)</option>
                <option value="llama-3.1-8b-instant">Llama 3.1 8B Instant</option>
                <option value="mixtral-8x7b-32768">Mixtral 8x7B</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                Auto-Approve Threshold: <span className="text-indigo-400 font-mono">{settings.autoApproveThreshold}%</span>
              </label>
              <input
                type="range"
                min="50"
                max="100"
                value={settings.autoApproveThreshold}
                onChange={(e) => handleChange('autoApproveThreshold', parseInt(e.target.value))}
                className="w-full accent-indigo-500"
              />
              <p className="text-xs text-slate-500 mt-1">
                Actions with confidence above this threshold may be auto-approved
              </p>
            </div>
          </div>
        </div>

        {/* HITL Configuration */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Shield size={18} className="text-amber-400" />
            <h2 className="text-lg font-semibold text-slate-100">Human-in-the-Loop</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                HITL Required Above Risk Level: <span className="text-amber-400 font-mono">{settings.hitlRequiredRisk}/10</span>
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={settings.hitlRequiredRisk}
                onChange={(e) => handleChange('hitlRequiredRisk', parseInt(e.target.value))}
                className="w-full accent-amber-500"
              />
              <p className="text-xs text-slate-500 mt-1">
                Actions with risk level above this require human approval
              </p>
            </div>
          </div>
        </div>

        {/* Ticket Generation */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Ticket size={18} className="text-cyan-400" />
            <h2 className="text-lg font-semibold text-slate-100">Ticket Generation</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">
                Number of Tickets: <span className="text-cyan-400 font-mono">{settings.ticketCount}</span>
              </label>
              <input
                type="range"
                min="3"
                max="20"
                value={settings.ticketCount}
                onChange={(e) => handleChange('ticketCount', parseInt(e.target.value))}
                className="w-full accent-cyan-500"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>3</span>
                <span>20</span>
              </div>
            </div>
            
            <button
              onClick={handleGenerateTickets}
              disabled={isGenerating}
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white py-2 rounded-lg font-medium flex items-center justify-center transition-colors disabled:opacity-50"
            >
              {isGenerating ? (
                <><Spinner size="sm" className="mr-2" /> Generating...</>
              ) : (
                <><RefreshCcw size={18} className="mr-2" /> Generate New Tickets</>
              )}
            </button>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Bell size={18} className="text-rose-400" />
            <h2 className="text-lg font-semibold text-slate-100">Notifications</h2>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-300">Enable Toast Notifications</p>
              <p className="text-xs text-slate-500">Show alerts for agent actions and errors</p>
            </div>
            <button
              onClick={() => handleChange('enableNotifications', !settings.enableNotifications)}
              className={`w-12 h-6 rounded-full transition-colors ${
                settings.enableNotifications ? 'bg-indigo-600' : 'bg-slate-700'
              }`}
            >
              <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
                settings.enableNotifications ? 'translate-x-6' : 'translate-x-0.5'
              }`} />
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-lg font-medium flex items-center justify-center transition-colors disabled:opacity-50"
          >
            {isSaving ? (
              <><Spinner size="sm" className="mr-2" /> Saving...</>
            ) : (
              <><Save size={18} className="mr-2" /> Save Settings</>
            )}
          </button>
          
          <button
            onClick={handleReset}
            className="px-6 bg-slate-800 hover:bg-slate-700 text-slate-200 py-3 rounded-lg font-medium flex items-center transition-colors"
          >
            <RotateCcw size={18} className="mr-2" /> Reset
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
