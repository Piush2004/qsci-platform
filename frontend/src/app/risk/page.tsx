import React from 'react';
import { ShieldAlert, TrendingUp, AlertTriangle, Clock, Activity, ArrowUpRight, ArrowDownRight, Filter, Search, MoreHorizontal } from 'lucide-react';

const RiskHub = () => {
  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-300 p-4 font-mono text-xs">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
        <div className="flex items-center gap-3">
          <ShieldAlert className="text-cyan-400 w-5 h-5" />
          <h1 className="text-lg font-semibold text-slate-100">QSCI // Risk Hub // Decision Mode</h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-slate-900/50 border border-slate-800 rounded px-2 py-1.5 focus-within:border-cyan-500/50 transition-colors">
            <Search className="w-3.5 h-3.5 text-slate-500 mr-2" />
            <input 
              type="text" 
              placeholder="Search suppliers, nodes..." 
              className="bg-transparent border-none outline-none text-xs text-slate-300 placeholder-slate-600 w-56" 
            />
          </div>
          <button className="flex items-center gap-1.5 bg-slate-800/80 hover:bg-slate-700 px-3 py-1.5 rounded border border-slate-700 transition-colors text-slate-200">
            <Filter className="w-3.5 h-3.5" /> Filters
          </button>
        </div>
      </header>

      {/* Top Metrics Grid */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <MetricCard title="Global Volatility Index" value="84.2" trend="+2.4%" status="critical" icon={<TrendingUp className="w-4 h-4 text-cyan-400" />} />
        <MetricCard title="High Risk Suppliers" value="12" trend="-1" status="warning" icon={<AlertTriangle className="w-4 h-4 text-amber-400" />} />
        <MetricCard title="Avg Lead-Time Disruption" value="+4.2 days" trend="+1.1 days" status="critical" icon={<Clock className="w-4 h-4 text-violet-400" />} />
        <MetricCard title="Network Resilience Score" value="76/100" trend="+3pts" status="good" icon={<Activity className="w-4 h-4 text-emerald-400" />} />
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Main Panel: Supplier Risk Matrix */}
        <div className="col-span-2 space-y-4">
          <div className="bg-slate-900/40 border border-slate-800/80 rounded shadow-sm p-3">
            <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
              <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Supplier Risk Matrix</h2>
              <button><MoreHorizontal className="w-4 h-4 text-slate-500 hover:text-slate-300" /></button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse whitespace-nowrap">
                <thead>
                  <tr className="text-slate-500 border-b border-slate-800/50">
                    <th className="font-normal pb-2 px-2">Supplier ID</th>
                    <th className="font-normal pb-2 px-2">Region</th>
                    <th className="font-normal pb-2 px-2">Risk Score</th>
                    <th className="font-normal pb-2 px-2">Volatility</th>
                    <th className="font-normal pb-2 px-2">Lead-Time Var.</th>
                    <th className="font-normal pb-2 px-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <SupplierRow id="SUP-8921" region="APAC" score="92" vol="High" lead="+8d" status="Critical" />
                  <SupplierRow id="SUP-4412" region="EMEA" score="84" vol="High" lead="+5d" status="Warning" />
                  <SupplierRow id="SUP-1093" region="NA" score="65" vol="Med" lead="+2d" status="Stable" />
                  <SupplierRow id="SUP-7734" region="LATAM" score="88" vol="High" lead="+6d" status="Warning" />
                  <SupplierRow id="SUP-2291" region="APAC" score="45" vol="Low" lead="-1d" status="Stable" />
                  <SupplierRow id="SUP-5582" region="EMEA" score="78" vol="Med" lead="+4d" status="Warning" />
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Volatility Graph Placeholder */}
            <div className="bg-slate-900/40 border border-slate-800/80 rounded p-3 flex flex-col">
              <div className="flex justify-between items-center mb-2">
                <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Volatility (30D)</h2>
                <span className="text-[10px] text-cyan-400 bg-cyan-900/20 px-1.5 py-0.5 rounded border border-cyan-800/30">Active</span>
              </div>
              <div className="h-32 flex items-end gap-1 pt-4 border-b border-l border-slate-800/80 mt-auto">
                {/* Synthetic bars for high data density feel */}
                {[40, 55, 45, 60, 75, 85, 80, 95, 88, 70, 65, 80, 90, 75].map((h, i) => (
                  <div key={i} className="flex-1 bg-cyan-900/40 hover:bg-cyan-400/60 transition-colors rounded-t" style={{ height: `${h}%` }}></div>
                ))}
              </div>
            </div>

            {/* AI Insights */}
            <div className="bg-slate-900/40 border border-slate-800/80 rounded p-3">
              <h2 className="text-xs font-semibold text-violet-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Activity className="w-3.5 h-3.5" /> Quantum AI Insights
              </h2>
              <ul className="space-y-2">
                <li className="bg-[#0B1120] p-2 rounded border border-slate-800/80 border-l-cyan-500 border-l-2 leading-relaxed">
                  <span className="text-cyan-400 font-semibold mr-1">Prediction:</span> 
                  Route APAC-NA shows 85% probability of +4d delay in next 72h.
                </li>
                <li className="bg-[#0B1120] p-2 rounded border border-slate-800/80 border-l-violet-500 border-l-2 leading-relaxed">
                  <span className="text-violet-400 font-semibold mr-1">Action:</span> 
                  Re-route shipments from SUP-8921 to backup nodes in EMEA. Est. cost: +$45k.
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Right Panel: Lead Time Disruptions */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded p-3 flex flex-col h-[calc(100vh-140px)]">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Lead-Time Disruptions</h2>
            <button><Filter className="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 transition-colors" /></button>
          </div>
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
            <DisruptionItem node="Port of Shanghai" impact="+6 days" severity="high" cause="Weather anomaly" />
            <DisruptionItem node="Frankfurt Hub" impact="+2 days" severity="medium" cause="Labor shortage" />
            <DisruptionItem node="Suez Canal" impact="+12 days" severity="critical" cause="Congestion" />
            <DisruptionItem node="Los Angeles Port" impact="+4 days" severity="high" cause="Equipment failure" />
            <DisruptionItem node="Rotterdam" impact="+1 day" severity="low" cause="Customs delay" />
            <DisruptionItem node="Shenzhen" impact="+3 days" severity="medium" cause="Capacity constraints" />
            <DisruptionItem node="Singapore" impact="+2 days" severity="medium" cause="Vessel delay" />
            <DisruptionItem node="Antwerp" impact="+1.5 days" severity="low" cause="Port strikes" />
            <DisruptionItem node="Dubai Jebel Ali" impact="+4 days" severity="high" cause="Volume surge" />
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, trend, status, icon }) => {
  const isPositive = trend.startsWith('+');
  return (
    <div className="bg-slate-900/40 border border-slate-800/80 rounded p-3 flex flex-col justify-between shadow-sm hover:border-slate-700 transition-colors">
      <div className="flex justify-between items-start mb-3">
        <span className="text-slate-400 uppercase tracking-wider text-[10px] font-medium">{title}</span>
        <div className="p-1.5 bg-slate-950 rounded border border-slate-800/50">
          {icon}
        </div>
      </div>
      <div className="flex items-end justify-between">
        <span className="text-xl font-bold text-slate-100">{value}</span>
        <div className={`flex items-center font-medium text-[10px] ${
          status === 'critical' ? 'text-rose-400' : 
          status === 'warning' ? 'text-amber-400' : 'text-emerald-400'
        }`}>
          {isPositive ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
          {trend}
        </div>
      </div>
    </div>
  );
};

const SupplierRow = ({ id, region, score, vol, lead, status }) => {
  const numericScore = Number(score);
  return (
    <tr className="border-b border-slate-800/30 hover:bg-slate-800/30 transition-colors">
      <td className="py-2.5 px-2 font-medium text-cyan-400">{id}</td>
      <td className="py-2.5 px-2 text-slate-400">{region}</td>
      <td className="py-2.5 px-2">
        <div className="flex items-center gap-2">
          <span className={`w-6 text-right ${numericScore > 80 ? 'text-rose-400' : numericScore > 60 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {score}
          </span>
          <div className="w-16 h-1.5 bg-[#0B1120] rounded-full overflow-hidden border border-slate-800">
            <div 
              className={`h-full ${numericScore > 80 ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]' : numericScore > 60 ? 'bg-amber-500' : 'bg-emerald-500'}`} 
              style={{ width: `${score}%` }}
            ></div>
          </div>
        </div>
      </td>
      <td className="py-2.5 px-2 text-slate-300">{vol}</td>
      <td className="py-2.5 px-2 text-slate-300">{lead}</td>
      <td className="py-2.5 px-2">
        <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium uppercase tracking-wide border ${
          status === 'Critical' ? 'bg-rose-950/50 text-rose-400 border-rose-900/50' :
          status === 'Warning' ? 'bg-amber-950/50 text-amber-400 border-amber-900/50' :
          'bg-emerald-950/50 text-emerald-400 border-emerald-900/50'
        }`}>
          {status}
        </span>
      </td>
    </tr>
  );
};

const DisruptionItem = ({ node, impact, severity, cause }) => {
  return (
    <div className="bg-[#0B1120] p-2.5 rounded border border-slate-800/80 flex flex-col gap-2 hover:border-slate-700 transition-colors group">
      <div className="flex justify-between items-center">
        <span className="font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors">{node}</span>
        <span className={`text-[9px] px-1.5 py-0.5 rounded uppercase font-semibold tracking-wider ${
          severity === 'critical' ? 'bg-rose-950 text-rose-400 border border-rose-900/50' :
          severity === 'high' ? 'bg-orange-950 text-orange-400 border border-orange-900/50' :
          severity === 'medium' ? 'bg-amber-950 text-amber-400 border border-amber-900/50' :
          'bg-slate-900 text-slate-400 border border-slate-800'
        }`}>{severity}</span>
      </div>
      <div className="flex justify-between items-center text-[10px] text-slate-400">
        <span className="truncate mr-2">Cause: <span className="text-slate-300">{cause}</span></span>
        <span className="text-violet-400 font-semibold bg-violet-950/50 px-1.5 py-0.5 rounded border border-violet-900/30 whitespace-nowrap">
          {impact}
        </span>
      </div>
    </div>
  );
};

export default RiskHub;