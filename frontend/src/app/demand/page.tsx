"use client";
import React, { useState } from 'react';
import { 
  Activity, TrendingUp, AlertTriangle, BarChart2, 
  Settings, Filter, Clock, Database, Zap, 
  ChevronDown, ArrowUpRight, ArrowDownRight, Maximize2
} from 'lucide-react';

// Simulated data for high-dimensional forecasting
const skuForecasts = [
  { id: 'SKU-7782', name: 'Quantum Processor Q1', current: 1240, predicted: 1450, delta: '+16.9%', confidence: 94, anomaly: false },
  { id: 'SKU-8921', name: 'Neuromorphic Core X', current: 890, predicted: 820, delta: '-7.8%', confidence: 88, anomaly: false },
  { id: 'SKU-3341', name: 'Cryogenic Cooling Unit', current: 450, predicted: 890, delta: '+97.7%', confidence: 76, anomaly: true },
  { id: 'SKU-1109', name: 'Optical Interconnect', current: 3100, predicted: 3150, delta: '+1.6%', confidence: 98, anomaly: false },
  { id: 'SKU-5542', name: 'Superconducting Qubit Array', current: 120, predicted: 45, delta: '-62.5%', confidence: 82, anomaly: true },
];

const anomalyAlerts = [
  { id: 'ALT-1', type: 'Demand Spike', item: 'Cryogenic Cooling Unit', impact: 'High', time: '2h ago' },
  { id: 'ALT-2', type: 'Trend Reversal', item: 'Superconducting Qubit Array', impact: 'Critical', time: '5h ago' },
  { id: 'ALT-3', type: 'Seasonal Deviation', item: 'Photon Detector', impact: 'Medium', time: '12h ago' },
];

