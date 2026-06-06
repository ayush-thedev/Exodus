'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  Bot, 
  User, 
  Terminal, 
  Table as TableIcon, 
  BarChart3, 
  Download, 
  RefreshCw,
  AlertCircle,
  FileSpreadsheet
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  msg_type?: string;
  metadata?: any;
  created_at?: string;
}

export default function AnalysisPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    fetchMessages();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchMessages = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}/messages`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue;
    setInputValue('');
    
    // Optimistic update
    const newUserMsg: Message = { role: 'user', content: userMessage };
    setMessages(prev => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/api/chat/${sessionId}?message=${encodeURIComponent(userMessage)}`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, data]);
      } else {
        const errorMsg: Message = { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error while processing your request.', 
          msg_type: 'error' 
        };
        setMessages(prev => [...prev, errorMsg]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const chartMessages = messages.filter(m => m.metadata?.fig_base64);

  const handleExport = () => {
    const a = document.createElement('a');
    a.href = `http://localhost:8000/api/export/${sessionId}`;
    a.download = `exodus_report_${sessionId}.xlsx`;
    a.click();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-6xl mx-auto gap-6">
      {/* Header Info */}
      <div className="flex items-center justify-between bg-neutral-900/40 border border-neutral-800/50 p-4 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center border border-neutral-800">
            <FileSpreadsheet className="text-neutral-400" size={20} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Analysis Session</h2>
            <p className="text-[10px] font-mono text-neutral-500 uppercase tracking-wider">{sessionId}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-neutral-800 rounded-lg text-neutral-400 transition-colors cursor-pointer">
            <RefreshCw size={16} />
          </button>
          <button 
            onClick={handleExport}
            className="bg-white text-black px-4 py-1.5 rounded-lg text-xs font-semibold hover:bg-neutral-200 transition-colors flex items-center gap-2 cursor-pointer"
          >
            <Download size={14} /> Export Results
          </button>
        </div>
      </div>

      <div className="flex-1 flex gap-6 min-h-0">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-neutral-900/40 border border-neutral-800/50 rounded-[2rem] overflow-hidden backdrop-blur-sm shadow-2xl">
          <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
            <AnimatePresence initial={false}>
              {messages.map((msg, idx) => (
                <ChatMessage key={idx} message={msg} />
              ))}
            </AnimatePresence>
            {isLoading && (
              <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                className="flex gap-4"
              >
                <div className="w-8 h-8 rounded-lg bg-neutral-800 flex items-center justify-center shrink-0">
                  <Bot size={16} className="text-neutral-500 animate-pulse" />
                </div>
                <div className="space-y-2 pt-1">
                  <div className="h-4 w-48 bg-neutral-800/50 rounded animate-pulse" />
                  <div className="h-4 w-32 bg-neutral-800/50 rounded animate-pulse" />
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-6 bg-neutral-950/50 border-t border-neutral-800/50">
            <div className="relative group">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask me to analyze trends, generate charts, or clean data..."
                className="w-full bg-neutral-900 border border-neutral-800/80 rounded-2xl p-4 pr-16 min-h-[60px] max-h-[200px] outline-none text-neutral-200 placeholder:text-neutral-600 focus:border-white/20 transition-all resize-none shadow-inner"
              />
              <button 
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="absolute right-3 bottom-3 p-2.5 bg-white text-black rounded-xl hover:bg-neutral-200 disabled:opacity-30 disabled:hover:bg-white transition-all cursor-pointer shadow-lg"
              >
                <Send size={18} />
              </button>
            </div>
            <p className="mt-3 text-[10px] text-neutral-600 text-center uppercase tracking-widest font-mono">
              Press Enter to send — Shift+Enter for new line
            </p>
          </div>
        </div>

        {/* Info Panel */}
        <div className="w-80 flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-2">
          <div className="bg-neutral-900/40 border border-neutral-800/50 rounded-2xl p-5 space-y-4 shadow-xl">
            <div className="flex items-center gap-2 mb-2">
              <TableIcon size={16} className="text-neutral-400" />
              <h3 className="text-xs font-bold text-neutral-300 uppercase tracking-widest">Dataset Overview</h3>
            </div>
            {messages.length > 0 && messages[0].metadata?.df_metadata ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <StatCard label="Rows" value={messages[0].metadata.df_metadata.row_count} />
                  <StatCard label="Cols" value={messages[0].metadata.df_metadata.column_count} />
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] text-neutral-500 font-medium">Columns Detected</span>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {messages[0].metadata.df_metadata.columns.map((col: string) => (
                      <span key={col} className="px-2 py-0.5 bg-neutral-800/50 border border-neutral-700/50 rounded text-[10px] text-neutral-400 font-mono">
                        {col}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-neutral-600 italic">No data loaded yet</p>
            )}
          </div>

          <div className="bg-neutral-900/40 border border-neutral-800/50 rounded-2xl p-5 space-y-4 shadow-xl flex-1 flex flex-col min-h-0">
            <div className="flex items-center gap-2 mb-2 shrink-0">
              <BarChart3 size={16} className="text-neutral-400" />
              <h3 className="text-xs font-bold text-neutral-300 uppercase tracking-widest">Active Insights</h3>
            </div>
            {chartMessages.length > 0 ? (
              <div className="flex-1 overflow-y-auto pr-1 space-y-4 custom-scrollbar">
                {chartMessages.map((msg, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="w-full rounded-xl overflow-hidden border border-neutral-800 bg-white">
                      <img src={`data:image/png;base64,${msg.metadata.fig_base64}`} alt={`Insight ${idx + 1}`} className="w-full h-auto object-contain hover:scale-105 transition-transform duration-300" />
                    </div>
                    <p className="text-[10px] text-neutral-500 font-mono">Insight {idx + 1} • {new Date(msg.created_at || Date.now()).toLocaleTimeString()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 border border-dashed border-neutral-800 rounded-xl flex flex-col items-center justify-center text-center gap-3">
                <AlertCircle size={20} className="text-neutral-700" />
                <p className="text-[11px] text-neutral-600 leading-relaxed">
                  Start a conversation to generate visualizations and reports.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string, value: any }) {
  return (
    <div className="bg-neutral-950/50 border border-neutral-800/50 p-3 rounded-xl">
      <div className="text-[10px] text-neutral-500 font-medium mb-1">{label}</div>
      <div className="text-lg font-serif text-white">{value}</div>
    </div>
  );
}

function ChatMessage({ message }: { message: Message }) {
  const isAssistant = message.role === 'assistant';
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 ${isAssistant ? '' : 'flex-row-reverse'}`}
    >
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${
        isAssistant 
          ? 'bg-neutral-900 border-neutral-800 text-white' 
          : 'bg-white border-white text-black'
      }`}>
        {isAssistant ? <Bot size={16} /> : <User size={16} />}
      </div>
      
      <div className={`flex flex-col gap-2 max-w-[85%] ${isAssistant ? '' : 'items-end'}`}>
        <div className={`rounded-2xl px-5 py-3 text-sm leading-relaxed ${
          isAssistant 
            ? 'bg-neutral-800/30 text-neutral-200 border border-neutral-800/50' 
            : 'bg-neutral-800 text-white shadow-lg'
        }`}>
          {message.content}
        </div>
        
        {message.metadata?.generated_code && (
          <div className="w-full bg-[#050505] border border-neutral-800 rounded-xl overflow-hidden mt-2">
            <div className="flex items-center gap-2 px-3 py-2 bg-neutral-900 border-b border-neutral-800">
              <Terminal size={12} className="text-neutral-500" />
              <span className="text-[10px] font-mono text-neutral-400">analysis_script.py</span>
            </div>
            <pre className="p-4 text-[11px] font-mono text-neutral-300 overflow-x-auto">
              <code>{message.metadata.generated_code}</code>
            </pre>
          </div>
        )}
        
        {message.metadata?.fig_base64 && (
          <div className="w-full mt-2 rounded-xl overflow-hidden border border-neutral-800 bg-white">
            <img src={`data:image/png;base64,${message.metadata.fig_base64}`} alt="Analysis Graph" className="w-full h-auto object-contain" />
          </div>
        )}
      </div>
    </motion.div>
  );
}
