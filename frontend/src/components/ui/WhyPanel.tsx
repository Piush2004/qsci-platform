'use client';

import React from 'react';
import { Info, Target, AlertCircle, DollarSign, HelpCircle, ArrowRight } from 'lucide-react';

interface ConfidenceMetrics {
  dataQuality: number;
  forecastStability: number;
  modelConsensus: number;
  backtestPerformance: number;
  overall: number;
}

interface FinancialImpact {
  holdingCost: number;
  lostSales: number;
  expectedSavings: number;
}

interface WhyPanelProps {
  title: string;
  recommendation: string;
  confidence: ConfidenceMetrics;
  financialImpact: FinancialImpact;
  constraints: string[];
  explanation: string;
  onApprove?: () => void;
  onReject?: () => void;
}

export function WhyPanel({
  title,
  recommendation,
  confidence,
  financialImpact,
  constraints,
  explanation,
  onApprove,
  onReject
}: WhyPanelProps) {
  return (
    <div className="bg-surface-dim border border-border-subtle rounded-xl overflow-hidden shadow-2xl max-w-lg w-full">
      {/* Header */}
      <div className="p-4 border-b border-border-subtle bg-surface flex items-center justify-between">
        <h3 className="text-white font-semibold flex items-center gap-2">
          <Info size={18} className="text-cyber-cyan" /> {title}
        </h3>
        <span className="text-2xl font-light text-cyber-cyan">{confidence.overall}%</span>
      </div>

      <div className="p-5 space-y-6">
        {/* The Action */}
        <div>
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Recommendation</p>
          <div className="bg-electric-blue/10 border border-electric-blue/30 rounded-lg p-4">
            <p className="text-white font-medium">{recommendation}</p>
            <p className="text-sm text-gray-400 mt-2 leading-relaxed">{explanation}</p>
          </div>
        </div>

        {/* Financial Impact */}
        <div>
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
            <DollarSign size={14} /> Financial Impact
          </p>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-surface rounded-lg p-3 border border-border-subtle">
              <p className="text-xs text-gray-500 mb-1">Holding Cost</p>
              <p className="text-sm font-semibold text-red-400">-${Math.abs(financialImpact.holdingCost).toLocaleString()}</p>
            </div>
            <div className="bg-surface rounded-lg p-3 border border-border-subtle">
              <p className="text-xs text-gray-500 mb-1">Lost Sales Risk</p>
              <p className="text-sm font-semibold text-amber-400">${Math.abs(financialImpact.lostSales).toLocaleString()}</p>
            </div>
            <div className="bg-surface rounded-lg p-3 border border-border-subtle">
              <p className="text-xs text-electric-blue mb-1">Expected Savings</p>
              <p className="text-sm font-bold text-cyber-cyan">+${financialImpact.expectedSavings.toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Confidence Decomposition */}
        <div>
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
            <Target size={14} /> Confidence Decomposition
          </p>
          <div className="space-y-3">
            {[
              { label: 'Data Quality', value: confidence.dataQuality },
              { label: 'Forecast Stability', value: confidence.forecastStability },
              { label: 'Model Consensus', value: confidence.modelConsensus },
              { label: 'Historical Backtest', value: confidence.backtestPerformance },
            ].map((metric) => (
              <div key={metric.label}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">{metric.label}</span>
                  <span className="text-white font-medium">{metric.value}%</span>
                </div>
                <div className="h-1.5 w-full bg-surface rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-electric-blue rounded-full"
                    style={{ width: `${metric.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Constraints */}
        <div>
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
            <AlertCircle size={14} /> Business Constraints Applied
          </p>
          <ul className="space-y-2">
            {constraints.map((constraint, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-electric-blue mt-0.5">•</span> {constraint}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Action Footer */}
      <div className="p-4 border-t border-border-subtle bg-surface flex gap-3">
        <button 
          onClick={onReject}
          className="flex-1 px-4 py-2 bg-surface hover:bg-white/5 border border-border-subtle text-white text-sm font-medium rounded-lg transition-colors"
        >
          Reject / Override
        </button>
        <button 
          onClick={onApprove}
          className="flex-1 px-4 py-2 bg-electric-blue hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          Approve Action <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
