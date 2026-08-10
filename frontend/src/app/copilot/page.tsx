"use client";

import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Database, 
  Share2, 
  Sparkles, 
  Activity, 
  FileText,
  MessageSquare,
  Search,
  Settings,
  MoreVertical,
  Network
} from 'lucide-react';

// --- Types ---
type MessageRole = 'user' | 'assistant';

interface KnowledgeGraphNode {
  id: string;
  label: string;
  type: string;
}

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  knowledgeGraphContext?: KnowledgeGraphNode[];
  timestamp: Date;
}

// --- Mock Data ---
const MOCK_CHAT_HISTORY: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: 'Welcome to the QSCI Copilot. I can help you query supply chain data, analyze supplier risks, and visualize network dependencies. How can I assist you today?',
    timestamp: new Date(Date.now() - 3600000),
  },
  {
    id: '2',
    role: 'user',
    content: 'What is the current risk exposure for our semiconductor components in Taiwan?',
    timestamp: new Date(Date.now() - 3500000),
  },
  {
    id: '3',
    role: 'assistant',
    content: 'Based on current supply chain telemetry, your risk exposure for semiconductor components in Taiwan is currently assessed as **HIGH**. \n\nRecent disruptions at the Kaohsiung port facility have delayed 3 major shipments (Shipment IDs: SHP-9021, SHP-9022, SHP-9025). Furthermore, our predictive model indicates a 65% probability of further delays over the next 14 days due to approaching weather systems.',
    knowledgeGraphContext: [
      { id: 'n1', label: 'Taiwan', type: 'Region' },
      { id: 'n2', label: 'Semiconductors', type: 'Category' },
      { id: 'n3', label: 'Kaohsiung Port', type: 'Facility' },
      { id: 'n4', label: 'Weather Risk', type: 'Factor' },
    ],
    timestamp: new Date(Date.now() - 3490000),
  }
];

