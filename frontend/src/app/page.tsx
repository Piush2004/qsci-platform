"use client";

import React, { useState } from 'react';
import {
  Database,
  LineChart,
  Target,
  Calculator,
  Search,
  CheckCircle2,
  RefreshCw,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  Cpu,
  Atom,
  ChevronRight,
  Menu
} from 'lucide-react';

const Navbar = () => (
  <nav className="border-b border-slate-800/50 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
    <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-cyan-900 rounded flex items-center justify-center border border-cyan-700">
          <div className="w-3 h-3 bg-cyan-400 rounded-sm"></div>
        </div>
        <span className="font-mono font-bold text-lg tracking-wider text-white">QSCI</span>
      </div>
      <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
        <a href="#" className="hover:text-white transition-colors">Platform</a>
        <a href="#" className="hover:text-white transition-colors">Solutions</a>
        <a href="#" className="hover:text-white transition-colors">Research</a>
        <a href="#" className="hover:text-white transition-colors">Company</a>
      </div>
      <div className="flex items-center gap-4">
        <button className="hidden md:block text-sm font-medium text-slate-300 hover:text-white transition-colors">Sign In</button>
        <button className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded text-sm font-medium transition-colors shadow-[0_0_15px_rgba(8,145,178,0.3)]">
          Request Demo
        </button>
        <button className="md:hidden text-slate-300">
          <Menu />
        </button>
      </div>
    </div>
  </nav>
);

const HeroSection = () => (
  <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden border-b border-slate-800/50">
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950 -z-10"></div>
    <div className="absolute top-0 left-0 right-0 h-[500px] bg-gradient-to-b from-cyan-900/10 to-transparent pointer-events-none -z-10"></div>
    
    <div className="relative max-w-7xl mx-auto px-6 text-center">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 backdrop-blur border border-slate-800 text-sm text-cyan-400 font-mono mb-8">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.8)]"></span>
        Platform Early Access
      </div>
      
      <h1 className="text-5xl md:text-7xl font-light tracking-tight mb-8 text-white max-w-5xl mx-auto leading-tight">
        FROM SUPPLY CHAIN SIGNALS TO <br className="hidden md:block"/>
        <span className="font-medium text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-400">
          INTELLIGENT DECISIONS.
        </span>
      </h1>
      
      <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto mb-12 font-light leading-relaxed">
        QSCI unifies predictive forecasting with advanced mathematical optimization and quantum-ready algorithms, delivering explainable financial impact for modern supply chains.
      </p>
      
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <button className="px-8 py-4 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(8,145,178,0.3)] w-full sm:w-auto">
          Explore the Platform <ArrowRight size={18} />
        </button>
        <button className="px-8 py-4 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-white rounded font-medium transition-all duration-200 flex items-center justify-center gap-2 w-full sm:w-auto">
          Read the Research
        </button>
      </div>
    </div>
  </section>
);

