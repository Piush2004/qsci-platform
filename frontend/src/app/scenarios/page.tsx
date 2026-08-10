"use client";

import React, { useState } from 'react';
import { 
  Activity, AlertTriangle, ArrowRight, BarChart3, 
  ChevronRight, Copy, Filter, Info, Layers, 
  MoreVertical, Play, Plus, RefreshCw, Save, 
  Search, Settings, Share2, TrendingDown, TrendingUp,
  Zap, Clock, ShieldAlert, Target, Box
} from 'lucide-react';

// --- Mock Data ---

const SCENARIOS = [
  {
    id: 's1',
    title: 'What if demand spikes 30% in Q4?',
    category: 'Demand',
    status: 'Completed',
    riskLevel: 'High',
    impactCost: '+$2.4M',
    impactService: '-4.2%',
    lastRun: '10m ago'
  },
  {
    id: 's2',
    title: 'What if Supplier A is delayed by 14 days?',
    category: 'Supply',
    status: 'Completed',
    riskLevel: 'Critical',
    impactCost: '+$5.1M',
    impactService: '-12.0%',
    lastRun: '1h ago'
  },
  {
    id: 's3',
    title: 'Port Strike: West Coast 7-day shutdown',
    category: 'Logistics',
    status: 'Running',
    riskLevel: 'Medium',
    impactCost: '--',
    impactService: '--',
    lastRun: 'Active'
  },
  {
    id: 's4',
    title: 'Competitor price drop by 15%',
    category: 'Market',
    status: 'Draft',
    riskLevel: 'Low',
    impactCost: '--',
    impactService: '--',
    lastRun: '-'
  }
];

const METRICS = [
  { label: 'Total Revenue Impact', value: '-$1.2M', trend: 'down', type: 'negative' },
  { label: 'Fulfillment Cost', value: '+$3.4M', trend: 'up', type: 'negative' },
  { label: 'Service Level', value: '88.4%', trend: 'down', type: 'negative', baseline: '95.0%' },
  { label: 'Working Capital', value: '$42M', trend: 'up', type: 'positive', baseline: '$38M' }
];

