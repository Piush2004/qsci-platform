'use client';

import React, from 'react';
import { 
  Database, Activity, TrendingUp, AlertTriangle, GitPullRequest, 
  Settings, DollarSign, Percent, CheckCircle, UserCheck, Search, History 
} from 'lucide-react';

export type DecisionStage = 
  | 'DATA' | 'DATA QUALITY' | 'FORECAST' | 'UNCERTAINTY' | 'RISK' 
  | 'OPTIMIZATION' | 'FINANCIAL IMPACT' | 'CONFIDENCE' | 'RECOMMENDATION' 
  | 'HUMAN DECISION' | 'AUDIT' | 'OUTCOME';

interface DecisionChainProps {
  currentStage: DecisionStage;
  onStageClick?: (stage: DecisionStage) => void;
}

const STAGES = [
  { id: 'DATA', label: 'Data', icon: Database },
  { id: 'DATA QUALITY', label: 'Quality', icon: Activity },
  { id: 'FORECAST', label: 'Forecast', icon: TrendingUp },
  { id: 'UNCERTAINTY', label: 'Uncertainty', icon: AlertTriangle },
  { id: 'RISK', label: 'Risk', icon: GitPullRequest },
  { id: 'OPTIMIZATION', label: 'Optimization', icon: Settings },
  { id: 'FINANCIAL IMPACT', label: 'Financial Impact', icon: DollarSign },
  { id: 'CONFIDENCE', label: 'Confidence', icon: Percent },
  { id: 'RECOMMENDATION', label: 'Recommendation', icon: CheckCircle },
  { id: 'HUMAN DECISION', label: 'Human Review', icon: UserCheck },
  { id: 'AUDIT', label: 'Audit', icon: Search },
  { id: 'OUTCOME', label: 'Outcome', icon: History }
];

export function DecisionChain({ currentStage, onStageClick }: DecisionChainProps) {
  const currentIndex = STAGES.findIndex(s => s.id === currentStage);

  return (
    <div className="w-full overflow-x-auto py-4 scrollbar-hide">
      <div className="flex items-center min-w-max px-2">
        {STAGES.map((stage, index) => {
          const Icon = stage.icon;
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isPending = index > currentIndex;

          return (
            <React.Fragment key={stage.id}>
              {/* Node */}
              <div 
                className={`flex flex-col items-center gap-2 cursor-pointer group transition-all duration-300 ${
                  isCurrent ? 'scale-110' : 'hover:scale-105'
                }`}
                onClick={() => onStageClick?.(stage.id as DecisionStage)}
              >
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors duration-300
                  ${isCompleted ? 'bg-electric-blue border-electric-blue text-white shadow-[0_0_15px_rgba(0,240,255,0.4)]' : ''}
                  ${isCurrent ? 'bg-surface-dim border-cyber-cyan text-cyber-cyan shadow-[0_0_20px_rgba(0,255,204,0.5)]' : ''}
                  ${isPending ? 'bg-surface border-border-subtle text-gray-500' : ''}
                `}>
                  <Icon size={18} />
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-wider ${
                  isCurrent ? 'text-cyber-cyan' : isCompleted ? 'text-electric-blue' : 'text-gray-500'
                }`}>
                  {stage.label}
                </span>
              </div>

              {/* Edge */}
              {index < STAGES.length - 1 && (
                <div className="w-12 h-[2px] mx-2 flex-shrink-0 relative">
                  <div className="absolute inset-0 bg-border-subtle rounded-full" />
                  <div className={`absolute inset-0 rounded-full transition-all duration-700 ${
                    isCompleted ? 'bg-electric-blue w-full shadow-[0_0_10px_rgba(0,240,255,0.5)]' : 'w-0'
                  }`} />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
