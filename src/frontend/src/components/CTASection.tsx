/**
 * CTA Section Component
 * 
 * Reusable call-to-action section with branded styling.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './CTASection.css';

interface CTASectionProps {
  title: string;
  subtitle?: string;
  primaryText: string;
  primaryLink: string;
  secondaryText?: string;
  secondaryLink?: string;
  note?: string;
  variant?: 'gradient' | 'light' | 'dark';
}

export const CTASection: React.FC<CTASectionProps> = ({
  title,
  subtitle,
  primaryText,
  primaryLink,
  secondaryText,
  secondaryLink,
  note,
  variant = 'gradient'
}) => {
  return (
    <section className={`cta-section-component cta-${variant}`}>
      <div className="container">
        <h2 className="cta-title">{title}</h2>
        {subtitle && <p className="cta-subtitle">{subtitle}</p>}
        
        <div className="cta-buttons">
          <Link to={primaryLink} className="btn btn-primary btn-xlarge">
            {primaryText}
          </Link>
          {secondaryText && secondaryLink && (
            <Link to={secondaryLink} className="btn btn-secondary btn-xlarge">
              {secondaryText}
            </Link>
          )}
        </div>

        {note && <p className="cta-note">{note}</p>}
      </div>
    </section>
  );
};

export default CTASection;


