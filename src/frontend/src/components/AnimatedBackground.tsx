/**
 * Animated Background Component - CSS VERSION
 * 
 * Pure CSS animated background with floating particles.
 * GUARANTEED to work - no Canvas, no JavaScript animation.
 */

import React from 'react';
import './AnimatedBackground.css';

interface AnimatedBackgroundProps {
  intensity?: 'low' | 'medium' | 'high';
}

export const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({ 
  intensity = 'medium' 
}) => {
  console.log('AnimatedBackground: Rendering CSS version');

  // Number of particles based on intensity
  const particleCount = {
    low: 20,
    medium: 30,
    high: 40
  }[intensity];

  return (
    <div className="animated-background">
      {/* CSS Animated Particles */}
      <div className="particles-container">
        {Array.from({ length: particleCount }).map((_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 20}s`,
              animationDuration: `${15 + Math.random() * 10}s`,
              width: `${10 + Math.random() * 15}px`,
              height: `${10 + Math.random() * 15}px`,
            }}
          />
        ))}
      </div>

      {/* Gradient Overlay */}
      <div className="gradient-overlay" />
      
      {/* CSS Grid Pattern */}
      <div className="grid-pattern" />
    </div>
  );
};

export default AnimatedBackground;
