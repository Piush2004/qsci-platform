'use client';

import React, { useState } from 'react';
import {
  Package,
  TrendingUp,
  AlertTriangle,
  MapPin,
  ArrowRightLeft,
  Search,
  Filter,
  MoreVertical,
  ArrowUpRight,
  Boxes,
  Truck
} from 'lucide-react';
import Link from 'next/link';

// Mock Data
const inventorySummary = [
  { label: 'Total Inventory Value', value: '$42.5M', change: '+2.4%', icon: Boxes, color: 'text-cyan-400' },
  { label: 'Total Holding Costs', value: '$1.2M', change: '-5.1%', icon: TrendingUp, color: 'text-violet-400' },
  { label: 'Units In-Transit', value: '14,200', change: '+12%', icon: Truck, color: 'text-blue-400' },
  { label: 'Critical Exceptions', value: '3', change: 'Action Required', icon: AlertTriangle, color: 'text-rose-400', isAlert: true }
];

const warehouseData = [
  {
    id: 'WH-ALPHA',
    name: 'Warehouse Alpha',
    location: 'Chicago, IL',
    type: 'Primary Hub',
    stockLevel: '85%',
    holdingCost: '$45,000/mo',
    inTransit: 2400,
    status: 'Exception',
    exception: 'SKU-103 Stockout Predicted',
  },
  {
    id: 'WH-BETA',
    name: 'Warehouse Beta',
    location: 'Dallas, TX',
    type: 'Regional',
    stockLevel: '62%',
    holdingCost: '$28,000/mo',
    inTransit: 1100,
    status: 'Optimal',
  },
  {
    id: 'WH-GAMMA',
    name: 'Warehouse Gamma',
    location: 'Atlanta, GA',
    type: 'Regional',
    stockLevel: '94%',
    holdingCost: '$32,000/mo',
    inTransit: 500,
    status: 'Overstock Warning',
  },
  {
    id: 'NODE-X',
    name: 'Fulfillment Node X',
    location: 'Seattle, WA',
    type: 'Edge Node',
    stockLevel: '45%',
    holdingCost: '$12,000/mo',
    inTransit: 850,
    status: 'Optimal',
  }
];

export default function InventoryHub() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 md:p-8 font-sans">
      
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-semibold text-white flex items-center gap-2">
            <Package className="w-8 h-8 text-cyan-400" />
            Inventory Hub
          </h1>
          <p className="text-slate-400 mt-1 text-sm md:text-base">
            Multi-echelon routing & network stock levels
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm transition-colors flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filter View
          </button>
          <button className="px-4 py-2 bg-cyan-600/10 hover:bg-cyan-600/20 text-cyan-400 border border-cyan-500/30 rounded-lg text-sm transition-colors flex items-center gap-2">
            <ArrowRightLeft className="w-4 h-4" />
            Rebalance Network
          </button>
        </div>
      </header>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {inventorySummary.map((metric, idx) => (
          <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col relative overflow-hidden group hover:border-slate-700 transition-colors">
            {/* Subtle glow effect */}
            <div className={`absolute top-0 right-0 w-24 h-24 bg-current opacity-[0.02] rounded-full blur-xl -mr-10 -mt-10 ${metric.color}`}></div>
            
            <div className="flex items-start justify-between mb-4">
              <div className={`p-2 rounded-lg bg-slate-950 border border-slate-800 ${metric.color}`}>
                <metric.icon className="w-5 h-5" />
              </div>
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                metric.isAlert ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-slate-800 text-slate-300'
              }`}>
                {metric.change}
              </span>
            </div>
            <div>
              <p className="text-slate-400 text-sm">{metric.label}</p>
              <p className="text-2xl font-semibold text-white mt-1">{metric.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        
        {/* Table Toolbar */}
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h2 className="text-lg font-medium text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-violet-400" />
            Network Nodes
          </h2>
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text"
              placeholder="Search nodes, SKUs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-sm rounded-lg pl-9 pr-4 py-2 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all w-full sm:w-64"
            />
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/50 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                <th className="px-6 py-4 font-medium">Node Details</th>
                <th className="px-6 py-4 font-medium">Type</th>
                <th className="px-6 py-4 font-medium">Stock Level</th>
                <th className="px-6 py-4 font-medium">Holding Cost</th>
                <th className="px-6 py-4 font-medium">In-Transit</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-sm">
              {warehouseData.map((node) => (
                <tr key={node.id} className="hover:bg-slate-800/20 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="text-slate-200 font-medium">{node.name}</span>
                      <span className="text-slate-500 text-xs">{node.location} ({node.id})</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">
                    {node.type}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            parseInt(node.stockLevel) > 90 ? 'bg-amber-400' :
                            parseInt(node.stockLevel) < 50 ? 'bg-cyan-400' :
                            'bg-emerald-400'
                          }`}
                          style={{ width: node.stockLevel }}
                        />
                      </div>
                      <span className="text-slate-300">{node.stockLevel}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">
                    {node.holdingCost}
                  </td>
                  <td className="px-6 py-4 text-slate-300 flex items-center gap-1">
                    <Truck className="w-3.5 h-3.5 text-slate-500" />
                    {node.inTransit.toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    {node.status === 'Exception' ? (
                      <div className="flex flex-col gap-1">
                         <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium w-fit">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          Stockout Predicted
                        </span>
                        <span className="text-xs text-rose-300/70">{node.exception}</span>
                      </div>
                    ) : node.status === 'Overstock Warning' ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-medium w-fit">
                        Overcapacity
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium w-fit">
                        Optimal
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {node.status === 'Exception' ? (
                      <Link href="/decision-center" className="inline-flex items-center justify-center gap-1 px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-md text-xs transition-colors">
                        Resolve
                        <ArrowUpRight className="w-3 h-3" />
                      </Link>
                    ) : (
                      <button className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md transition-colors">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="p-4 border-t border-slate-800 bg-slate-950/30 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {warehouseData.length} nodes in the network</span>
          <div className="flex items-center gap-2">
            <button className="px-2 py-1 hover:text-slate-300 disabled:opacity-50">Previous</button>
            <button className="px-2 py-1 hover:text-slate-300 disabled:opacity-50">Next</button>
          </div>
        </div>

      </div>
    </div>
  );
}