const PipelineSection = () => {
  const steps = [
    { id: 'data', label: 'DATA', icon: Database, color: 'text-slate-400' },
    { id: 'predict', label: 'PREDICT', icon: LineChart, color: 'text-blue-400' },
    { id: 'optimize', label: 'OPTIMIZE', icon: Target, color: 'text-indigo-400' },
    { id: 'quantify', label: 'QUANTIFY', icon: Calculator, color: 'text-violet-400' },
    { id: 'explain', label: 'EXPLAIN', icon: Search, color: 'text-purple-400' },
    { id: 'decide', label: 'DECIDE', icon: CheckCircle2, color: 'text-cyan-400' },
    { id: 'learn', label: 'LEARN', icon: RefreshCw, color: 'text-emerald-400' }
  ];

  const [activeStep, setActiveStep] = useState('optimize');

  return (
    <section className="py-24 bg-slate-950 border-b border-slate-800/50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-light mb-4">The Decision Intelligence Pipeline</h2>
          <p className="text-slate-400">End-to-end visibility and actionable intelligence at every step.</p>
        </div>

        <div className="flex justify-between items-center relative overflow-x-auto pb-8 hide-scrollbar snap-x">
          <div className="absolute left-0 right-0 top-1/2 h-[1px] bg-slate-800 -z-10 -translate-y-1/2 hidden md:block"></div>
          
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isActive = activeStep === step.id;
            return (
              <div 
                key={step.id}
                onClick={() => setActiveStep(step.id)}
                className={`relative flex flex-col items-center gap-4 cursor-pointer group px-4 min-w-[120px] snap-center transition-all ${isActive ? '' : 'opacity-50 hover:opacity-100'}`}
              >
                <div className={`w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-300 ${isActive ? 'bg-slate-800 border-2 border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.2)] scale-110' : 'bg-slate-900 border border-slate-800 group-hover:border-slate-600'}`}>
                  <Icon className={`w-6 h-6 ${isActive ? step.color : 'text-slate-500 group-hover:text-slate-300'}`} />
                </div>
                <span className={`text-xs font-mono tracking-wider ${isActive ? 'text-white' : 'text-slate-500'}`}>
                  {step.label}
                </span>
                
                {idx < steps.length - 1 && (
                  <div className="absolute right-[-20px] top-7 -translate-y-1/2 text-slate-800 hidden md:block">
                    <ChevronRight size={16} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

const VisualStorySection = () => {
  return (
    <section className="py-32 bg-slate-950">
      <div className="max-w-6xl mx-auto px-6 space-y-32">
        
        {/* Story 1: Forecast */}
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <div className="text-cyan-400 font-mono text-sm mb-4 tracking-widest">01. PREDICTIVE BASELINE</div>
            <h3 className="text-3xl lg:text-4xl font-light mb-6">Accurate Forecasting</h3>
            <p className="text-slate-400 text-lg leading-relaxed mb-6">
              Our models ingest diverse supply chain signals—from historical ERP data to external market drivers—to generate highly accurate demand forecasts, establishing the baseline for future operations.
            </p>
            <ul className="space-y-4 text-slate-300">
              <li className="flex items-center gap-3"><CheckCircle2 className="text-cyan-500 w-5 h-5"/> High-dimensional time-series models</li>
              <li className="flex items-center gap-3"><CheckCircle2 className="text-cyan-500 w-5 h-5"/> Automated exogenous variable integration</li>
            </ul>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-tr from-cyan-900/10 to-transparent"></div>
            {/* Mock Dashboard UI */}
            <div className="bg-slate-950 rounded-xl border border-slate-800 p-4 relative z-10">
               <div className="flex justify-between items-center mb-6">
                 <div className="text-sm text-slate-400">Demand Forecast: SKU-9042</div>
                 <div className="flex gap-2">
                   <span className="w-2 h-2 rounded-full bg-slate-700"></span>
                   <span className="w-2 h-2 rounded-full bg-slate-700"></span>
                   <span className="w-2 h-2 rounded-full bg-slate-700"></span>
                 </div>
               </div>
               <div className="h-48 border-b border-l border-slate-800 relative flex items-end pt-4 pb-2">
                 <svg className="w-full h-full text-blue-500/20" viewBox="0 0 100 100" preserveAspectRatio="none">
                   <path d="M0,80 Q20,70 40,50 T80,40 T100,20 L100,100 L0,100 Z" fill="currentColor" />
                   <path d="M0,80 Q20,70 40,50 T80,40 T100,20" fill="none" stroke="#3b82f6" strokeWidth="2" />
                   <path d="M70,0 L70,100" fill="none" stroke="#64748b" strokeWidth="1" strokeDasharray="4 4" />
                 </svg>
                 <div className="absolute left-[70%] top-0 bottom-0 border-l border-dashed border-slate-600">
                   <div className="absolute -top-4 -left-10 text-xs font-mono text-cyan-400">PREDICTED</div>
                 </div>
               </div>
            </div>
          </div>
        </div>

        {/* Story 2: But prediction isn't enough -> Optimization */}
        <div className="grid md:grid-cols-2 gap-16 items-center flex-col-reverse md:flex-row-reverse">
          <div>
            <div className="text-violet-400 font-mono text-sm mb-4 tracking-widest">02. MATHEMATICAL OPTIMIZATION</div>
            <h3 className="text-3xl lg:text-4xl font-light mb-6">Prediction isn't enough.</h3>
            <p className="text-slate-400 text-lg leading-relaxed mb-6">
              Knowing what will happen doesn't tell you what to do. QSCI translates predictions into optimal actions, balancing inventory holding costs, service level agreements, and complex logistics constraints.
            </p>
            <ul className="space-y-4 text-slate-300">
              <li className="flex items-center gap-3"><Target className="text-violet-500 w-5 h-5"/> Stochastic Optimization</li>
              <li className="flex items-center gap-3"><Target className="text-violet-500 w-5 h-5"/> Multi-echelon Inventory Routing</li>
            </ul>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
             <div className="absolute inset-0 bg-gradient-to-bl from-violet-900/10 to-transparent"></div>
             <div className="grid grid-cols-2 gap-4 relative z-10">
               <div className="bg-slate-950 rounded-xl border border-slate-800 flex flex-col justify-center items-center p-6 transition-transform hover:-translate-y-1">
                 <AlertTriangle className="text-amber-500 mb-4 w-8 h-8" />
                 <div className="text-sm text-slate-400 mb-1">Stockout Risk</div>
                 <div className="text-3xl font-mono text-amber-500">-12%</div>
               </div>
               <div className="bg-slate-950 rounded-xl border border-slate-800 flex flex-col justify-center items-center p-6 transition-transform hover:-translate-y-1">
                 <TrendingUp className="text-emerald-500 mb-4 w-8 h-8" />
                 <div className="text-sm text-slate-400 mb-1">Service Level</div>
                 <div className="text-3xl font-mono text-emerald-500">99.9%</div>
               </div>
               <div className="col-span-2 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between p-6">
                  <div className="flex flex-col">
                    <span className="text-slate-400 text-sm mb-1">Recommended Order Qty</span>
                    <span className="text-xs font-mono text-slate-500">Node: WH-NA-EAST</span>
                  </div>
                  <span className="text-2xl font-mono text-cyan-400">4,250 units</span>
               </div>
             </div>
          </div>
        </div>

        {/* Story 3: Financial Impact & Explainability */}
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <div className="text-emerald-400 font-mono text-sm mb-4 tracking-widest">03. QUANTIFY & EXPLAIN</div>
            <h3 className="text-3xl lg:text-4xl font-light mb-6">Financial Impact & Trust</h3>
            <p className="text-slate-400 text-lg leading-relaxed mb-6">
              AI shouldn't be a black box. Every QSCI recommendation is backed by a quantified financial impact and clear attribution, empowering human operators to make the final call with absolute confidence.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
             <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-emerald-900/10 to-transparent"></div>
             <div className="space-y-4 relative z-10">
                <div className="p-6 bg-slate-950 border border-slate-800 rounded-xl flex justify-between items-center shadow-lg">
                   <div className="flex items-center gap-4">
                     <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center">
                       <DollarSign className="text-emerald-500 w-5 h-5"/>
                     </div>
                     <span className="text-slate-300 font-medium">Projected Savings</span>
                   </div>
                   <span className="font-mono text-2xl text-emerald-400">+$2.4M</span>
                </div>
                <div className="p-6 bg-slate-950 border border-slate-800 rounded-xl">
                   <div className="text-sm font-medium text-slate-300 mb-4">Recommendation Attribution</div>
                   <div className="space-y-4">
                     <div>
                       <div className="flex justify-between text-xs mb-1">
                         <span className="text-slate-400">Supplier Lead Time Volatility</span>
                         <span className="text-cyan-400 font-mono">60%</span>
                       </div>
                       <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                         <div className="bg-cyan-500 h-full w-[60%] rounded-full"></div>
                       </div>
                     </div>
                     <div>
                       <div className="flex justify-between text-xs mb-1">
                         <span className="text-slate-400">Anticipated Demand Spike</span>
                         <span className="text-violet-400 font-mono">30%</span>
                       </div>
                       <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                         <div className="bg-violet-500 h-full w-[30%] rounded-full"></div>
                       </div>
                     </div>
                     <div>
                       <div className="flex justify-between text-xs mb-1">
                         <span className="text-slate-400">Holding Cost Threshold</span>
                         <span className="text-emerald-400 font-mono">10%</span>
                       </div>
                       <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                         <div className="bg-emerald-500 h-full w-[10%] rounded-full"></div>
                       </div>
                     </div>
                   </div>
                </div>
             </div>
          </div>
        </div>

      </div>
    </section>
  );
};

const ResearchEvidenceSection = () => {
  return (
    <section className="py-32 bg-slate-900 border-t border-slate-800/50">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-20">
          <h2 className="text-3xl lg:text-4xl font-light mb-6">Research & Validation</h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">Pioneering the transition from classical computing constraints to true quantum advantage in operations research.</p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8">
           {/* Classical */}
           <div className="bg-slate-950 border border-slate-800 rounded-2xl p-8 lg:p-10 relative overflow-hidden group hover:border-slate-700 transition-colors">
             <div className="absolute top-0 right-0 p-6 opacity-[0.03] group-hover:opacity-[0.05] transition-opacity">
               <Cpu className="w-32 h-32" />
             </div>
             <h3 className="text-2xl font-medium text-white mb-4 flex items-center gap-3">
               <div className="w-10 h-10 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center">
                 <Cpu className="w-5 h-5 text-slate-400" />
               </div>
               Classical Solvers
             </h3>
             <p className="text-slate-400 mb-8 text-base leading-relaxed">
               State-of-the-art heuristics (Simulated Annealing, Tabu Search) highly tuned for massive-scale global supply chain networks.
             </p>
             <div className="space-y-5">
               <div className="flex justify-between items-center text-sm border-b border-slate-800/50 pb-3">
                 <span className="text-slate-500">Problem Size limits</span>
                 <span className="text-slate-300 font-mono bg-slate-900 px-2 py-1 rounded">10,000+ Nodes</span>
               </div>
               <div className="flex justify-between items-center text-sm border-b border-slate-800/50 pb-3">
                 <span className="text-slate-500">Time to solution</span>
                 <span className="text-slate-300 font-mono bg-slate-900 px-2 py-1 rounded">Minutes</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-slate-500">Platform Status</span>
                 <span className="text-emerald-400 font-mono flex items-center gap-2">
                   <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Production Ready
                 </span>
               </div>
             </div>
           </div>

           {/* Quantum */}
           <div className="bg-slate-950 border border-violet-900/40 rounded-2xl p-8 lg:p-10 relative overflow-hidden group hover:border-violet-700/50 transition-colors">
             <div className="absolute inset-0 bg-gradient-to-br from-violet-900/10 to-transparent"></div>
             <div className="absolute top-0 right-0 p-6 opacity-[0.05] group-hover:opacity-[0.08] transition-opacity">
               <Atom className="w-32 h-32" />
             </div>
             <h3 className="text-2xl font-medium text-white mb-4 flex items-center gap-3 relative z-10">
               <div className="w-10 h-10 rounded-lg bg-violet-950 border border-violet-800 flex items-center justify-center">
                 <Atom className="w-5 h-5 text-violet-400" />
               </div>
               Quantum-Ready (QAOA)
             </h3>
             <p className="text-slate-400 mb-8 text-base leading-relaxed relative z-10">
               Formulating supply chain routing as QUBO problems, actively tested on quantum simulators and early-generation QPU hardware.
             </p>
             <div className="space-y-5 relative z-10">
               <div className="flex justify-between items-center text-sm border-b border-slate-800/50 pb-3">
                 <span className="text-slate-500">Problem Size limits</span>
                 <span className="text-slate-300 font-mono bg-slate-900 px-2 py-1 rounded">50-100 Qubits</span>
               </div>
               <div className="flex justify-between items-center text-sm border-b border-slate-800/50 pb-3">
                 <span className="text-slate-500">Algorithm Class</span>
                 <span className="text-slate-300 font-mono bg-slate-900 px-2 py-1 rounded">QAOA / VQE</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-slate-500">Platform Status</span>
                 <span className="text-violet-400 font-mono flex items-center gap-2">
                   <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse"></span> Active Research
                 </span>
               </div>
             </div>
           </div>
        </div>
      </div>
    </section>
  );
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-cyan-900 selection:text-cyan-50">
      <Navbar />
      <HeroSection />
      <PipelineSection />
      <VisualStorySection />
      <ResearchEvidenceSection />
      <footer className="border-t border-slate-800/50 py-12 bg-slate-950 text-center text-slate-500 text-sm">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-slate-900 rounded flex items-center justify-center border border-slate-700">
              <div className="w-2 h-2 bg-slate-500 rounded-sm"></div>
            </div>
            <span className="font-mono font-bold tracking-wider">QSCI</span>
          </div>
          <div>&copy; {new Date().getFullYear()} Quantum Supply Chain Intelligence. All rights reserved.</div>
          <div className="flex gap-4">
             <a href="#" className="hover:text-slate-300 transition-colors">Privacy Policy</a>
             <a href="#" className="hover:text-slate-300 transition-colors">Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
