/**
 * Step Helper Component
 * 
 * Shows contextual help and instructions for each step
 */

import React, { useState } from 'react';

interface StepHelperProps {
  title: string;
  content: string | React.ReactNode;
  type?: 'info' | 'tip' | 'warning';
  defaultOpen?: boolean;
}

const StepHelper: React.FC<StepHelperProps> = ({ 
  title, 
  content, 
  type = 'info',
  defaultOpen = false 
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  const colors = {
    info: {
      bg: '#eff6ff',  // Mais claro (quase branco)
      border: '#2563eb',
      text: '#1e40af',  // Azul escuro forte
      headerBg: '#dbeafe',  // Azul médio para o header
      icon: 'ℹ️'
    },
    tip: {
      bg: '#faf5ff',  // Mais claro (quase branco)
      border: '#7c3aed',
      text: '#6b21a8',  // Roxo escuro forte
      headerBg: '#e9d5ff',  // Roxo médio para o header
      icon: '💡'
    },
    warning: {
      bg: '#fffbeb',  // Mais claro (quase branco)
      border: '#f59e0b',
      text: '#92400e',  // Laranja escuro
      headerBg: '#fef3c7',  // Amarelo para o header
      icon: '⚠️'
    }
  };
  
  const colorScheme = colors[type];
  
  return (
    <div style={{
      border: `2px solid ${colorScheme.border}`,
      borderRadius: 'var(--radius-md)',
      marginBottom: 'var(--spacing-lg)',
      overflow: 'hidden',
      backgroundColor: 'white'
    }}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--spacing-md)',
          background: colorScheme.headerBg,
          border: 'none',
          cursor: 'pointer',
          fontSize: 'var(--font-size-md)',
          fontWeight: '600',
          color: colorScheme.text,
          textAlign: 'left'
        }}
      >
        <span>
          {colorScheme.icon} {title}
        </span>
        <span style={{ fontSize: 'var(--font-size-lg)' }}>
          {isOpen ? '▼' : '▶'}
        </span>
      </button>
      
      {isOpen && (
        <div style={{
          padding: 'var(--spacing-md)',
          fontSize: 'var(--font-size-sm)',
          lineHeight: '1.6',
          color: colorScheme.text,
          backgroundColor: colorScheme.bg
        }}>
          {typeof content === 'string' ? <p style={{ margin: 0 }}>{content}</p> : content}
        </div>
      )}
    </div>
  );
};

export default StepHelper;

