"use client";
import React, { useState } from 'react';
import { 
  Building, 
  Users, 
  Key, 
  Bell, 
  Save, 
  Plus, 
  Trash2, 
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function SettingsHub() {
  const [activeTab, setActiveTab] = useState('organization');

  const tabs = [
    { id: 'organization', label: 'Organization', icon: Building },
    { id: 'roles', label: 'User Roles', icon: Users },
    { id: 'apikeys', label: 'API Keys', icon: Key },
    { id: 'notifications', label: 'Notifications', icon: Bell },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-8 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Settings Hub</h1>
            <p className="text-slate-500 text-sm">Manage organization preferences, access controls, and infrastructure settings.</p>
          </div>
          <button className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-md transition-colors text-sm font-medium">
            <Save className="w-4 h-4" />
            Save Changes
          </button>
        </div>

        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 shrink-0">
            <nav className="flex flex-col gap-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-md transition-all text-sm font-medium ${
                      isActive 
                        ? 'bg-slate-900 text-cyan-400 border border-slate-800 shadow-sm' 
                        : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-200'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content Area */}
          <div className="flex-1">
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 shadow-xl">
              
              {/* Organization Preferences */}
              {activeTab === 'organization' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <Building className="w-5 h-5 text-violet-400" />
                    Organization Preferences
                  </h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Organization Name</label>
                      <input 
                        type="text" 
                        defaultValue="QSCI Corp"
                        className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Support Email</label>
                      <input 
                        type="email" 
                        defaultValue="support@qsci.network"
                        className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
                      />
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Data Residency Region</label>
                      <select className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all">
                        <option>US East (N. Virginia)</option>
                        <option>EU (Frankfurt)</option>
                        <option>Asia Pacific (Tokyo)</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* User Roles */}
              {activeTab === 'roles' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                      <Users className="w-5 h-5 text-violet-400" />
                      Role Management
                    </h2>
                    <button className="flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded transition-colors border border-slate-700">
                      <Plus className="w-3 h-3" />
                      Add Role
                    </button>
                  </div>

                  <div className="overflow-hidden border border-slate-800 rounded-md">
                    <table className="w-full text-sm text-left">
                      <thead className="text-xs text-slate-400 uppercase bg-slate-950/50 border-b border-slate-800">
                        <tr>
                          <th className="px-4 py-3 font-medium">Role Name</th>
                          <th className="px-4 py-3 font-medium">Permissions</th>
                          <th className="px-4 py-3 font-medium">Users</th>
                          <th className="px-4 py-3 font-medium text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50">
                        <tr className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-4 py-3 font-medium text-slate-200">Super Admin</td>
                          <td className="px-4 py-3">
                            <span className="bg-violet-900/30 text-violet-400 border border-violet-800/50 px-2 py-0.5 rounded text-xs">All Access</span>
                          </td>
                          <td className="px-4 py-3 text-slate-400">3</td>
                          <td className="px-4 py-3 text-right">
                            <button className="text-slate-500 hover:text-cyan-400 transition-colors px-1">Edit</button>
                          </td>
                        </tr>
                        <tr className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-4 py-3 font-medium text-slate-200">Data Scientist</td>
                          <td className="px-4 py-3">
                            <div className="flex gap-1 flex-wrap">
                              <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded text-xs">Read Models</span>
                              <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded text-xs">Execute Experiments</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-slate-400">12</td>
                          <td className="px-4 py-3 text-right">
                            <button className="text-slate-500 hover:text-cyan-400 transition-colors px-1">Edit</button>
                          </td>
                        </tr>
                        <tr className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-4 py-3 font-medium text-slate-200">Viewer</td>
                          <td className="px-4 py-3">
                            <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded text-xs">Read Only</span>
                          </td>
                          <td className="px-4 py-3 text-slate-400">45</td>
                          <td className="px-4 py-3 text-right">
                            <button className="text-slate-500 hover:text-cyan-400 transition-colors px-1">Edit</button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* API Keys */}
              {activeTab === 'apikeys' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                      <Key className="w-5 h-5 text-cyan-400" />
                      API Keys
                    </h2>
                    <button className="flex items-center gap-1 text-xs bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/30 border border-cyan-500/30 px-3 py-1.5 rounded transition-colors">
                      <Plus className="w-3 h-3" />
                      Generate New Key
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div className="bg-slate-950 p-4 rounded-md border border-slate-800 flex justify-between items-center group">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-slate-200">Production Inference Key</span>
                          <span className="bg-green-900/30 text-green-400 text-[10px] uppercase px-1.5 py-0.5 rounded border border-green-800/50 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> Active
                          </span>
                        </div>
                        <code className="text-xs text-slate-500 font-mono">qsci_prod_xxxx...xxxx_8f92</code>
                        <div className="text-xs text-slate-600 mt-1">Created: Oct 12, 2025 • Last used: 2 mins ago</div>
                      </div>
                      <button className="text-slate-600 hover:text-red-400 transition-colors p-2 opacity-0 group-hover:opacity-100">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="bg-slate-950 p-4 rounded-md border border-slate-800 flex justify-between items-center group">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-slate-200">Staging Environment</span>
                          <span className="bg-yellow-900/30 text-yellow-400 text-[10px] uppercase px-1.5 py-0.5 rounded border border-yellow-800/50 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" /> Expiring Soon
                          </span>
                        </div>
                        <code className="text-xs text-slate-500 font-mono">qsci_stag_xxxx...xxxx_1a2b</code>
                        <div className="text-xs text-slate-600 mt-1">Created: Jan 05, 2026 • Last used: 1 day ago</div>
                      </div>
                      <button className="text-slate-600 hover:text-red-400 transition-colors p-2 opacity-0 group-hover:opacity-100">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications */}
              {activeTab === 'notifications' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <Bell className="w-5 h-5 text-violet-400" />
                    Alert Thresholds
                  </h2>

                  <div className="space-y-6 mt-4">
                    <div className="border-b border-slate-800 pb-6">
                      <h3 className="text-sm font-medium text-slate-200 mb-4">Infrastructure Health</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm text-slate-300">CPU Usage Alert</div>
                            <div className="text-xs text-slate-500">Notify when CPU utilization exceeds threshold for 5m</div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-sm font-mono text-cyan-400">85%</span>
                            <input type="range" min="50" max="99" defaultValue="85" className="w-24 accent-cyan-500" />
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm text-slate-300">API Latency Warning</div>
                            <div className="text-xs text-slate-500">Notify when p99 latency exceeds limit</div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-sm font-mono text-cyan-400">500ms</span>
                            <input type="range" min="100" max="2000" defaultValue="500" className="w-24 accent-cyan-500" />
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-slate-200 mb-4">Model Performance</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm text-slate-300">Data Drift Detection</div>
                            <div className="text-xs text-slate-500">Alert when confidence drops below threshold</div>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" defaultChecked className="sr-only peer" />
                            <div className="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyan-600"></div>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                </div>
              )}

            </div>
          </div>
        </div>

      </div>
    </div>
  );
}