export default function ScenariosHub() {
  const [activeScenario, setActiveScenario] = useState(SCENARIOS[1]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans selection:bg-cyan-500/30 flex flex-col">
      {/* Top Navigation / Header */}
      <header className="h-14 border-b border-slate-800 bg-slate-950/50 backdrop-blur-md flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-cyan-400">
            <Layers className="w-5 h-5" />
            <h1 className="text-sm font-semibold tracking-wide uppercase">QSCI <span className="text-slate-500">/</span> Scenarios Hub</h1>
          </div>
          <div className="h-4 w-px bg-slate-800 mx-2"></div>
          <div className="flex gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-violet-500/20 text-violet-300 border border-violet-500/30 uppercase tracking-wider">Decision Mode</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700 uppercase tracking-wider">Live Sandbox</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-2.5 top-1.5 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search scenarios..." 
              className="bg-slate-900 border border-slate-800 text-xs rounded-md pl-8 pr-3 py-1.5 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 w-64 text-slate-200 placeholder-slate-600 transition-all"
            />
          </div>
          <button className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-slate-900 rounded transition-colors">
            <Settings className="w-4 h-4" />
          </button>
          <button className="bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-semibold px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-colors">
            <Plus className="w-3.5 h-3.5" />
            New Scenario
          </button>
        </div>
      </header>

      {/* Main Content Workspace */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* Left Sidebar - Scenarios List */}
        <aside className="w-80 border-r border-slate-800 bg-slate-950/30 flex flex-col shrink-0">
          <div className="p-3 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Saved Simulations</h2>
            <button className="text-slate-500 hover:text-slate-300 p-1">
              <Filter className="w-3.5 h-3.5" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {SCENARIOS.map(scenario => (
              <div 
                key={scenario.id}
                onClick={() => setActiveScenario(scenario)}
                className={`p-3 rounded-md cursor-pointer border transition-all duration-200 ${
                  activeScenario.id === scenario.id 
                    ? 'bg-slate-900 border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.1)]' 
                    : 'bg-slate-950 border-slate-800 hover:border-slate-700 hover:bg-slate-900/50'
                }`}
              >
                <div className="flex justify-between items-start mb-1.5">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                    scenario.category === 'Supply' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' :
                    scenario.category === 'Demand' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' :
                    'bg-violet-500/10 text-violet-400 border border-violet-500/20'
                  }`}>
                    {scenario.category}
                  </span>
                  <span className="text-[10px] text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {scenario.lastRun}
                  </span>
                </div>
                <h3 className={`text-sm font-medium mb-2 ${activeScenario.id === scenario.id ? 'text-cyan-50' : 'text-slate-300'}`}>
                  {scenario.title}
                </h3>
                
                <div className="flex items-center justify-between text-xs mt-3">
                  <div className="flex gap-3">
                    <div className="flex flex-col">
                      <span className="text-[9px] text-slate-500 uppercase">Cost Impact</span>
                      <span className={`font-mono font-medium ${scenario.impactCost.includes('+') ? 'text-red-400' : 'text-slate-300'}`}>
                        {scenario.impactCost}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[9px] text-slate-500 uppercase">Service</span>
                      <span className={`font-mono font-medium ${scenario.impactService.includes('-') ? 'text-orange-400' : 'text-slate-300'}`}>
                        {scenario.impactService}
                      </span>
                    </div>
                  </div>
                  
                  {scenario.status === 'Running' ? (
                    <RefreshCw className="w-3.5 h-3.5 text-cyan-500 animate-spin" />
                  ) : (
                    <ChevronRight className={`w-4 h-4 ${activeScenario.id === scenario.id ? 'text-cyan-500' : 'text-slate-600'}`} />
                  )}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* Right Pane - Scenario Details (High Density) */}
        <main className="flex-1 overflow-y-auto flex flex-col">
          
          {/* Scenario Header */}
          <div className="p-4 lg:p-6 border-b border-slate-800 bg-slate-900/20">
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-orange-500/10 text-orange-400 border border-orange-500/20 uppercase tracking-wider flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Critical Risk
                  </span>
                  <span className="text-xs text-slate-500 font-mono">ID: {activeScenario.id.toUpperCase()}-091A</span>
                </div>
                <h2 className="text-2xl font-bold text-slate-50 tracking-tight">{activeScenario.title}</h2>
              </div>
              <div className="flex gap-2">
                <button className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-medium rounded flex items-center gap-1.5 transition-colors">
                  <Copy className="w-3.5 h-3.5" /> Clone
                </button>
                <button className="px-3 py-1.5 bg-violet-600/20 hover:bg-violet-600/30 border border-violet-500/30 text-violet-300 text-xs font-medium rounded flex items-center gap-1.5 transition-colors">
                  <Save className="w-3.5 h-3.5" /> Save Baseline
                </button>
                <button className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-bold rounded flex items-center gap-1.5 transition-colors shadow-[0_0_10px_rgba(6,182,212,0.3)]">
                  <Play className="w-3.5 h-3.5 fill-current" /> Run Simulation
                </button>
              </div>
            </div>

            <p className="text-sm text-slate-400 max-w-3xl leading-relaxed mb-6">
              This scenario models a catastrophic delay from Supplier A affecting 3 major product lines. 
              Simulation assumes no alternative sourcing available for the first 7 days, and standard buffer stock depletion.
            </p>

            {/* Top Level KPIs */}
            <div className="grid grid-cols-4 gap-4">
              {METRICS.map((metric, idx) => (
                <div key={idx} className="bg-slate-950 border border-slate-800 p-3 rounded-lg relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
                    {metric.trend === 'up' ? <TrendingUp className="w-8 h-8" /> : <TrendingDown className="w-8 h-8" />}
                  </div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1 font-semibold">{metric.label}</div>
                  <div className="flex items-end gap-2">
                    <div className={`text-2xl font-mono font-bold ${
                      metric.type === 'negative' ? 'text-red-400' : 'text-emerald-400'
                    }`}>
                      {metric.value}
                    </div>
                    {metric.baseline && (
                      <div className="text-xs text-slate-500 font-mono mb-1 line-through decoration-slate-600">
                        {metric.baseline}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Analysis Grid */}
          <div className="p-4 lg:p-6 grid grid-cols-3 gap-6 flex-1">
            
            {/* Column 1 & 2: Propagation & Charts */}
            <div className="col-span-2 space-y-6">
              
              {/* Supply Chain Impact Propagation */}
              <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-cyan-500" /> Impact Propagation
                  </h3>
                  <button className="text-xs text-cyan-400 hover:text-cyan-300">View Network Graph &rarr;</button>
                </div>
                
                <div className="relative">
                  {/* Connecting Line */}
                  <div className="absolute left-6 top-4 bottom-4 w-px bg-slate-800"></div>
                  
                  <div className="space-y-4">
                    {[
                      { node: 'Tier 1 Supplier (A)', effect: 'Production Halted', time: 'T+0 Days', color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20', icon: Box },
                      { node: 'Regional Distribution Center (EU)', effect: 'Buffer Stock Depleting (65%)', time: 'T+3 Days', color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20', icon: Layers },
                      { node: 'End Consumer Demand', effect: 'Service Level drops < 90%', time: 'T+7 Days', color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', icon: Target },
                    ].map((step, i) => (
                      <div key={i} className="relative flex items-center gap-4 pl-3">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center z-10 bg-slate-950 border border-slate-700`}>
                          <div className={`w-2 h-2 rounded-full ${step.color.replace('text-', 'bg-')}`}></div>
                        </div>
                        <div className={`flex-1 flex justify-between items-center p-3 rounded-md border ${step.border} ${step.bg}`}>
                          <div className="flex items-center gap-3">
                            <step.icon className={`w-4 h-4 ${step.color}`} />
                            <div>
                              <div className="text-xs font-semibold text-slate-200">{step.node}</div>
                              <div className={`text-[10px] ${step.color}`}>{step.effect}</div>
                            </div>
                          </div>
                          <div className="text-xs font-mono text-slate-400">{step.time}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Data Visualization Mock */}
              <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-violet-400" /> Projected Inventory vs Demand
                  </h3>
                  <div className="flex gap-2">
                    <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-2 h-2 rounded-full bg-cyan-500"></div> Demand</span>
                    <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-2 h-2 rounded-full bg-slate-600"></div> Inventory</span>
                  </div>
                </div>
                
                {/* Mock Chart Area */}
                <div className="h-48 w-full border-b border-l border-slate-700 relative flex items-end justify-between pt-4 px-2">
                  {/* Grid Lines */}
                  <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
                    {[1,2,3,4,5].map(i => <div key={i} className="w-full border-t border-slate-800/50"></div>)}
                  </div>
                  
                  {/* Bars */}
                  {[60, 55, 45, 30, 20, 15, 10, 5, 20, 40].map((val, i) => (
                    <div key={i} className="w-[8%] flex flex-col justify-end gap-1 items-center h-full group">
                      {/* Demand line sim */}
                      <div className="w-full h-0.5 bg-cyan-500/50 absolute" style={{ bottom: `${60 - (i*2)}%` }}></div>
                      
                      <div 
                        className={`w-full rounded-t-sm transition-all duration-300 ${val < 30 ? 'bg-red-500/40 border-t border-red-500' : 'bg-slate-700'}`}
                        style={{ height: `${val}%` }}
                      ></div>
                      <span className="text-[8px] text-slate-500 mt-1">D+{i}</span>
                    </div>
                  ))}
                  
                  {/* Critical Threshold Line */}
                  <div className="absolute w-full border-t border-dashed border-red-500/50 bottom-[30%] flex items-center">
                    <span className="text-[9px] text-red-400 absolute -left-12">Stockout</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Column 3: Actions & Parameters */}
            <div className="space-y-6">
              
              {/* Mitigation Strategies */}
              <div className="bg-slate-900/30 border border-slate-800 rounded-lg flex flex-col h-full max-h-[400px]">
                <div className="p-4 border-b border-slate-800">
                  <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-emerald-400" /> Auto-Generated Mitigations
                  </h3>
                </div>
                <div className="p-2 overflow-y-auto space-y-2">
                  {[
                    { title: 'Expedite Freight from Supplier B', cost: '+$450k', effect: '+12% Service Level', selected: true },
                    { title: 'Reallocate US Buffer Stock to EU', cost: '+$120k', effect: '+5% Service Level', selected: false },
                    { title: 'Accept Stockouts (No Action)', cost: '$0', effect: '-12% Service Level', selected: false }
                  ].map((action, i) => (
                    <label key={i} className={`flex items-start gap-3 p-3 rounded border cursor-pointer transition-colors ${
                      action.selected 
                        ? 'bg-cyan-900/20 border-cyan-500/50' 
                        : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                    }`}>
                      <input type="radio" name="mitigation" defaultChecked={action.selected} className="mt-1 accent-cyan-500" />
                      <div className="flex-1">
                        <div className={`text-xs font-medium mb-1 ${action.selected ? 'text-cyan-100' : 'text-slate-300'}`}>
                          {action.title}
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-slate-500">Cost: <span className="font-mono text-slate-300">{action.cost}</span></span>
                          <span className="text-slate-500">Impact: <span className="font-mono text-emerald-400">{action.effect}</span></span>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
                <div className="p-4 mt-auto border-t border-slate-800">
                  <button className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium py-2 rounded transition-colors flex items-center justify-center gap-2">
                    <Zap className="w-3.5 h-3.5 text-cyan-400" /> Apply Selected Mitigation
                  </button>
                </div>
              </div>

              {/* Scenario Parameters */}
              <div className="bg-slate-900/30 border border-slate-800 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <Settings className="w-4 h-4 text-slate-400" /> Model Parameters
                </h3>
                <div className="space-y-3">
                  {[
                    { label: 'Delay Duration', value: '14 Days' },
                    { label: 'Affected SKUs', value: '3,492' },
                    { label: 'Demand Variance', value: '± 5%' },
                    { label: 'Lead Time Factor', value: '1.5x' }
                  ].map((param, i) => (
                    <div key={i} className="flex justify-between items-center border-b border-slate-800/50 pb-2 last:border-0 last:pb-0">
                      <span className="text-xs text-slate-500">{param.label}</span>
                      <span className="text-xs font-mono text-slate-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                        {param.value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>

        </main>
      </div>
    </div>
  );
}