'use client';

import React from 'react';
import { Cpu, Activity } from 'lucide-react';

export default function ModelsPage() {
  return (
    <div className="p-8 pb-20 space-y-8 animate-in fade-in duration-700">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <Cpu className="text-cyber-cyan" /> Model Registry
        </h1>
        <p className="text-gray-400 mt-1">Manage AI and Quantum optimization models.</p>
      </header>

      <div className="glass-card rounded-xl border border-border-subtle overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface-dim border-b border-border-subtle text-xs uppercase tracking-wider text-gray-400">
              <th className="p-4 font-medium">Model Name</th>
              <th className="p-4 font-medium">Type</th>
              <th className="p-4 font-medium">Accuracy</th>
              <th className="p-4 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 text-sm font-medium text-white">N-BEATS Demand Forecaster</td>
              <td className="p-4 text-sm text-gray-400">Deep Learning</td>
              <td className="p-4 text-sm text-white">92.4%</td>
              <td className="p-4"><span className="text-xs font-medium text-green-400 bg-green-500/10 px-2 py-1 rounded">Active</span></td>
            </tr>
            <tr className="hover:bg-white/5 transition-colors">
              <td className="p-4 text-sm font-medium text-white">QAOA Router v2</td>
              <td className="p-4 text-sm text-gray-400">Quantum Hybrid</td>
              <td className="p-4 text-sm text-white">N/A (Cost -12%)</td>
              <td className="p-4"><span className="text-xs font-medium text-amber-400 bg-amber-500/10 px-2 py-1 rounded">A/B Testing</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
