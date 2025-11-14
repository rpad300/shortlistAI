/**
 * Modern Form Layout Component
 * 
 * Glassmorphism card layout for forms with animated background.
 * Provides consistent, modern design for all form pages.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import ThemeSwitcher from './ThemeSwitcher';
import LanguageSelector from './LanguageSelector';
import AnimatedBackground from './AnimatedBackground';
import './ModernFormLayout.css';

interface ModernFormLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  step?: string;
  totalSteps?: number;
  currentStep?: number;
  showLogo?: boolean;
}

export const ModernFormLayout: React.FC<ModernFormLayoutProps> = ({
  children,
  title,
  subtitle,
  step,
  totalSteps,
  currentStep,
  showLogo = true
}) => {
  return (
    <div className="modern-form-layout">
      <AnimatedBackground intensity="medium" />
      
      {/* Header */}
      <header className="modern-header">
        <div className="modern-header-left">
          {showLogo && (
            <Link to="/" className="modern-logo-link">
              <img 
                src="/assets/logos/shortlistai-full-color.svg" 
                alt="ShortlistAI" 
                className="modern-logo"
                width="140"
                height="35"
              />
            </Link>
          )}
        </div>
        
        <div className="modern-header-right">
          <LanguageSelector />
          <ThemeSwitcher />
        </div>
      </header>

      {/* Main Content */}
      <main className="modern-main">
        <div className="modern-container">
          {/* Progress Bar (if steps provided) */}
          {currentStep && totalSteps && (
            <div className="modern-progress-container">
              <div className="modern-progress-bar">
                <div 
                  className="modern-progress-fill"
                  style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                />
              </div>
              <div className="modern-progress-text">
                Step {currentStep} of {totalSteps}
              </div>
            </div>
          )}

          {/* Glass Card */}
          <div className="modern-glass-card">
            <div className="modern-card-header">
              {step && <div className="modern-step-badge">{step}</div>}
              <h1 className="modern-card-title">{title}</h1>
              {subtitle && <p className="modern-card-subtitle">{subtitle}</p>}
            </div>

            <div className="modern-card-content">
              {children}
            </div>
          </div>

          {/* Back to Home Link */}
          <div className="modern-footer-link">
            <Link to="/" className="link-home">
              ← Back to Home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ModernFormLayout;



