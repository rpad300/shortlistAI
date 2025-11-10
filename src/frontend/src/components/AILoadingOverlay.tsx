/**
 * AI Loading Overlay
 * 
 * Shows when AI is processing with animated progress
 */

import React, { useEffect, useState } from 'react';

interface AILoadingOverlayProps {
  isVisible: boolean;
  message?: string;
  estimatedSeconds?: number;
}

const AILoadingOverlay: React.FC<AILoadingOverlayProps> = ({ 
  isVisible, 
  message = 'AI is analyzing...',
  estimatedSeconds = 30
}) => {
  const [progress, setProgress] = useState(0);
  const [dots, setDots] = useState('');
  
  useEffect(() => {
    if (!isVisible) {
      setProgress(0);
      return;
    }
    
    // Simulate progress (not real, just visual feedback)
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return 95; // Cap at 95% until actually done
        return prev + (100 - prev) * 0.1; // Asymptotic approach
      });
    }, 1000);
    
    // Animated dots
    const dotsInterval = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return '';
        return prev + '.';
      });
    }, 500);
    
    return () => {
      clearInterval(interval);
      clearInterval(dotsInterval);
    };
  }, [isVisible]);
  
  if (!isVisible) return null;
  
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{
        backgroundColor: 'var(--color-bg-primary)',
        padding: 'var(--spacing-xl)',
        borderRadius: 'var(--radius-lg)',
        maxWidth: '500px',
        width: '90%',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        textAlign: 'center'
      }}>
        {/* AI Icon Animation */}
        <div style={{
          fontSize: '64px',
          marginBottom: 'var(--spacing-lg)',
          animation: 'pulse 2s ease-in-out infinite'
        }}>
          🤖
        </div>
        
        {/* Message */}
        <h2 style={{ 
          marginBottom: 'var(--spacing-md)',
          color: 'var(--color-text-primary)'
        }}>
          {message}{dots}
        </h2>
        
        {/* Progress Bar */}
        <div style={{
          width: '100%',
          height: '8px',
          backgroundColor: 'var(--color-bg-secondary)',
          borderRadius: '4px',
          overflow: 'hidden',
          marginBottom: 'var(--spacing-md)'
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            backgroundColor: 'var(--color-accent-primary)',
            transition: 'width 0.5s ease-out',
            borderRadius: '4px'
          }} />
        </div>
        
        {/* Progress Text */}
        <p style={{ 
          fontSize: 'var(--font-size-sm)',
          color: 'var(--color-text-secondary)',
          marginBottom: 'var(--spacing-sm)'
        }}>
          {Math.round(progress)}% complete
        </p>
        
        <p style={{ 
          fontSize: 'var(--font-size-xs)',
          color: 'var(--color-text-secondary)'
        }}>
          This may take {estimatedSeconds} seconds. Please wait...
        </p>
        
        <style>{`
          @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.8; }
          }
        `}</style>
      </div>
    </div>
  );
};

export default AILoadingOverlay;

