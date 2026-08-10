"use client";
import React, { useState } from 'react';
import { 
  Database, 
  Activity, 
  Server, 
  Cpu, 
  HardDrive, 
  Globe, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight,
  Filter,
  Search,
  RefreshCw,
  BarChart3,
  Layers,
  Terminal
} from 'lucide-react';

const DataHubPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 font-sans selection:bg-cyan-500/30">
      {/* Header */}
      <header className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Database className="text-cyan-400 h-8 w-8" />
            Data Infrastructure Hub
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            Manage data ingestion, database health, and ML feature stores across the QSCI platform.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-md border border-slate-700 transition-colors text-sm font-medium">
            <RefreshCw className="h-4 w-4" />
            Sync Now
          </button>
          <button className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-md transition-colors text-sm font-medium shadow-[0_0_15px_rgba(8,145,178,0.4)]">
            <Filter className="h-4 w-4" />
            Filters
          </button>
        </div>
      </header>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          title="Total Processed" 
          value="1.24 PB" 
          change="+2.4TB today" 
          icon={<HardDrive className="h-5 w-5 text-cyan-400" />} 
          trend="up" 
        />
        <StatCard 
          title="Active Pipelines" 
          value="48" 
          change="3 degraded" 
          icon={<Activity className="h-5 w-5 text-violet-400" />} 
          trend="warning" 
        />
        <StatCard 
          title="Ingestion Rate" 
          value="45.2 GB/s" 
          change="Peak: 52GB/s" 
          icon={<Zap className="h-5 w-5 text-cyan-400" />} 
          trend="neutral" 
        />
        <StatCard 
          title="Query Latency (Avg)" 
          value="12ms" 
          change="-2ms vs yesterday" 
          icon={<Clock className="h-5 w-5 text-violet-400" />} 
          trend="down" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column - Database Health */}
        <div className="lg:col-span-1 space-y-6">
          <SectionHeader title="Database Health" icon={<Server className="h-5 w-5 text-slate-400" />} />
          
          <div className="space-y-4">
            {/* TimescaleDB */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-slate-700 transition-colors relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-cyan-500/10 transition-colors" />
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-white flex items-center gap-2">
                    TimescaleDB
                    <span className="flex h-2 w-2 rounded-full bg-emerald-500 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">Time-series telemetry & metrics</p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Healthy
                  </div>
                  <div className="text-xs text-slate-500 mt-1">v2.11.0</div>
                </div>
              </div>
              
              <div className="space-y-3">
                <HealthMetric label="CPU Usage" value={45} />
                <HealthMetric label="Memory (128GB)" value={72} />
                <HealthMetric label="Storage (5TB)" value={68} />
              </div>
              
              <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-500 block">Read QPS</span>
                  <span className="text-slate-300 font-mono">12,450</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Write QPS</span>
                  <span className="text-slate-300 font-mono">8,920</span>
                </div>
              </div>
            </div>

            {/* PostgreSQL */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-slate-700 transition-colors relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-violet-500/10 transition-colors" />
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-white flex items-center gap-2">
                    PostgreSQL
                    <span className="flex h-2 w-2 rounded-full bg-amber-500"></span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">Relational metadata & config</p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-amber-400 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" /> High Load
                  </div>
                  <div className="text-xs text-slate-500 mt-1">v15.3</div>
                </div>
              </div>
              
              <div className="space-y-3">
                <HealthMetric label="CPU Usage" value={88} color="bg-amber-500" />
                <HealthMetric label="Memory (64GB)" value={65} />
                <HealthMetric label="Storage (2TB)" value={42} />
              </div>

               <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-500 block">Active Conns</span>
                  <span className="text-slate-300 font-mono">842 / 1000</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Replication Lag</span>
                  <span className="text-slate-300 font-mono">45ms</span>
                </div>
              </div>
            </div>
            
            {/* Redis */}
            <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-slate-700 transition-colors relative overflow-hidden group">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-white flex items-center gap-2">
                    Redis Cache
                    <span className="flex h-2 w-2 rounded-full bg-emerald-500"></span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">Fast access & session data</p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Healthy
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <HealthMetric label="Memory Usage" value={32} />
                <HealthMetric label="Cache Hit Rate" value={98} color="bg-cyan-500" />
              </div>
            </div>
          </div>
        </div>

        {/* Middle & Right Columns - Pipelines & ML Stores */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Data Ingestion Pipelines */}
          <div>
            <SectionHeader title="Data Ingestion Pipelines" icon={<Activity className="h-5 w-5 text-slate-400" />} />
            
            <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
              <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
                <div className="relative">
                  <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" />
                  <input 
                    type="text" 
                    placeholder="Search pipelines..." 
                    className="bg-slate-950 border border-slate-700 rounded-md pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 text-slate-300 w-64"
                  />
                </div>
                <div className="text-xs text-slate-500">
                  Showing 4 of 48 active pipelines
                </div>
              </div>
              
              <div className="divide-y divide-slate-800/50">
                <PipelineRow 
                  name="IoT Sensor Telemetry (Kafka)" 
                  status="running" 
                  throughput="15.2 GB/s" 
                  latency="5ms" 
                  destination="TimescaleDB"
                  lastUpdated="Just now"
                />
                <PipelineRow 
                  name="Financial Tick Data (Kinesis)" 
                  status="running" 
                  throughput="8.4 GB/s" 
                  latency="12ms" 
                  destination="TimescaleDB"
                  lastUpdated="Just now"
                />
                <PipelineRow 
                  name="User Interaction Logs (S3)" 
                  status="degraded" 
                  throughput="1.2 GB/s" 
                  latency="450ms" 
                  destination="PostgreSQL"
                  lastUpdated="2 min ago"
                />
                <PipelineRow 
                  name="Market Sentiment Scraper (REST)" 
                  status="running" 
                  throughput="0.5 GB/s" 
                  latency="45ms" 
                  destination="PostgreSQL"
                  lastUpdated="5 min ago"
                />
              </div>
            </div>
          </div>

          {/* ML Feature Stores */}
          <div>
            <SectionHeader title="ML Feature Stores" icon={<Layers className="h-5 w-5 text-slate-400" />} />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FeatureStoreCard 
                name="Market Indicators"
                description="Aggregated technical indicators (RSI, MACD, Bollinger Bands) computed at 1m, 5m, 15m intervals."
                featureCount={124}
                modelCount={8}
                updateFreq="1 minute"
                size="450 GB"
                color="cyan"
              />
              <FeatureStoreCard 
                name="Sensor Anomalies"
                description="Pre-computed statistical baselines and deviation metrics for industrial IoT sensors."
                featureCount={56}
                modelCount={3}
                updateFreq="Real-time"
                size="1.2 TB"
                color="violet"
              />
              <FeatureStoreCard 
                name="User Behavior Profiles"
                description="Session-based embeddings and interaction metrics for personalization models."
                featureCount={210}
                modelCount={5}
                updateFreq="Hourly"
                size="85 GB"
                color="slate"
              />
              <div className="bg-slate-900/50 border border-slate-800 border-dashed rounded-lg p-5 flex flex-col items-center justify-center text-center hover:bg-slate-900 transition-colors cursor-pointer group">
                <div className="h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center mb-3 group-hover:bg-cyan-900/30 group-hover:text-cyan-400 transition-colors">
                  <Plus className="h-5 w-5 text-slate-400 group-hover:text-cyan-400" />
                </div>
                <h4 className="text-sm font-medium text-slate-300">Create New Feature Store</h4>
                <p className="text-xs text-slate-500 mt-1">Define schema and ingestion logic</p>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

// Sub-components

const Zap = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
  </svg>
);

const Plus = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
);

