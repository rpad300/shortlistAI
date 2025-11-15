/**
 * Feature Card Component
 * 
 * Reusable card for displaying product features.
 */

import React from 'react';
import './FeatureCard.css';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  link?: string;
  linkText?: string;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  link,
  linkText = 'Learn more →'
}) => {
  return (
    <div className="feature-card-component">
      <div className="feature-card-icon">
        <img src={icon} alt="" width="32" height="32" />
      </div>
      <h3 className="feature-card-title">{title}</h3>
      <p className="feature-card-description">{description}</p>
      {link && (
        <a href={link} className="feature-card-link">
          {linkText}
        </a>
      )}
    </div>
  );
};

export default FeatureCard;





