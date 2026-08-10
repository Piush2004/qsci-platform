"use client";
import React, { useState } from 'react';
import { 
  Activity, 
  Settings2, 
  Network, 
  Cpu, 
  Thermometer, 
  LineChart, 
  Square, 
  BarChart3,
  GitCommit,
  GitBranch
} from 'lucide-react';

export default function OptimizationHub() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 p-6 font-mono text-sm selection:bg-cyan-900 selection:text-cyan-50">
      <header className="mb-8 border-b border-slate-800 pb-4 flex justify-between items-end">
        <div>
          <div className="text-cyan-500 text-xs font-semibold tracking-wider uppercase mb-1">QSCI Platform &gt; Optimization</div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Network className="text-violet-400" />
            Optimization Hub
          </h1>
        </div>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded border border-slate-800">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
            Active Nodes: 12/16
          </div>
          <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded border border-slate-800">
            <Cpu size={14} className="text-violet-400" />
            QPU Status: Idle
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Active Jobs */}
        <div className="lg:col-span-2 space-y-6">
          <section className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                <Activity size={18} className="text-cyan-400" />
                Active Stochastic Routing Jobs
              </h2>
              <button className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1 rounded border border-slate-700 transition-colors">
                + New Job
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                    <th className="pb-3 pr-4 font-medium">Job ID</th>
                    <th className="pb-3 pr-4 font-medium">Algorithm</th>
                    <th className="pb-3 pr-4 font-medium">Iteration</th>
                    <th className="pb-3 pr-4 font-medium">Objective (Cost)</th>
                    <th className="pb-3 pr-4 font-medium">Gap</th>
                    <th className="pb-3 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  <tr className="hover:bg-slate-800/20 transition-colors">
                    <td className="py-3 pr-4 text-cyan-300 font-medium">SRJ-8942A</td>
                    <td className="py-3 pr-4">QAOA (p=4)</td>
                    <td className="py-3 pr-4 text-slate-400">4,520 / 10,000</td>
                    <td className="py-3 pr-4">42,105.33</td>
                    <td className="py-3 pr-4 text-violet-400">1.2%</td>
                    <td className="py-3 flex justify-end gap-2">
                      <button className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-cyan-400"><Square size={14} /></button>
                      <button className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-cyan-400"><LineChart size={14} /></button>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-800/20 transition-colors">
                    <td className="py-3 pr-4 text-cyan-300 font-medium">SRJ-8943B</td>
                    <td className="py-3 pr-4">VQE (UCCSD)</td>
                    <td className="py-3 pr-4 text-slate-400">1,205 / 5,000</td>
                    <td className="py-3 pr-4">45,992.10</td>
                    <td className="py-3 pr-4 text-violet-400">3.8%</td>
                    <td className="py-3 flex justify-end gap-2">
                      <button className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-cyan-400"><Square size={14} /></button>
                      <button className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-cyan-400"><LineChart size={14} /></button>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-800/20 transition-colors">
                    <td className="py-3 pr-4 text-cyan-300 font-medium">SRJ-8941X</td>
                    <td className="py-3 pr-4">Simulated Annealing</td>
                    <td className="py-3 pr-4 text-slate-400">98,000 / 100,000</td>
                    <td className="py-3 pr-4 text-emerald-400">39,401.55</td>
                    <td className="py-3 pr-4 text-emerald-400">0.4%</td>
                    <td className="py-3 flex justify-end gap-2">
                      <button className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-cyan-400"><Square size={14} /></button>
                      <button className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-cyan-400"><LineChart size={14} /></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section className="bg-slate-900 border border-slate-800 rounded-lg p-5">
             <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                <BarChart3 size={18} className="text-violet-400" />
                Convergence Topology
              </h2>
              <div className="flex gap-2">
                 <select className="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-slate-300 focus:outline-none focus:border-cyan-500">
                    <option>Loss Landscape</option>
                    <option>Parameter Trace</option>
                 </select>
              </div>
            </div>
            
            {/* Placeholder for complex visualization */}
            <div className="h-64 border border-slate-800 rounded bg-slate-950/50 flex items-center justify-center relative overflow-hidden">
               {/* Abstract grid lines for "research/academic" feel */}
               <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(to right, #1e293b 1px, transparent 1px), linear-gradient(to bottom, #1e293b 1px, transparent 1px)', backgroundSize: '20px 20px', opacity: 0.3 }}></div>
               
               {/* Fake chart elements */}
               <svg className="w-full h-full absolute inset-0 text-cyan-500/20" preserveAspectRatio="none">
                  <path d="M0,200 Q100,50 200,150 T400,100 T600,180 T800,40" fill="none" stroke="currentColor" strokeWidth="2" />
               </svg>
               <svg className="w-full h-full absolute inset-0 text-violet-500/30" preserveAspectRatio="none">
                  <path d="M0,220 Q150,180 250,80 T450,120 T650,50 T800,100" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" />
               </svg>
               
               <div className="z-10 bg-slate-900/80 p-3 rounded border border-slate-700 backdrop-blur text-xs">
                 <div className="flex items-center gap-2 mb-1"><div className="w-2 h-2 bg-cyan-500 rounded-full"></div> QAOA Loss</div>
                 <div className="flex items-center gap-2"><div className="w-2 h-2 bg-violet-500 rounded-full"></div> SA Objective</div>
               </div>
            </div>
          </section>
        </div>

        {/* Right Column: Parameters */}
        <div className="space-y-6">
          <section className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2 mb-4">
              <Settings2 size={18} className="text-cyan-400" />
              Heuristic Parameters
            </h2>

            <div className="space-y-5">
              {/* SA Parameters */}
              <div className="border border-slate-800 rounded p-4 bg-slate-950/50">
                <h3 className="font-medium text-slate-200 flex items-center gap-2 mb-3">
                  <Thermometer size={14} className="text-rose-400" />
                  Simulated Annealing
                </h3>
                <div className="space-y-3 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Initial Temp (T₀)</span>
                    <span className="text-slate-200 font-medium">10,000.0</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Cooling Rate (α)</span>
                    <span className="text-slate-200 font-medium">0.995</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Schedule</span>
                    <span className="text-cyan-400 font-medium">Exponential</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Markov Chain Length</span>
                    <span className="text-slate-200 font-medium">500 iter</span>
                  </div>
                </div>
              </div>

              {/* Tabu Search */}
              <div className="border border-slate-800 rounded p-4 bg-slate-950/50">
                <h3 className="font-medium text-slate-200 flex items-center gap-2 mb-3">
                  <GitCommit size={14} className="text-violet-400" />
                  Tabu Search
                </h3>
                <div className="space-y-3 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Tabu Tenure</span>
                    <span className="text-slate-200 font-medium">Dynamic [10, 30]</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Aspiration Criteria</span>
                    <span className="text-cyan-400 font-medium">Enabled</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Neighborhood Size</span>
                    <span className="text-slate-200 font-medium">150 moves</span>
                  </div>
                </div>
              </div>
              
              {/* QAOA Parameters */}
              <div className="border border-slate-800 rounded p-4 bg-slate-950/50">
                <h3 className="font-medium text-slate-200 flex items-center gap-2 mb-3">
                  <GitBranch size={14} className="text-indigo-400" />
                  QAOA Settings
                </h3>
                <div className="space-y-3 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Depth (p)</span>
                    <span className="text-slate-200 font-medium">4</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Optimizer</span>
                    <span className="text-cyan-400 font-medium">COBYLA</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Shots</span>
                    <span className="text-slate-200 font-medium">8192</span>
                  </div>
                </div>
              </div>

            </div>
          </section>
        </div>
      </div>
    </div>
  );
}