/**
 * Theme Switcher Component
 * 
 * Modern toggle for light/dark mode with smooth transition and visual feedback.
 */

import React, { useState, useEffect } from 'react';
import './ThemeSwitcher.css';

export const ThemeSwitcher: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'auto'>('auto');
  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    // Load saved preference
    const saved = (localStorage.getItem('theme') as 'light' | 'dark' | 'auto') || 'auto';
    setTheme(saved);
    
    // Apply theme immediately on load
    const applyTheme = (themeValue: 'light' | 'dark' | 'auto') => {
      if (themeValue === 'auto') {
        // Remove manual override, use system preference
        document.documentElement.removeAttribute('data-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setEffectiveTheme(prefersDark ? 'dark' : 'light');
      } else {
        // Apply manual theme
        document.documentElement.setAttribute('data-theme', themeValue);
        setEffectiveTheme(themeValue);
      }
    };
    
    // Apply on load
    applyTheme(saved);
    
    // Listen to system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = () => {
      if (theme === 'auto') {
        setEffectiveTheme(mediaQuery.matches ? 'dark' : 'light');
      }
    };
    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, [theme]);

  const cycleTheme = () => {
    const next = theme === 'light' ? 'dark' : theme === 'dark' ? 'auto' : 'light';
    setTheme(next);
    localStorage.setItem('theme', next);
    
    // Apply theme immediately
    if (next === 'auto') {
      document.documentElement.removeAttribute('data-theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setEffectiveTheme(prefersDark ? 'dark' : 'light');
    } else {
      document.documentElement.setAttribute('data-theme', next);
      setEffectiveTheme(next);
    }
  };

  const getIcon = () => {
    if (theme === 'light') return '☀️';
    if (theme === 'dark') return '🌙';
    return '🔄'; // Auto
  };

  const getLabel = () => {
    if (theme === 'light') return 'Light';
    if (theme === 'dark') return 'Dark';
    return 'Auto';
  };

  return (
    <button 
      className={`theme-switcher theme-${effectiveTheme}`}
      onClick={cycleTheme}
      aria-label={`Current theme: ${getLabel()}. Click to change.`}
      title={`Theme: ${getLabel()} (click to cycle)`}
    >
      <span className="theme-icon">{getIcon()}</span>
      <span className="theme-label">{getLabel()}</span>
    </button>
  );
};

export default ThemeSwitcher;

