/**
 * Home / Landing Page
 * 
 * Main institutional landing page for ShortlistAI.
 * Features: Hero section, features overview, benefits, CTAs, SEO optimized.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { HeroDualMode } from '../components/HeroDualMode';
import { SEOHead, getOrganizationSchema, getWebsiteSchema, getSoftwareApplicationSchema } from '../components/SEOHead';
import Layout from '../components/Layout';
import './Home.css';

export const Home: React.FC = () => {
  const { t } = useTranslation();
  const [totalAnalyses, setTotalAnalyses] = useState<number | null>(null);

  // Fetch total analyses count
  useEffect(() => {
    const fetchTotalAnalyses = async () => {
      try {
        const response = await fetch('/api/stats/total-analyses', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          // Add cache control to prevent stale data
          cache: 'no-cache',
        });
        
        if (response.ok) {
          const data = await response.json();
          const count = data.total_analyses || 0;
          console.log('[Home] Total analyses fetched:', count);
          setTotalAnalyses(count);
        } else {
          console.warn('[Home] Failed to fetch total analyses:', response.status, response.statusText);
          // Set to null to hide the stat card instead of showing 0
          setTotalAnalyses(null);
        }
      } catch (error) {
        console.error('[Home] Error fetching total analyses:', error);
        // Set to null to hide the stat card instead of showing 0
        setTotalAnalyses(null);
      }
    };

    fetchTotalAnalyses();
  }, []);

  const interviewerFeaturesRaw = t('home.features.interviewer.features', { returnObjects: true }) as unknown;
  const interviewerFeatures = Array.isArray(interviewerFeaturesRaw) ? (interviewerFeaturesRaw as string[]) : [];
  const candidateFeaturesRaw = t('home.features.candidate.features', { returnObjects: true }) as unknown;
  const candidateFeatures = Array.isArray(candidateFeaturesRaw) ? (candidateFeaturesRaw as string[]) : [];

  // Structured data for homepage
  const structuredData = {
    "@context": "https://schema.org",
    "@graph": [
      getOrganizationSchema(),
      getWebsiteSchema(),
      getSoftwareApplicationSchema()
    ]
  };

  return (
    <Layout backgroundIntensity="medium" showFooter={true}>
      <SEOHead 
        title="ShortlistAI - AI-Powered CV Analysis Platform"
        description="Free AI-powered CV analysis for interviewers and candidates. Compare CVs, prepare for interviews, and build your headhunting database. Multilingual support: EN, PT, FR, ES."
        keywords="CV analysis, AI recruitment, interview preparation, headhunting, candidate screening, CV comparison, job matching, free recruiting tool"
        canonicalUrl="https://shortlistai.com/"
        pageType="home"
        structuredData={structuredData}
      />
        
        {/* Hero Section - Dual Mode */}
        <HeroDualMode totalAnalyses={totalAnalyses} />

      {/* Value Proposition */}
      <section className="value-prop-section">
        <div className="container">
          <div className="value-prop-header">
            <h2 className="section-title">{t('home.valueProp.title')}</h2>
            <p className="section-subtitle">
              {t('home.valueProp.subtitle')}
            </p>
          </div>
          
          <div className="value-prop-cards">
            {/* Interviewer Value Prop */}
            <div className="value-prop-card value-prop-card-interviewer">
              <div className="value-prop-card-header">
                <div className="value-prop-icon value-prop-icon-interviewer">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 11l3 3L22 4" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 className="value-prop-card-title">{t('home.valueProp.interviewer.title')}</h3>
                <p className="value-prop-card-subtitle">{t('home.valueProp.interviewer.subtitle')}</p>
              </div>
              <p className="value-prop-card-description">
                {t('home.valueProp.interviewer.description')}
              </p>
              <div className="value-prop-stats">
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.interviewer.stat1.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.interviewer.stat1.label')}</div>
                </div>
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.interviewer.stat2.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.interviewer.stat2.label')}</div>
                </div>
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.interviewer.stat3.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.interviewer.stat3.label')}</div>
                </div>
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.interviewer.stat4.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.interviewer.stat4.label')}</div>
                </div>
              </div>
            </div>

            {/* Candidate Value Prop */}
            <div className="value-prop-card value-prop-card-candidate">
              <div className="value-prop-card-header">
                <div className="value-prop-icon value-prop-icon-candidate">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M8 9h8M8 13h6" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 className="value-prop-card-title">{t('home.valueProp.candidate.title')}</h3>
                <p className="value-prop-card-subtitle">{t('home.valueProp.candidate.subtitle')}</p>
              </div>
              <p className="value-prop-card-description">
                {t('home.valueProp.candidate.description')}
              </p>
              <div className="value-prop-stats">
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.candidate.stat1.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.candidate.stat1.label')}</div>
                </div>
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.candidate.stat2.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.candidate.stat2.label')}</div>
                </div>
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.candidate.stat3.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.candidate.stat3.label')}</div>
                </div>
                <div className="value-prop-stat">
                  <div className="value-prop-stat-number">{t('home.valueProp.candidate.stat4.value')}</div>
                  <div className="value-prop-stat-label">{t('home.valueProp.candidate.stat4.label')}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Features */}
      <section className="features-section">
        <div className="container">
          <div className="features-header">
            <h2 className="section-title">{t('home.features.title')}</h2>
            {t('home.features.subtitle') && (
              <p className="section-subtitle">{t('home.features.subtitle')}</p>
            )}
          </div>
          
          <div className="features-grid">
            {/* Interviewer Mode */}
            <div className="feature-card feature-card-large feature-card-interviewer">
              <div className="feature-card-badge feature-card-badge-interviewer">
                {t('home.features.interviewer.badge')}
              </div>
              <div className="feature-image feature-image-interviewer">
                <picture>
                  <source srcSet="/assets/illustrations/feature-interviewer.webp" type="image/webp" />
                  <img 
                    src="/assets/illustrations/feature-interviewer.png" 
                    alt="Interviewer mode - Analyze multiple CVs"
                    loading="lazy"
                  />
                </picture>
                <div className="feature-image-overlay"></div>
              </div>
              <div className="feature-content">
                <h3 className="feature-title">
                  <div className="feature-icon-wrapper feature-icon-interviewer">
                    <img src="/assets/icons/feature-analytics.svg" alt="" width="32" height="32" />
                  </div>
                  {t('home.features.interviewer.title')}
                </h3>
                {t('home.features.interviewer.highlight') && (
                  <div className="feature-highlight feature-highlight-interviewer">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {t('home.features.interviewer.highlight')}
                  </div>
                )}
                <p className="feature-description">
                  {t('home.features.interviewer.description')}
                </p>
                <ul className="feature-list">
                  {interviewerFeatures.map((feature, i: number) => (
                    <li key={i}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/interviewer/step1" className="btn btn-primary btn-feature">
                  {t('home.features.interviewer.cta')}
                </Link>
              </div>
            </div>

            {/* Candidate Mode */}
            <div className="feature-card feature-card-large feature-card-candidate">
              <div className="feature-card-badge feature-card-badge-candidate">
                {t('home.features.candidate.badge')}
              </div>
              <div className="feature-image feature-image-candidate">
                <picture>
                  <source srcSet="/assets/illustrations/feature-candidate.webp" type="image/webp" />
                  <img 
                    src="/assets/illustrations/feature-candidate.png" 
                    alt="Candidate mode - Prepare for interviews"
                    loading="lazy"
                  />
                </picture>
                <div className="feature-image-overlay"></div>
              </div>
              <div className="feature-content">
                <h3 className="feature-title">
                  <div className="feature-icon-wrapper feature-icon-candidate">
                    <img src="/assets/icons/feature-ai.svg" alt="" width="32" height="32" />
                  </div>
                  {t('home.features.candidate.title')}
                </h3>
                {t('home.features.candidate.highlight') && (
                  <div className="feature-highlight feature-highlight-candidate">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {t('home.features.candidate.highlight')}
                  </div>
                )}
                <p className="feature-description">
                  {t('home.features.candidate.description')}
                </p>
                <ul className="feature-list">
                  {candidateFeatures.map((feature, i: number) => (
                    <li key={i}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/candidate/step1" className="btn btn-primary btn-feature">
                  {t('home.features.candidate.cta')}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works-section">
        <div className="container">
          <div className="how-it-works-header">
            <h2 className="section-title">{t('home.howItWorks.title')}</h2>
            <p className="section-subtitle">{t('home.howItWorks.subtitle')}</p>
          </div>
          
          <div className="steps-container">
            <div className="steps-grid">
              <div className="step-card step-card-1">
                <div className="step-number-wrapper">
                  <div className="step-number">1</div>
                </div>
                <div className="step-icon-wrapper">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 className="step-title">{t('home.howItWorks.step1.title')}</h3>
                <p className="step-description">{t('home.howItWorks.step1.description')}</p>
                {t('home.howItWorks.step1.time') && (
                  <div className="step-time">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {t('home.howItWorks.step1.time')}
                  </div>
                )}
                <div className="step-connector step-connector-right">
                  <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
                    <path d="M0 12h35" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M30 7l5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>

              <div className="step-card step-card-2">
                <div className="step-number-wrapper">
                  <div className="step-number">2</div>
                </div>
                <div className="step-icon-wrapper">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M2 17l10 5 10-5M2 12l10 5 10-5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 className="step-title">{t('home.howItWorks.step2.title')}</h3>
                <p className="step-description">{t('home.howItWorks.step2.description')}</p>
                {t('home.howItWorks.step2.time') && (
                  <div className="step-time">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {t('home.howItWorks.step2.time')}
                  </div>
                )}
                <div className="step-connector step-connector-right">
                  <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
                    <path d="M0 12h35" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M30 7l5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>

              <div className="step-card step-card-3">
                <div className="step-number-wrapper">
                  <div className="step-number">3</div>
                </div>
                <div className="step-icon-wrapper">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 11l3 3L22 4" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 className="step-title">{t('home.howItWorks.step3.title')}</h3>
                <p className="step-description">{t('home.howItWorks.step3.description')}</p>
                {t('home.howItWorks.step3.time') && (
                  <div className="step-time">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {t('home.howItWorks.step3.time')}
                  </div>
                )}
                <div className="step-connector step-connector-right">
                  <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
                    <path d="M0 12h35" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M30 7l5 5-5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>

              <div className="step-card step-card-4">
                <div className="step-number-wrapper">
                  <div className="step-number">4</div>
                </div>
                <div className="step-icon-wrapper">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 className="step-title">{t('home.howItWorks.step4.title')}</h3>
                <p className="step-description">{t('home.howItWorks.step4.description')}</p>
                {t('home.howItWorks.step4.time') && (
                  <div className="step-time">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {t('home.howItWorks.step4.time')}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits / Why ShortlistAI */}
      <section className="benefits-section">
        <div className="container">
          <div className="benefits-header">
            <h2 className="section-title">{t('home.benefits.title')}</h2>
            {t('home.benefits.subtitle') && (
              <p className="section-subtitle">{t('home.benefits.subtitle')}</p>
            )}
          </div>
          
          <div className="benefits-grid">
            <div className="benefit-card benefit-card-free">
              <div className="benefit-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="benefit-title">{t('home.benefits.free.title')}</h3>
              <p className="benefit-description">{t('home.benefits.free.description')}</p>
            </div>

            <div className="benefit-card benefit-card-fast">
              <div className="benefit-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="benefit-title">{t('home.benefits.fast.title')}</h3>
              <p className="benefit-description">{t('home.benefits.fast.description')}</p>
            </div>

            <div className="benefit-card benefit-card-multilingual">
              <div className="benefit-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="benefit-title">{t('home.benefits.multilingual.title')}</h3>
              <p className="benefit-description">{t('home.benefits.multilingual.description')}</p>
            </div>

            <div className="benefit-card benefit-card-ai">
              <div className="benefit-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="4" y="4" width="16" height="16" rx="2" ry="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M9 9h6M9 15h6M9 12h6" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="benefit-title">{t('home.benefits.ai.title')}</h3>
              <p className="benefit-description">{t('home.benefits.ai.description')}</p>
            </div>

            <div className="benefit-card benefit-card-secure">
              <div className="benefit-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="benefit-title">{t('home.benefits.secure.title')}</h3>
              <p className="benefit-description">{t('home.benefits.secure.description')}</p>
            </div>

            <div className="benefit-card benefit-card-everywhere">
              <div className="benefit-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="5" y="2" width="14" height="20" rx="2" ry="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 18h.01" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="benefit-title">{t('home.benefits.everywhere.title')}</h3>
              <p className="benefit-description">{t('home.benefits.everywhere.description')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="use-cases-section">
        <div className="container">
          <div className="use-cases-header">
            <h2 className="section-title">{t('home.useCases.title')}</h2>
            {t('home.useCases.subtitle') && (
              <p className="section-subtitle">{t('home.useCases.subtitle')}</p>
            )}
          </div>
          
          <div className="use-cases-grid">
            <div className="use-case-card use-case-card-recruiters">
              <div className="use-case-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="9" cy="7" r="4" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="use-case-title">{t('home.useCases.recruiters.title')}</h3>
              <p className="use-case-description">{t('home.useCases.recruiters.description')}</p>
              {t('home.useCases.recruiters.benefit') && (
                <div className="use-case-benefit">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {t('home.useCases.recruiters.benefit')}
                </div>
              )}
            </div>

            <div className="use-case-card use-case-card-managers">
              <div className="use-case-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 17l10 5 10-5M2 12l10 5 10-5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="use-case-title">{t('home.useCases.managers.title')}</h3>
              <p className="use-case-description">{t('home.useCases.managers.description')}</p>
              {t('home.useCases.managers.benefit') && (
                <div className="use-case-benefit">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {t('home.useCases.managers.benefit')}
                </div>
              )}
            </div>

            <div className="use-case-card use-case-card-seekers">
              <div className="use-case-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="12" cy="10" r="3" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="use-case-title">{t('home.useCases.seekers.title')}</h3>
              <p className="use-case-description">{t('home.useCases.seekers.description')}</p>
              {t('home.useCases.seekers.benefit') && (
                <div className="use-case-benefit">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {t('home.useCases.seekers.benefit')}
                </div>
              )}
            </div>

            <div className="use-case-card use-case-card-startups">
              <div className="use-case-icon-wrapper">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" strokeLinecap="round" strokeLinejoin="round"/>
                  <polyline points="9 22 9 12 15 12 15 22" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="use-case-title">{t('home.useCases.startups.title')}</h3>
              <p className="use-case-description">{t('home.useCases.startups.description')}</p>
              {t('home.useCases.startups.benefit') && (
                <div className="use-case-benefit">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {t('home.useCases.startups.benefit')}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-box">
            <h2 className="cta-title">{t('home.cta.title')}</h2>
            <p className="cta-subtitle">{t('home.cta.subtitle')}</p>
            <div className="cta-buttons">
              <Link to="/interviewer/step1" className="btn btn-primary btn-xlarge">
                {t('nav.analyzeCV')}
              </Link>
              <Link to="/candidate/step1" className="btn btn-secondary btn-xlarge">
                {t('nav.prepareInterview')}
              </Link>
            </div>
            <p className="cta-note">{t('home.cta.note')}</p>
          </div>
        </div>
      </section>

    </Layout>
  );
};

export default Home;

