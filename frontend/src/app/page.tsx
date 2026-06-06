'use client';

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { FileUp, Link as LinkIcon, Type, ArrowRight, Database } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'upload' | 'link' | 'text'>('link');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // Navigate to the analysis page with the new session_id
        router.push(`/analysis/${data.session_id}`);
      } else {
        console.error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="dashboard-page min-h-[calc(100vh-52px)] flex flex-col items-center justify-center p-8 bg-[#0A0A0B]">
      <div className="max-w-3xl w-full space-y-12">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center gap-2"
          >
            <div className="w-2 h-2 rounded-full bg-white/20" />
            <span className="text-[10px] font-mono tracking-[0.2em] text-text-tertiary uppercase">
              Exodus AI — Data Intelligence
            </span>
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-6xl font-serif text-white tracking-tight leading-[1.1]"
          >
            What are you <br />
            <span className="italic opacity-80">analyzing today?</span>
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-text-secondary max-w-xl mx-auto leading-relaxed"
          >
            Upload a spreadsheet, drop a CSV, or link a data source. We surface insights, identify trends, and generate native Excel reports instantly.
          </motion.p>
        </div>

        {/* Input Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-[#111113] border border-[#2E2E34] rounded-2xl overflow-hidden shadow-2xl"
        >
          {/* Tabs */}
          <div className="flex border-b border-[#232327]">
            <TabButton 
              active={activeTab === 'upload'} 
              onClick={() => setActiveTab('upload')} 
              icon={<FileUp size={16} />} 
              label="Upload Excel" 
            />
            <TabButton 
              active={activeTab === 'link'} 
              onClick={() => setActiveTab('link')} 
              icon={<LinkIcon size={16} />} 
              label="Link Source" 
            />
            <TabButton 
              active={activeTab === 'text'} 
              onClick={() => setActiveTab('text')} 
              icon={<Type size={16} />} 
              label="Paste Data" 
            />
          </div>

          {/* Content */}
          <div className="p-8">
            {activeTab === 'link' && (
              <div className="space-y-6">
                <div className="bg-[#18181B] border border-[#2E2E34] rounded-xl p-4">
                  <input 
                    type="text" 
                    placeholder="Paste data source URL (SharePoint, Google Sheets, etc.)..."
                    className="w-full bg-transparent border-none outline-none text-white placeholder:text-text-tertiary text-base font-sans"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-[10px] font-mono text-text-tertiary uppercase tracking-wider">
                    <span className="flex items-center gap-1.5"><ArrowRight size={10} /> Press Enter to Analyze</span>
                  </div>
                  <button className="bg-white text-black px-6 py-2 rounded-lg font-semibold text-sm hover:bg-white/90 transition-all flex items-center gap-2 group cursor-pointer">
                    Analyze <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'upload' && (
              <div 
                onClick={handleFileClick}
                className="border-2 border-dashed border-[#2E2E34] rounded-xl p-12 text-center space-y-4 hover:border-white/20 transition-colors cursor-pointer group"
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileChange} 
                  className="hidden" 
                  accept=".xlsx,.xls,.csv"
                />
                <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <FileUp className="text-white/60" size={24} />
                </div>
                <p className="text-text-secondary font-medium text-sm">
                  Click to upload or drag and drop <br />
                  <span className="text-text-tertiary font-normal">.xlsx, .csv, .xls up to 50MB</span>
                </p>
              </div>
            )}

            {activeTab === 'text' && (
              <div className="space-y-6">
                <textarea 
                  placeholder="Paste raw data or table content here..."
                  className="w-full bg-[#18181B] border border-[#2E2E34] rounded-xl p-4 min-h-[160px] outline-none text-white placeholder:text-text-tertiary text-base font-sans resize-none"
                />
                <div className="flex justify-end">
                  <button className="bg-white text-black px-6 py-2 rounded-lg font-semibold text-sm hover:bg-white/90 transition-all cursor-pointer">
                    Analyze Data
                  </button>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Footer info */}
        <div className="flex justify-center gap-8 text-[10px] font-mono text-text-tertiary uppercase tracking-[0.15em]">
          <span className="flex items-center gap-2"><Database size={10} /> Cloud Secure</span>
          <span className="flex items-center gap-2"><ArrowRight size={10} /> Real-time Analysis</span>
          <span className="flex items-center gap-2"><Type size={10} /> Multi-format Support</span>
        </div>
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) {
  return (
    <button 
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-4 text-sm font-medium transition-all border-b-2 cursor-pointer ${
        active 
          ? 'text-white border-white bg-white/[0.02]' 
          : 'text-text-tertiary border-transparent hover:text-text-secondary'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
