"use client";

import React, { useState } from 'react';
import { 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Globe, 
  Clock, 
  ShieldAlert, 
  CheckCircle, 
  XCircle, 
  ChevronRight, 
  Box, 
  Truck, 
  Factory,
  BarChart2,
  Cpu,
  ArrowRight,
  Info,
  Layers,
  Zap
} from 'lucide-react';

export default function DecisionCenter() {
  const [selectedDecision, setSelectedDecision] = useState<number | null>(null);

  const kpis = [
    { label: 'Global Fulfillment', value: '98.2%', trend: '+0.4%', status: 'optimal' },
    { label: 'Capital Locked', value: '₹4.2M', trend: '-1.2%', status: 'warning' },
    { label: 'Supplier Risk Index', value: '24/100', trend: '-5.0%', status: 'optimal' },
    { label: 'Network Latency', value: '12ms', trend: '0ms', status: 'optimal' }
  ];

  const exceptions = [
    { id: 'E-092', type: 'Stockout Risk', target: 'SKU-103 (Quantum Processors)', timeframe: '48h', severity: 'critical' },
    { id: 'E-093', type: 'Supplier Delay', target: 'TechCorp Substrates', timeframe: '72h', severity: 'high' },
    { id: 'E-094', type: 'Capacity Alert', target: 'Warehouse Alpha', timeframe: '24h', severity: 'medium' }
  ];

  const decisions = [
    {
      id: 1,
      title: 'Reroute inventory to cover SKU-103 Stockout',
      exceptionId: 'E-092',
      impact: '₹82K',
      impactType: 'savings',
      confidence: 94,
      chain: [
        { step: 'Identify', detail: 'SKU-103 depletion rate increased by 40%.' },
        { step: 'Analyze', detail: 'Warehouse Beta has surplus. Cost to transfer is ₹12K. Potential lost sales: ₹94K.' },
        { step: 'Recommend', detail: 'Transfer 500 units from Beta to Alpha.' }
      ]
    },
    {
      id: 2,
      title: 'Expedite alternative supplier for Substrates',
      exceptionId: 'E-093',
      impact: '₹51K',
      impactType: 'risk_mitigation',
      confidence: 88,
      chain: [
        { step: 'Identify', detail: 'TechCorp shipments delayed by 4 days.' },
        { step: 'Analyze', detail: 'Production line 2 will stall in 72h. AltSupplier has immediate stock at 15% premium.' },
        { step: 'Recommend', detail: 'Procure 2000 units from AltSupplier.' }
      ]
    },
    {
      id: 3,
      title: 'Enable overflow storage protocol',
      exceptionId: 'E-094',
      impact: '₹14K',
      impactType: 'cost',
      confidence: 97,
      chain: [
        { step: 'Identify', detail: 'Warehouse Alpha approaching 98% capacity.' },
        { step: 'Analyze', detail: 'Inbound shipments exceed outflow. Nearby 3PL has space.' },
        { step: 'Recommend', detail: 'Activate 3PL overflow contract.' }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans p-4 selection:bg-cyan-900 selection:text-cyan-50">
      
      {/* 1. GLOBAL CONTEXT */}
      <header className="flex items-center justify-between border-b border-slate-800/60 pb-3 mb-4">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-gradient-to-br from-cyan-600 to-violet-700 rounded flex items-center justify-center border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
            <Cpu className="text-white h-4 w-4" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight leading-tight">Decision Center</h1>
            <div className="flex items-center text-[10px] text-slate-400 space-x-3 uppercase tracking-wider font-semibold mt-0.5">
              <span className="flex items-center"><Globe className="h-3 w-3 mr-1" /> Global Network</span>
              <span className="flex items-center"><Clock className="h-3 w-3 mr-1" /> Sync: 0ms</span>
              <span className="flex items-center text-cyan-400"><Zap className="h-3 w-3 mr-1" /> AI Active</span>
            </div>
          </div>
        </div>
        <div className="flex space-x-2">
          <button className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-xs hover:bg-slate-800 transition-colors">
            System Logs
          </button>
          <button className="px-3 py-1.5 bg-violet-600/20 border border-violet-500/30 text-violet-300 rounded text-xs hover:bg-violet-600/30 transition-colors flex items-center">
            <Activity className="h-3 w-3 mr-1.5" />
            Live Monitor
          </button>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-4">
        {/* Left Column: Context & Exceptions */}
        <div className="col-span-12 lg:col-span-4 space-y-4">
          
          {/* 2. BUSINESS KPIs */}
          <section className="bg-slate-900/50 border border-slate-800/80 rounded-lg p-3">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center">
              <BarChart2 className="h-3 w-3 mr-1.5" /> Business Pulse
            </h2>
            <div className="grid grid-cols-2 gap-2">
              {kpis.map((kpi, idx) => (
                <div key={idx} className="bg-slate-950/50 border border-slate-800/50 rounded p-2">
                  <div className="text-[10px] text-slate-500 mb-1">{kpi.label}</div>
                  <div className="flex items-baseline justify-between">
                    <div className="text-sm font-bold text-slate-100">{kpi.value}</div>
                    <div className={`text-[10px] flex items-center ${
                      kpi.status === 'optimal' ? 'text-emerald-400' : 'text-amber-400'
                    }`}>
                      {kpi.trend.startsWith('+') ? <TrendingUp className="h-2.5 w-2.5 mr-0.5" /> : <TrendingDown className="h-2.5 w-2.5 mr-0.5" />}
                      {kpi.trend}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 3. URGENT EXCEPTIONS */}
          <section className="bg-slate-900/50 border border-slate-800/80 rounded-lg p-3">
            <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center">
              <ShieldAlert className="h-3 w-3 mr-1.5 text-rose-400" /> Urgent Exceptions
            </h2>
            <div className="space-y-2">
              {exceptions.map(exc => (
                <div key={exc.id} className="flex items-start justify-between bg-slate-950 border border-rose-900/30 rounded p-2.5">
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-[10px] font-mono text-rose-400 bg-rose-400/10 px-1 rounded">{exc.id}</span>
                      <span className="text-xs font-medium text-slate-200">{exc.type}</span>
                    </div>
                    <div className="text-[11px] text-slate-400">{exc.target}</div>
                  </div>
                  <div className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                    T-{exc.timeframe}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right Column: Recommendations & Actions */}
        <div className="col-span-12 lg:col-span-8 space-y-4">
          
          {/* 4. RECOMMENDATIONS */}
          <section className="bg-slate-900/50 border border-slate-800/80 rounded-lg p-4 h-full flex flex-col">
            <h2 className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-4 flex items-center">
              <Layers className="h-3 w-3 mr-1.5" /> AI Recommendations
            </h2>
            
            <div className="flex-1 space-y-3">
              {decisions.map(decision => (
                <div 
                  key={decision.id} 
                  className={`border rounded-lg transition-all duration-200 ${
                    selectedDecision === decision.id 
                      ? 'bg-slate-800/40 border-cyan-500/50 shadow-[0_0_20px_rgba(6,182,212,0.1)]' 
                      : 'bg-slate-950/50 border-slate-800 hover:border-slate-700 cursor-pointer'
                  }`}
                  onClick={() => setSelectedDecision(decision.id === selectedDecision ? null : decision.id)}
                >
                  <div className="p-3 flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1.5">
                        <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/50 px-1.5 py-0.5 rounded border border-cyan-900">
                          {decision.confidence}% CONFIDENCE
                        </span>
                        <span className="text-[10px] font-mono text-slate-500">Ref: {decision.exceptionId}</span>
                      </div>
                      <h3 className="text-sm font-semibold text-slate-100">{decision.title}</h3>
                    </div>
                    
                    {/* FINANCIAL IMPACT */}
                    <div className="flex flex-col items-end mr-4">
                      <div className="text-[10px] text-slate-400 uppercase tracking-wide mb-0.5">Impact</div>
                      <div className={`text-sm font-bold font-mono ${
                        decision.impactType === 'savings' ? 'text-emerald-400' :
                        decision.impactType === 'cost' ? 'text-rose-400' : 'text-amber-400'
                      }`}>
                        {decision.impactType === 'cost' ? '-' : '+'}{decision.impact}
                      </div>
                    </div>

                    <ChevronRight className={`h-4 w-4 text-slate-500 transition-transform ${
                      selectedDecision === decision.id ? 'rotate-90' : ''
                    }`} />
                  </div>

                  {/* DECISION CHAIN & HUMAN APPROVAL (Expanded State) */}
                  {selectedDecision === decision.id && (
                    <div className="border-t border-slate-800 p-4 bg-slate-900/30 rounded-b-lg">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        
                        {/* Why Panel / Chain */}
                        <div>
                          <h4 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3">
                            Decision Chain
                          </h4>
                          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[9px] before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-slate-700 before:via-slate-700 before:to-transparent">
                            {decision.chain.map((step, idx) => (
                              <div key={idx} className="relative flex items-start space-x-3">
                                <div className="h-5 w-5 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center shrink-0 z-10 mt-0.5">
                                  <div className="h-1.5 w-1.5 rounded-full bg-cyan-500"></div>
                                </div>
                                <div>
                                  <div className="text-[11px] font-semibold text-slate-300">{step.step}</div>
                                  <div className="text-[11px] text-slate-400 leading-relaxed mt-0.5">{step.detail}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Approve / Reject */}
                        <div className="flex flex-col justify-end space-y-3 bg-slate-950/50 p-4 rounded border border-slate-800/80">
                          <h4 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                            Execution Requires Approval
                          </h4>
                          <p className="text-[11px] text-slate-500 mb-2">
                            Executing this decision will automatically generate purchase orders and update logistics routes.
                          </p>
                          <div className="flex space-x-2 mt-auto">
                            <button className="flex-1 flex items-center justify-center px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded transition-colors">
                              <XCircle className="h-3.5 w-3.5 mr-1.5" /> Reject
                            </button>
                            <button className="flex-1 flex items-center justify-center px-3 py-2 bg-gradient-to-r from-cyan-600 to-violet-600 hover:from-cyan-500 hover:to-violet-500 text-white text-xs font-medium rounded shadow-[0_0_10px_rgba(6,182,212,0.3)] transition-all">
                              <CheckCircle className="h-3.5 w-3.5 mr-1.5" /> Approve & Execute
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
