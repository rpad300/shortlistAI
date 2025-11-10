/**
 * Hero Component with Light/Dark Mode Support
 * 
 * Displays hero images that adapt to the user's color scheme preference.
 * Uses the generated brand images from Gemini Nano Banana.
 */

import React from 'react';
import './Hero.css';

interface HeroProps {
  title?: string;
  subtitle?: string;
  showImage?: boolean;
  className?: string;
}

export const Hero: React.FC<HeroProps> = ({
  title = 'ShortlistAI',
  subtitle = 'AI-Powered CV Analysis Platform',
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
        {title && <h1 className="hero-title">{title}</h1>}
        {subtitle && <p className="hero-subtitle">{subtitle}</p>}
      </div>
    </div>
  );
};

export default Hero;