const SectionHeader = ({ title, icon }) => (
  <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-2">
    {icon}
    <h2 className="text-lg font-semibold text-slate-200">{title}</h2>
  </div>
);

const StatCard = ({ title, value, change, icon, trend }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col">
      <div className="flex justify-between items-start mb-2">
        <span className="text-slate-400 text-sm font-medium">{title}</span>
        <div className="p-2 bg-slate-950 rounded-md">
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className={`text-xs font-medium flex items-center gap-1 ${
        trend === 'up' ? 'text-emerald-400' : 
        trend === 'down' ? 'text-emerald-400' : 
        trend === 'warning' ? 'text-amber-400' : 'text-slate-500'
      }`}>
        {change}
      </div>
    </div>
  );
};

const HealthMetric = ({ label, value, color = "bg-cyan-500" }) => (
  <div>
    <div className="flex justify-between text-xs mb-1">
      <span className="text-slate-400">{label}</span>
      <span className="text-slate-300 font-mono">{value}%</span>
    </div>
    <div className="w-full bg-slate-950 rounded-full h-1.5 border border-slate-800 overflow-hidden">
      <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${value}%` }}></div>
    </div>
  </div>
);

const PipelineRow = ({ name, status, throughput, latency, destination, lastUpdated }) => {
  const isHealthy = status === 'running';
  
  return (
    <div className="p-4 hover:bg-slate-800/30 transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 group">
      <div className="flex items-center gap-3">
        <div className={`h-2 w-2 rounded-full ${isHealthy ? 'bg-emerald-500' : 'bg-amber-500'}`} />
        <div>
          <h4 className="text-sm font-medium text-slate-200">{name}</h4>
          <div className="text-xs text-slate-500 flex items-center gap-2 mt-1">
            <span className="flex items-center gap-1"><ArrowRight className="h-3 w-3" /> {destination}</span>
            <span>•</span>
            <span>{lastUpdated}</span>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-6 text-sm">
        <div className="text-right">
          <div className="text-slate-400 text-xs mb-0.5">Throughput</div>
          <div className="text-slate-200 font-mono">{throughput}</div>
        </div>
        <div className="text-right">
          <div className="text-slate-400 text-xs mb-0.5">Latency</div>
          <div className={`font-mono ${isHealthy ? 'text-slate-200' : 'text-amber-400'}`}>{latency}</div>
        </div>
        <button className="text-slate-500 hover:text-cyan-400 transition-colors p-2 opacity-0 group-hover:opacity-100">
          <Terminal className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

const FeatureStoreCard = ({ name, description, featureCount, modelCount, updateFreq, size, color }) => {
  const colorMap = {
    cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    violet: "text-violet-400 bg-violet-500/10 border-violet-500/20",
    slate: "text-slate-300 bg-slate-800 border-slate-700"
  };
  
  const iconColorMap = {
    cyan: "text-cyan-400",
    violet: "text-violet-400",
    slate: "text-slate-400"
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-slate-700 transition-colors flex flex-col h-full">
      <div className="flex justify-between items-start mb-3">
        <div className={`px-2.5 py-1 rounded-md text-xs font-medium border ${colorMap[color]}`}>
          {featureCount} Features
        </div>
        <div className="text-xs text-slate-500 font-mono">{size}</div>
      </div>
      
      <h3 className="text-md font-medium text-white mb-2">{name}</h3>
      <p className="text-xs text-slate-400 mb-4 flex-grow line-clamp-2">{description}</p>
      
      <div className="mt-auto pt-4 border-t border-slate-800 flex justify-between items-center">
        <div className="flex items-center gap-1.5 text-xs text-slate-300">
          <Cpu className={`h-3.5 w-3.5 ${iconColorMap[color]}`} />
          {modelCount} Models connected
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-500">
          <RefreshCw className="h-3 w-3" />
          {updateFreq}
        </div>
      </div>
    </div>
  );
};

export default DataHubPage;
