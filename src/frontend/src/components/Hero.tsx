/**
 * Hero Component with Light/Dark Mode Support
 * 
 * Enhanced hero with badges, stats, and improved visual impact.
 * Displays hero images that adapt to the user's color scheme preference.
 */

import React from 'react';
import './Hero.css';

interface HeroProps {
  title?: string;
  subtitle?: string;
  badge?: string;
  stats?: Array<{label: string; value: string}>;
  showImage?: boolean;
  className?: string;
}

export const Hero: React.FC<HeroProps> = ({
  title = 'ShortlistAI',
  subtitle = 'AI-Powered CV Analysis Platform',
  badge,
  stats,
  showImage = true,
  className = ''
}) => {
  return (
    <div className={`hero ${className}`}>
      {showImage && (
        <div className="hero-background">
          <picture>
            {/* Dark mode - WebP with PNG fallback */}
            <source 
              srcSet="/assets/heroes/hero-home-dark.webp" 
              type="image/webp"
              media="(prefers-color-scheme: dark)"
            />
            <source 
              srcSet="/assets/heroes/hero-home-dark.png" 
              type="image/png"
              media="(prefers-color-scheme: dark)"
            />
            
            {/* Light mode - WebP with PNG fallback */}
            <source 
              srcSet="/assets/heroes/hero-home-light.webp" 
              type="image/webp"
            />
            <img 
              src="/assets/heroes/hero-home-light.png" 
              alt="AI-powered CV analysis visualization" 
              className="hero-image"
              loading="eager"
            />
          </picture>
        </div>
      )}
      
      <div className="hero-content">
        {badge && (
          <div className="hero-badge">
            <span className="hero-badge-text">{badge}</span>
          </div>
        )}
        
        {title && (
          <h1 className="hero-title">
            {title.split('.').map((part, index, array) => (
              <React.Fragment key={index}>
                <span className="hero-title-line">{part.trim()}</span>
                {index < array.length - 1 && '.'}
                {index < array.length - 1 && <br />}
              </React.Fragment>
            ))}
          </h1>
        )}
        
        {subtitle && <p className="hero-subtitle">{subtitle}</p>}
        
        {stats && stats.length > 0 && (
          <div className="hero-stats">
            {stats.map((stat, index) => (
              <div key={index} className="hero-stat">
                <div className="hero-stat-value">{stat.value}</div>
                <div className="hero-stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Hero;

