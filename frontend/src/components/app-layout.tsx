'use client';

import React, { useState } from 'react';
import { Sidebar } from './sidebar';
import { Header } from './header';
import { usePathname } from 'next/navigation';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const activeView = pathname.split('/').pop() || 'dashboard';

  // Calculate dynamic width: 
  // Expanded: 8(p) + 64(rail) + 8(gap) + 288(detail) + 8(p) = 376px
  // Collapsed: 8(p) + 64(rail) + 8(gap) + 64(detail) + 8(p) = 152px
  const sidebarWidth = isSidebarCollapsed ? 152 : 376;

  return (
    <div className="app-shell min-h-screen bg-black">
      {/* Sidebar - Fixed Dual Panel */}
      <Sidebar isCollapsed={isSidebarCollapsed} onToggleCollapse={setIsSidebarCollapsed} />

      {/* Main Content Area */}
      <div 
        className="app-main min-h-screen transition-all duration-500" 
        style={{ marginLeft: `${sidebarWidth}px` }}
      >
        {/* Sticky Header */}
        <Header activeView={activeView} />

        {/* Page Content */}
        <main className="app-content flex-1 overflow-y-auto bg-neutral-950/50 rounded-tl-[2.5rem] border-t border-l border-neutral-800/50 min-h-[calc(100vh-64px)] shadow-2xl">
          <div className="p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
