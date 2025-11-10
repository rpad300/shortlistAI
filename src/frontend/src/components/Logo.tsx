/**
 * Logo Component
 * 
 * Adaptive logo that changes based on theme (light/dark).
 * Uses color logo for light mode, white logo for dark mode.
 */

import React, { useEffect, useState } from 'react';
import './Logo.css';

interface LogoProps {
  width?: number;
  height?: number;
  variant?: 'auto' | 'color' | 'white' | 'black';
  className?: string;
}

export const Logo: React.FC<LogoProps> = ({
  width = 160,
  height = 40,
  variant = 'auto',
  className = ''
}) => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check current theme
    const checkTheme = () => {
      const dataTheme = document.documentElement.getAttribute('data-theme');
      if (dataTheme === 'dark') {
        setIsDark(true);
      } else if (dataTheme === 'light') {
        setIsDark(false);
      } else {
        // Auto - check system preference
        setIsDark(window.matchMedia('(prefers-color-scheme: dark)').matches);
      }
    };

    checkTheme();

    // Watch for theme changes
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });

    // Watch for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (!document.documentElement.getAttribute('data-theme')) {
        checkTheme();
      }
    };
    mediaQuery.addEventListener('change', handleChange);

    return () => {
      observer.disconnect();
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  // Determine which logo to use
  const getLogoSrc = () => {
    if (variant === 'color') {
      return '/assets/logos/shortlistai-full-color.svg';
    }
    if (variant === 'white') {
      return '/assets/logos/shortlistai-monochrome-white.svg';
    }
    if (variant === 'black') {
      return '/assets/logos/shortlistai-monochrome-black.svg';
    }
    // Auto - choose based on theme
    return isDark 
      ? '/assets/logos/shortlistai-monochrome-white.svg'
      : '/assets/logos/shortlistai-full-color.svg';
  };

  return (
    <img 
      src={getLogoSrc()}
      alt="ShortlistAI" 
      width={width}
      height={height}
      className={`logo ${className}`}
    />
  );
};

export default Logo;
