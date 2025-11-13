/**
 * Hero Dual Mode Component
 * 
 * Displays two prominent sections for Interviewer Mode and Candidate Mode.
 * Each section has its own visual card with specific benefits and CTA.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './HeroDualMode.css';

export const HeroDualMode: React.FC = () => {
  const { t } = useTranslation();

  return (
    <section className="hero-dual-section">
      <div className="hero-dual-header">
        <div className="hero-dual-badge">
          <span className="hero-dual-badge-text">{t('home.heroDual.badge')}</span>
        </div>
        <h1 className="hero-dual-title">{t('home.heroDual.title')}</h1>
        <p className="hero-dual-subtitle">{t('home.heroDual.subtitle')}</p>
      </div>

      <div className="hero-dual-cards">
        {/* Interviewer Mode Card */}
        <div className="hero-dual-card hero-dual-card-interviewer">
          <div className="hero-dual-card-background">
            <div className="hero-dual-card-gradient hero-dual-card-gradient-interviewer"></div>
          </div>
          <div className="hero-dual-card-content">
            <div className="hero-dual-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 11l3 3L22 4" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" strokeLinecap="round" strokeLinejoin="round"/>
                <rect x="3" y="3" width="8" height="8" rx="1" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2 className="hero-dual-card-title">{t('home.heroDual.interviewer.title')}</h2>
            <p className="hero-dual-card-description">{t('home.heroDual.interviewer.description')}</p>
            
            <div className="hero-dual-card-features">
              <div className="hero-dual-card-feature">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>{t('home.heroDual.interviewer.feature1')}</span>
              </div>
              <div className="hero-dual-card-feature">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>{t('home.heroDual.interviewer.feature2')}</span>
              </div>
              <div className="hero-dual-card-feature">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>{t('home.heroDual.interviewer.feature3')}</span>
              </div>
            </div>

            <Link to="/interviewer/step1" className="hero-dual-card-cta hero-dual-card-cta-primary">
              <span>{t('home.heroDual.interviewer.cta')}</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
          </div>
        </div>

        {/* Candidate Mode Card */}
        <div className="hero-dual-card hero-dual-card-candidate">
          <div className="hero-dual-card-background">
            <div className="hero-dual-card-gradient hero-dual-card-gradient-candidate"></div>
          </div>
          <div className="hero-dual-card-content">
            <div className="hero-dual-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 9h8M8 13h6" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2 className="hero-dual-card-title">{t('home.heroDual.candidate.title')}</h2>
            <p className="hero-dual-card-description">{t('home.heroDual.candidate.description')}</p>
            
            <div className="hero-dual-card-features">
              <div className="hero-dual-card-feature">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>{t('home.heroDual.candidate.feature1')}</span>
              </div>
              <div className="hero-dual-card-feature">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>{t('home.heroDual.candidate.feature2')}</span>
              </div>
              <div className="hero-dual-card-feature">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>{t('home.heroDual.candidate.feature3')}</span>
              </div>
            </div>

            <Link to="/candidate/step1" className="hero-dual-card-cta hero-dual-card-cta-secondary">
              <span>{t('home.heroDual.candidate.cta')}</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
          </div>
        </div>
      </div>

      <p className="hero-dual-note">{t('home.heroDual.note')}</p>
    </section>
  );
};

export default HeroDualMode;

