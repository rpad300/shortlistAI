/**
 * Animated Background Component - AI Neural Network Style with Mouse Interaction
 * 
 * Interactive background with small particles and neural network connections.
 * Particles react to mouse movement - repelling and attracting based on proximity.
 * Represents AI data analysis and processing - perfect for CV analysis platform.
 */

import React, { useMemo, useRef, useEffect, useState, useCallback } from 'react';
import './AnimatedBackground.css';

interface AnimatedBackgroundProps {
  intensity?: 'low' | 'medium' | 'high';
}

interface MousePosition {
  x: number;
  y: number;
}

export const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({ 
  intensity = 'medium' 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState<MousePosition>({ x: -1000, y: -1000 });
  const animationFrameRef = useRef<number>();

  // Number of particles based on intensity - more particles for neural network effect
  const particleCount = {
    low: 40,
    medium: 60,
    high: 80
  }[intensity];

  // Generate particles with positions for connection calculations
  const { particles, connections } = useMemo(() => {
    const particles = Array.from({ length: particleCount }).map((_, i) => ({
      id: i,
      left: Math.random() * 100,
      top: Math.random() * 100,
      delay: Math.random() * 20,
      duration: 20 + Math.random() * 15,
      size: 2 + Math.random() * 3, // Smaller particles: 2-5px
      type: i % 3 === 0 ? 'purple' : 'blue' // Mix of colors
    }));

    // Generate connections between nearby particles (simplified algorithm)
    const connections: Array<{
      id: string;
      from: typeof particles[0];
      to: typeof particles[0];
      distance: number;
      angle: number;
      delay: number;
    }> = [];

    // Connect each particle to 1-2 nearby particles
    particles.forEach((particle, i) => {
      if (i % 3 !== 0) return; // Only connect some particles to reduce complexity
      
      const nearby = particles
        .filter(p => p.id !== particle.id)
        .map(p => ({
          particle: p,
          distance: Math.sqrt(
            Math.pow(particle.left - p.left, 2) + 
            Math.pow(particle.top - p.top, 2)
          )
        }))
        .filter(p => p.distance < 25 && p.distance > 5) // Only connect if within reasonable distance
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 2); // Connect to max 2 nearby particles
      
      nearby.forEach(({ particle: target, distance }) => {
        const angle = Math.atan2(
          target.top - particle.top,
          target.left - particle.left
        ) * (180 / Math.PI);
        
        connections.push({
          id: `${particle.id}-${target.id}`,
          from: particle,
          to: target,
          distance,
          angle,
          delay: (particle.delay + connections.length * 2) % 20
        });
      });
    });

    return { particles, connections };
  }, [particleCount]);

  // Handle mouse movement
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    // Calculate mouse position as percentage of viewport
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    // Only update if mouse is within bounds
    if (x >= 0 && x <= 100 && y >= 0 && y <= 100) {
      setMousePos({ x, y });
    }
  }, []);

  // Handle mouse leave - reset to far position
  const handleMouseLeave = useCallback(() => {
    setMousePos({ x: -1000, y: -1000 });
  }, []);

  // Update particle positions based on mouse
  useEffect(() => {
    const updateParticles = () => {
      if (!containerRef.current) return;

      particles.forEach((particle, index) => {
        const particleEl = containerRef.current?.querySelector(
          `[data-particle-id="${particle.id}"]`
        ) as HTMLElement;
        
        if (!particleEl) return;

        // Calculate distance from mouse to particle
        const dx = mousePos.x - particle.left;
        const dy = mousePos.y - particle.top;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Interaction radius (particles react within 15% of viewport)
        const interactionRadius = 15;
        const maxRepulsion = 8; // Maximum pixels to move away
        
        if (distance < interactionRadius && distance > 0) {
          // Calculate repulsion force (stronger when closer)
          const force = (1 - distance / interactionRadius) * maxRepulsion;
          const angle = Math.atan2(dy, dx);
          
          // Apply repulsion (move particle away from mouse)
          const offsetX = Math.cos(angle + Math.PI) * force;
          const offsetY = Math.sin(angle + Math.PI) * force;
          
          // Also scale up particle when near mouse
          const scale = 1 + (1 - distance / interactionRadius) * 0.5;
          
          particleEl.style.setProperty('--mouse-offset-x', `${offsetX}px`);
          particleEl.style.setProperty('--mouse-offset-y', `${offsetY}px`);
          particleEl.style.setProperty('--mouse-scale', `${scale}`);
        } else {
          // Reset when far from mouse
          particleEl.style.setProperty('--mouse-offset-x', '0px');
          particleEl.style.setProperty('--mouse-offset-y', '0px');
          particleEl.style.setProperty('--mouse-scale', '1');
        }
      });

      // Update connections - intensify near mouse
      connections.forEach((connection) => {
        const connectionEl = containerRef.current?.querySelector(
          `[data-connection-id="${connection.id}"]`
        ) as HTMLElement;
        
        if (!connectionEl) return;

        // Check if connection midpoint is near mouse
        const midX = (connection.from.left + connection.to.left) / 2;
        const midY = (connection.from.top + connection.to.top) / 2;
        const dx = mousePos.x - midX;
        const dy = mousePos.y - midY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        const interactionRadius = 20;
        
        if (distance < interactionRadius) {
          const intensity = 1 + (1 - distance / interactionRadius) * 1.5;
          connectionEl.style.setProperty('--connection-intensity', `${intensity}`);
          connectionEl.style.setProperty('--connection-opacity', `${Math.min(intensity * 0.6, 1)}`);
        } else {
          connectionEl.style.setProperty('--connection-intensity', '1');
          connectionEl.style.setProperty('--connection-opacity', '0.3');
        }
      });

      animationFrameRef.current = requestAnimationFrame(updateParticles);
    };

    animationFrameRef.current = requestAnimationFrame(updateParticles);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [mousePos, particles, connections]);

  // Add event listeners to document (doesn't interfere with page interactions)
  useEffect(() => {
    // Use document to capture mouse events without blocking page interactions
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [handleMouseMove, handleMouseLeave]);

  return (
    <div 
      ref={containerRef}
      className="animated-background interactive"
      style={{
        '--mouse-x': `${mousePos.x}%`,
        '--mouse-y': `${mousePos.y}%`,
      } as React.CSSProperties}
    >
      {/* Neural Network Connections Layer */}
      <div className="connections-layer">
        {connections.map((connection) => (
          <div
            key={connection.id}
            data-connection-id={connection.id}
            className="connection-line"
            style={{
              left: `${connection.from.left}%`,
              top: `${connection.from.top}%`,
              width: `${connection.distance}%`,
              transform: `rotate(${connection.angle}deg)`,
              animationDelay: `${connection.delay}s`,
            }}
          />
        ))}
      </div>

      {/* Small Particles (Data Points) */}
      <div className="particles-container">
        {particles.map((particle) => (
          <div
            key={particle.id}
            data-particle-id={particle.id}
            className={`particle particle-${particle.type}`}
            style={{
              left: `${particle.left}%`,
              top: `${particle.top}%`,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
            }}
          >
            <div 
              className="particle-inner"
              style={{
                animationDelay: `${particle.delay}s`,
                animationDuration: `${particle.duration}s`,
              }}
            />
          </div>
        ))}
      </div>

      {/* Gradient Overlay */}
      <div className="gradient-overlay" />
      
      {/* Subtle Grid Pattern (Data Structure) */}
      <div className="grid-pattern" />
    </div>
  );
};

export default AnimatedBackground;
