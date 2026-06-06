'use client';

import React from 'react';
import { MessageSquare } from 'lucide-react';

interface HeaderProps {
  activeView: string;
}

const viewLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  overview: 'Overview',
  clauses: 'Clauses',
  reports: 'Reports',
  compare: 'Compare',
  settings: 'Settings',
};

export function Header({ activeView }: HeaderProps) {
  const isDark = true; // Hardcoded for now

  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'compare', label: 'Compare' },
    { id: 'settings', label: 'Settings' },
  ];

  return (
    <header className="desktop-header" style={{
      position: 'sticky',
      top: 0,
      height: '52px',
      background: isDark ? 'rgba(10,10,11,0.85)' : 'rgba(250,250,250,0.85)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: `1px solid ${isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.06)'}`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'between',
      padding: '0 24px',
      zIndex: 20,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px', width: '100%', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          {/* Breadcrumb */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontFamily: 'var(--font-sans)',
            fontSize: '13px',
          }}>
            <span style={{ color: 'var(--text-tertiary)', fontWeight: '500' }}>Exodus</span>
            <span style={{ color: 'var(--text-tertiary)', fontSize: '10px' }}>/</span>
            <span style={{
              color: 'var(--text-primary)',
              fontWeight: '500',
            }}>{viewLabels[activeView] || 'Dashboard'}</span>
          </div>

          {/* Navigation */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
            {navItems.map(item => {
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '13px',
                    fontWeight: '500',
                    border: 'none',
                    background: 'transparent',
                    color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                  className="hover:text-white"
                >
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            type="button"
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              border: `1px solid var(--border-default)`,
              background: 'transparent',
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'background 0.18s ease, border-color 0.18s ease, color 0.18s ease',
            }}
          >
            <MessageSquare size={17} />
          </button>
        </div>
      </div>
    </header>
  );
}
