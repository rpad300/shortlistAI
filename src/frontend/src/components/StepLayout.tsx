/**
 * Step Layout Component
 * 
 * Wrapper for step pages that adds Navbar, Footer, and AnimatedBackground
 * without breaking existing step logic.
 */

import React from 'react';
import Navbar from './Navbar';
import AnimatedBackground from './AnimatedBackground';
import './StepLayout.css';

interface StepLayoutProps {
  children: React.ReactNode;
}

export const StepLayout: React.FC<StepLayoutProps> = ({ children }) => {
  return (
    <>
      <AnimatedBackground intensity="low" />
      
      <div className="step-layout">
        <Navbar />
        
        <main className="step-layout-main">
          {children}
        </main>

        {/* Optional: Add minimal footer or back link */}
        <div className="step-layout-footer">
          <a href="/" className="step-back-home">
            ← Back to Home
          </a>
        </div>
      </div>
    </>
  );
};

export default StepLayout;