export default function CopilotHubPage() {
  const [messages, setMessages] = useState<Message[]>(MOCK_CHAT_HISTORY);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim()) return;

    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I have analyzed the query. The requested data has been aggregated from our ERP and external risk intelligence sources. The supply network remains robust, though localized bottlenecks are emerging in tier-2 supplier lead times.',
        knowledgeGraphContext: [
          { id: 'n5', label: 'ERP Data', type: 'Source' },
          { id: 'n6', label: 'Tier-2 Suppliers', type: 'Entity' }
        ],
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-200 font-sans overflow-hidden">
      
      {/* Sidebar - Chat History & Tools */}
      <aside className="w-80 border-r border-slate-800/60 bg-slate-950/50 flex flex-col">
        <div className="p-4 border-b border-slate-800/60 flex items-center justify-between">
          <div className="flex items-center gap-2 text-cyan-400">
            <Network className="w-5 h-5" />
            <h2 className="font-semibold tracking-wide">QSCI Copilot</h2>
          </div>
          <button className="p-1.5 hover:bg-slate-800 rounded-md transition-colors text-slate-400">
            <Settings className="w-4 h-4" />
          </button>
        </div>

        <div className="p-3">
          <button className="w-full flex items-center gap-2 px-3 py-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 rounded-md border border-cyan-500/20 transition-all text-sm font-medium">
            <MessageSquare className="w-4 h-4" />
            New Analysis Session
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Recent Sessions</h3>
            <ul className="space-y-1">
              <li className="px-2 py-1.5 rounded bg-slate-800/40 text-slate-300 text-sm cursor-pointer border-l-2 border-cyan-500">
                Semiconductor Risk Taiwan
              </li>
              <li className="px-2 py-1.5 rounded hover:bg-slate-800/40 text-slate-400 text-sm cursor-pointer transition-colors">
                Q3 Logistics Cost Variance
              </li>
              <li className="px-2 py-1.5 rounded hover:bg-slate-800/40 text-slate-400 text-sm cursor-pointer transition-colors">
                Supplier ESG Compliance
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Data Sources Connected</h3>
            <div className="space-y-2 px-2">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Database className="w-3.5 h-3.5 text-violet-400" />
                <span>Global ERP Sync</span>
                <span className="ml-auto w-2 h-2 rounded-full bg-emerald-500"></span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Activity className="w-3.5 h-3.5 text-cyan-400" />
                <span>Live Telemetry API</span>
                <span className="ml-auto w-2 h-2 rounded-full bg-emerald-500"></span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
        
        {/* Header */}
        <header className="h-14 border-b border-slate-800/60 flex items-center px-6 justify-between bg-slate-950/80 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-100">Supply Chain Intelligence Copilot</h1>
              <p className="text-[11px] text-slate-400">Model: QSCI-Alpha-v2 • Infrastructure Mode</p>
            </div>
          </div>
          <button className="text-slate-400 hover:text-slate-200 transition-colors">
            <MoreVertical className="w-5 h-5" />
          </button>
        </header>

        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
          <div className="max-w-4xl mx-auto space-y-8 pb-10">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className="flex-shrink-0 mt-1">
                  {msg.role === 'assistant' ? (
                    <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400 shadow-sm">
                      <Bot className="w-5 h-5" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded bg-violet-500/20 border border-violet-500/30 flex items-center justify-center text-violet-400 shadow-sm">
                      <User className="w-5 h-5" />
                    </div>
                  )}
                </div>

                {/* Message Bubble */}
                <div className={`flex flex-col gap-2 max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`px-5 py-3.5 rounded-xl shadow-sm text-[15px] leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-slate-800/80 text-slate-200 border border-slate-700/50' 
                      : 'bg-transparent text-slate-300'
                  }`}>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                  
                  {/* Knowledge Graph Context Cards (Only for Assistant) */}
                  {msg.knowledgeGraphContext && msg.knowledgeGraphContext.length > 0 && (
                    <div className="mt-2 w-full p-4 rounded-lg bg-slate-900/60 border border-slate-800/80 shadow-inner">
                      <div className="flex items-center gap-2 mb-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">
                        <Share2 className="w-3.5 h-3.5" />
                        Knowledge Graph Context Extract
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {msg.knowledgeGraphContext.map((node) => (
                          <div key={node.id} className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-xs">
                            <span className="text-violet-400">{node.type}:</span>
                            <span className="text-slate-300 font-medium">{node.label}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <span className="text-[10px] text-slate-500 mt-1 px-1">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-4 flex-row">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400">
                    <Bot className="w-5 h-5" />
                  </div>
                </div>
                <div className="flex items-center px-5 py-4 rounded-xl bg-transparent">
                  <div className="flex space-x-1.5">
                    <div className="w-2 h-2 rounded-full bg-cyan-500/50 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 rounded-full bg-cyan-500/50 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 rounded-full bg-cyan-500/50 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 bg-slate-950/80 backdrop-blur-md border-t border-slate-800/60">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={handleSendMessage} className="relative flex items-end shadow-lg shadow-black/20 rounded-xl bg-slate-900 border border-slate-700/60 focus-within:border-cyan-500/50 focus-within:ring-1 focus-within:ring-cyan-500/20 transition-all">
              <div className="p-3 text-slate-500 hover:text-slate-300 cursor-pointer transition-colors">
                <FileText className="w-5 h-5" />
              </div>
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Query supply chain anomalies, request summaries, or explore network graphs..."
                className="w-full max-h-32 min-h-[52px] bg-transparent text-slate-200 placeholder-slate-500 resize-none py-3.5 focus:outline-none text-[15px] leading-relaxed"
                rows={1}
              />
              <div className="p-2.5">
                <button
                  type="submit"
                  disabled={!inputValue.trim() || isTyping}
                  className="p-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:hover:bg-cyan-600 text-white transition-colors flex items-center justify-center shadow-md shadow-cyan-900/50"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>
            <div className="text-center mt-2">
               <span className="text-[10px] text-slate-500">QSCI Copilot can make mistakes. Verify critical supply chain insights.</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}