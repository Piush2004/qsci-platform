import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Activity, BarChart2, Box, Command, Settings, ShieldAlert, GitBranch, Database, Cpu, MessageSquare, Search, Bell, User, LayoutDashboard, Truck, Zap, TestTube2 } from "lucide-react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "QSCI Enterprise Decision Intelligence",
  description: "Hybrid Classical-Quantum Supply Chain Decision Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#0A0F1C] text-[#F8FAFC] min-h-screen flex flex-col font-sans`}>
        
        {/* GLOBAL HEADER / CONTEXT BAR */}
        <header className="h-14 border-b border-[#1F2937] bg-[#111827] flex items-center justify-between px-4 z-50 sticky top-0">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2 font-bold tracking-tight text-white hover:text-[#06B6D4] transition-colors">
              <Command className="text-[#06B6D4] w-5 h-5" />
              <span>QSCI</span>
            </Link>
            
            <div className="hidden md:flex items-center bg-[#0A0F1C] border border-[#1F2937] rounded-md px-3 py-1.5 text-sm text-[#CBD5E1]">
              <Search className="w-4 h-4 mr-2 text-[#64748B]" />
              <span className="opacity-50 mr-8">Search anything...</span>
              <kbd className="text-[10px] bg-[#1F2937] px-1.5 py-0.5 rounded text-[#CBD5E1]">⌘K</kbd>
            </div>
          </div>

          {/* GLOBAL CONTEXT */}
          <div className="hidden lg:flex items-center gap-4 text-xs text-[#CBD5E1] bg-[#0A0F1C] border border-[#1F2937] rounded-md px-4 py-1.5">
            <span className="flex gap-1">Dataset: <span className="text-white font-mono">M5</span></span>
            <span className="text-[#1F2937]">|</span>
            <span className="flex gap-1">Region: <span className="text-white">California</span></span>
            <span className="text-[#1F2937]">|</span>
            <span className="flex gap-1">Horizon: <span className="text-[#06B6D4]">28 Days</span></span>
            <span className="text-[#1F2937]">|</span>
            <span className="flex gap-1">Model: <span className="text-[#8B5CF6]">Hybrid-Ensemble</span></span>
          </div>

          <div className="flex items-center gap-4">
            <button className="text-[#CBD5E1] hover:text-white transition-colors">
              <Bell className="w-5 h-5" />
            </button>
            <button className="w-8 h-8 rounded-full bg-[#1F2937] flex items-center justify-center text-sm border border-[#06B6D4]/30 hover:border-[#06B6D4] transition-colors">
              <User className="w-4 h-4" />
            </button>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          {/* COLLAPSIBLE SIDEBAR */}
          <aside className="w-64 border-r border-[#1F2937] bg-[#0A0F1C] flex-col hidden md:flex overflow-y-auto">
            <nav className="flex-1 p-4 space-y-1">
              <div className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase mb-2 px-3">Decision Engine</div>
              <Link href="/dashboard" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <LayoutDashboard size={18} /> Decision Center
              </Link>
              <Link href="/demand" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <BarChart2 size={18} /> Demand
              </Link>
              <Link href="/inventory" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <Box size={18} /> Inventory
              </Link>
              <Link href="/risk" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <ShieldAlert size={18} /> Risk
              </Link>
              <Link href="/optimization" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <Zap size={18} /> Optimization
              </Link>
              <Link href="/operations" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <Truck size={18} /> Operations
              </Link>
              
              <div className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase mt-6 mb-2 px-3">Intelligence</div>
              <Link href="/scenarios" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <GitBranch size={18} /> Scenarios
              </Link>
              <Link href="/copilot" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <MessageSquare size={18} /> Copilot
              </Link>
              <Link href="/research" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <TestTube2 size={18} /> Research Lab
              </Link>

              <div className="text-[10px] font-bold tracking-wider text-[#64748B] uppercase mt-6 mb-2 px-3">Infrastructure</div>
              <Link href="/models" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <Cpu size={18} /> Models
              </Link>
              <Link href="/data" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <Database size={18} /> Data Hub
              </Link>
              <Link href="/settings" className="flex items-center gap-3 px-3 py-2 hover:bg-[#111827] rounded-md text-sm font-medium text-[#CBD5E1] hover:text-white transition-colors">
                <Settings size={18} /> Settings
              </Link>
            </nav>
          </aside>
          
          <main className="flex-1 overflow-auto bg-[#0A0F1C]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