export default function DemandHub() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans p-4 flex flex-col gap-4">
      {/* Header */}
      <header className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/10 rounded-md border border-cyan-500/30">
            <Activity className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-100 tracking-tight">Demand Hub</h1>
            <p className="text-xs text-slate-500">High-Dimensional Time-Series Forecasting • Decision Mode</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded text-xs hover:bg-slate-800 transition-colors">
            <Clock className="w-3.5 h-3.5 text-cyan-500" />
            <span>Horizon: 30 Days</span>
            <ChevronDown className="w-3.5 h-3.5" />
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded text-xs hover:bg-slate-800 transition-colors">
            <Filter className="w-3.5 h-3.5 text-violet-500" />
            <span>Filter SKU</span>
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-4 flex-1">
        
        {/* Left Column (Charts & Tables) */}
        <div className="col-span-9 flex flex-col gap-4">
          
          {/* Top Row: Aggregate & Anomalies */}
          <div className="grid grid-cols-3 gap-4 h-64">
            {/* Main Chart Area */}
            <div className="col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-sm font-medium text-slate-200 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-cyan-400" />
                  Aggregate Demand Trajectory
                </h2>
                <button className="text-slate-500 hover:text-slate-300">
                  <Maximize2 className="w-4 h-4" />
                </button>
              </div>
              
              {/* Simulated Chart Container */}
              <div className="flex-1 relative flex items-end gap-1">
                {/* Y-Axis */}
                <div className="absolute left-0 top-0 bottom-6 w-8 flex flex-col justify-between text-[10px] text-slate-600 border-r border-slate-800 pb-1">
                  <span>10k</span>
                  <span>7.5k</span>
                  <span>5k</span>
                  <span>2.5k</span>
                </div>
                
                {/* Grid Lines */}
                <div className="absolute left-8 top-0 right-0 bottom-6 flex flex-col justify-between pointer-events-none">
                  <div className="w-full border-t border-slate-800/50"></div>
                  <div className="w-full border-t border-slate-800/50"></div>
                  <div className="w-full border-t border-slate-800/50"></div>
                  <div className="w-full border-t border-slate-800/50"></div>
                </div>

                {/* Simulated Data Bars/Lines (Abstract representation) */}
                <div className="ml-10 flex-1 h-[calc(100%-1.5rem)] flex items-end justify-between relative">
                   {/* Historical Data (Solid) */}
                   <div className="w-1/12 bg-slate-700/50 h-[40%] rounded-t-sm border-t border-slate-500"></div>
                   <div className="w-1/12 bg-slate-700/50 h-[45%] rounded-t-sm border-t border-slate-500"></div>
                   <div className="w-1/12 bg-slate-700/50 h-[35%] rounded-t-sm border-t border-slate-500"></div>
                   <div className="w-1/12 bg-slate-700/50 h-[50%] rounded-t-sm border-t border-slate-500"></div>
                   <div className="w-1/12 bg-slate-700/50 h-[48%] rounded-t-sm border-t border-slate-500"></div>
                   <div className="w-1/12 bg-slate-700/50 h-[60%] rounded-t-sm border-t border-cyan-500 bg-cyan-900/30 relative">
                     <div className="absolute -top-2 left-1/2 w-1.5 h-1.5 rounded-full bg-cyan-400 transform -translate-x-1/2 ring-2 ring-cyan-400/30"></div>
                   </div>
                   
                   {/* Forecast Data (Dashed/Gradient) */}
                   <div className="w-1/12 bg-slate-800/50 h-[65%] rounded-t-sm border-t border-dashed border-violet-500"></div>
                   <div className="w-1/12 bg-slate-800/50 h-[75%] rounded-t-sm border-t border-dashed border-violet-500"></div>
                   <div className="w-1/12 bg-slate-800/50 h-[70%] rounded-t-sm border-t border-dashed border-violet-500"></div>
                   <div className="w-1/12 bg-slate-800/50 h-[85%] rounded-t-sm border-t border-dashed border-violet-500"></div>
                   <div className="w-1/12 bg-slate-800/50 h-[95%] rounded-t-sm border-t border-dashed border-violet-500 relative">
                     {/* Anomaly Marker */}
                     <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 flex flex-col items-center z-10">
                        <span className="text-[9px] bg-red-500/20 text-red-400 px-1 rounded border border-red-500/30 mb-0.5">Spike</span>
                        <div className="w-px h-3 bg-red-500/50"></div>
                     </div>
                   </div>
                </div>

                {/* X-Axis */}
                <div className="absolute left-10 right-0 bottom-0 h-6 flex justify-between items-end text-[10px] text-slate-500">
                  <span>W1</span>
                  <span>W2</span>
                  <span>W3</span>
                  <span className="text-cyan-500 font-medium">Now</span>
                  <span>W5</span>
                  <span>W6</span>
                  <span>W7</span>
                </div>
              </div>
            </div>

            {/* Anomalies Panel */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col">
              <h2 className="text-sm font-medium text-slate-200 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                Active Interventions
              </h2>
              <div className="flex-1 overflow-y-auto pr-1 space-y-2 custom-scrollbar">
                {anomalyAlerts.map(alert => (
                  <div key={alert.id} className="bg-slate-950 border border-slate-800 p-2.5 rounded hover:border-slate-700 transition-colors group cursor-pointer">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs font-medium text-slate-300">{alert.type}</span>
                      <span className="text-[10px] text-slate-500">{alert.time}</span>
                    </div>
                    <div className="text-xs text-slate-400 truncate mb-1">{alert.item}</div>
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                        alert.impact === 'Critical' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                        alert.impact === 'High' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' :
                        'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                      }`}>
                        {alert.impact} Impact
                      </span>
                      <ArrowUpRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-cyan-400 transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Table: High-Dimensional SKU Forecasts */}
          <div className="bg-slate-900 border border-slate-800 rounded-lg flex flex-col flex-1 overflow-hidden">
            <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
              <h2 className="text-sm font-medium text-slate-200 flex items-center gap-2">
                <Database className="w-4 h-4 text-violet-400" />
                Dimensional Forecast Matrix (SKU-Level)
              </h2>
              <div className="flex gap-2">
                <input 
                  type="text" 
                  placeholder="Search dimensions..." 
                  className="bg-slate-950 border border-slate-800 text-xs px-2 py-1 rounded w-48 focus:outline-none focus:border-cyan-500/50 transition-colors"
                />
              </div>
            </div>
            
            <div className="overflow-x-auto flex-1">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-950/50 text-[10px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                    <th className="p-3 font-medium">Dimension ID</th>
                    <th className="p-3 font-medium">SKU Designation</th>
                    <th className="p-3 font-medium text-right">Current Vol</th>
                    <th className="p-3 font-medium text-right">Projected (T+30)</th>
                    <th className="p-3 font-medium text-right">Delta</th>
                    <th className="p-3 font-medium text-center">Model Conf.</th>
                    <th className="p-3 font-medium text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="text-xs divide-y divide-slate-800/50">
                  {skuForecasts.map(sku => (
                    <tr key={sku.id} className="hover:bg-slate-800/20 transition-colors">
                      <td className="p-3 font-mono text-slate-400">{sku.id}</td>
                      <td className="p-3 font-medium text-slate-300">{sku.name}</td>
                      <td className="p-3 text-right tabular-nums">{sku.current.toLocaleString()}</td>
                      <td className="p-3 text-right tabular-nums text-slate-200">{sku.predicted.toLocaleString()}</td>
                      <td className="p-3 text-right">
                        <span className={`flex items-center justify-end gap-1 ${sku.delta.startsWith('+') ? 'text-cyan-400' : 'text-rose-400'}`}>
                          {sku.delta.startsWith('+') ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                          {sku.delta}
                        </span>
                      </td>
                      <td className="p-3 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <span className="tabular-nums text-slate-400 w-6 text-right">{sku.confidence}%</span>
                          <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${sku.confidence > 90 ? 'bg-cyan-500' : sku.confidence > 80 ? 'bg-violet-500' : 'bg-yellow-500'}`}
                              style={{ width: `${sku.confidence}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        {sku.anomaly ? (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                            <Zap className="w-3 h-3" /> Review
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            Nominal
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Sidebar (Metrics & Inference Stats) */}
        <div className="col-span-3 flex flex-col gap-4">
          
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Settings className="w-3.5 h-3.5" />
              Inference Engine
            </h3>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Active Model</span>
                  <span className="text-cyan-400 font-mono">Q-Transformer v2.4</span>
                </div>
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span>Last trained: 4h ago</span>
                  <span>Loss: 0.042</span>
                </div>
              </div>

              <div className="h-px w-full bg-slate-800"></div>

              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Global Forecast Accuracy</span>
                  <span className="text-slate-200">92.8%</span>
                </div>
                <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div className="w-[92.8%] h-full bg-gradient-to-r from-violet-500 to-cyan-500"></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-slate-400">Data Pipeline Latency</span>
                  <span className="text-slate-200">14ms</span>
                </div>
                <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div className="w-[15%] h-full bg-emerald-500"></div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex-1">
             <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <BarChart2 className="w-3.5 h-3.5" />
              Dimensionality Map
            </h3>

            <div className="space-y-3">
               {/* Abstract representation of dimensions being tracked */}
               <div className="bg-slate-950 p-2.5 rounded border border-slate-800/50">
                 <div className="text-xs text-slate-300 mb-1">Geospatial Nodes</div>
                 <div className="text-xl font-light text-slate-100 font-mono">1,402</div>
               </div>
               
               <div className="bg-slate-950 p-2.5 rounded border border-slate-800/50">
                 <div className="text-xs text-slate-300 mb-1">Time-Series Features</div>
                 <div className="text-xl font-light text-slate-100 font-mono">84,550</div>
               </div>
               
               <div className="bg-slate-950 p-2.5 rounded border border-slate-800/50">
                 <div className="text-xs text-slate-300 mb-1">Exogenous Variables</div>
                 <div className="text-xl font-light text-slate-100 font-mono">128</div>
                 <div className="text-[9px] text-slate-500 mt-1 flex gap-1 flex-wrap">
                   <span className="bg-slate-900 px-1 py-0.5 rounded border border-slate-800">Weather</span>
                   <span className="bg-slate-900 px-1 py-0.5 rounded border border-slate-800">Events</span>
                   <span className="bg-slate-900 px-1 py-0.5 rounded border border-slate-800">Macro-Econ</span>
                 </div>
               </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}