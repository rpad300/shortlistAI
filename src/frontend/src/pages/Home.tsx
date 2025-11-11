/**
 * Home / Landing Page
 * 
 * Main institutional landing page for ShortlistAI.
 * Features: Hero section, features overview, benefits, CTAs, SEO optimized.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Hero } from '../components/Hero';
import { SEOHead, getOrganizationSchema, getWebsiteSchema, getSoftwareApplicationSchema } from '../components/SEOHead';
import Layout from '../components/Layout';
import './Home.css';

export const Home: React.FC = () => {
  const { t } = useTranslation();
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
        ogImage="https://shortlistai.com/assets/social/og-default.png"
        canonicalUrl="https://shortlistai.com/"
        structuredData={structuredData}
      />
        
        {/* Hero Section with AI-generated background */}
        <section className="hero-section">
        <Hero 
          title={t('home.hero.title')}
          subtitle={t('home.hero.subtitle')}
          showImage={false}
        />
        
        <div className="hero-cta">
          <Link to="/interviewer/step1" className="btn btn-primary btn-large">
            <img src="/assets/icons/feature-analytics.svg" alt="" width="20" height="20" />
            {t('nav.analyzeCV')}
          </Link>
          <Link to="/candidate/step1" className="btn btn-secondary btn-large">
            <img src="/assets/icons/feature-document.svg" alt="" width="20" height="20" />
            {t('nav.prepareInterview')}
          </Link>
        </div>
      </section>

      {/* Value Proposition */}
      <section className="value-prop-section">
        <div className="container">
          <h2 className="section-title">{t('home.valueProp.title')}</h2>
          <p className="section-subtitle">
            {t('home.valueProp.subtitle')}
          </p>
          
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">10x</div>
              <div className="stat-label">{t('home.valueProp.stat1')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">100%</div>
              <div className="stat-label">{t('home.valueProp.stat2')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">4</div>
              <div className="stat-label">{t('home.valueProp.stat3')}</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">5</div>
              <div className="stat-label">{t('home.valueProp.stat4')}</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Features */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">{t('home.features.title')}</h2>
          
          <div className="features-grid">
            {/* Interviewer Mode */}
            <div className="feature-card feature-card-large">
              <div className="feature-image">
                <picture>
                  <source srcSet="/assets/illustrations/feature-interviewer.webp" type="image/webp" />
                  <img 
                    src="/assets/illustrations/feature-interviewer.png" 
                    alt="Interviewer mode - Analyze multiple CVs"
                    loading="lazy"
                  />
                </picture>
              </div>
              <div className="feature-content">
                <h3 className="feature-title">
                  <img src="/assets/icons/feature-analytics.svg" alt="" width="28" height="28" />
                  {t('home.features.interviewer.title')}
                </h3>
                <p className="feature-description">
                  {t('home.features.interviewer.description')}
                </p>
                <ul className="feature-list">
                  {interviewerFeatures.map((feature, i: number) => (
                    <li key={i}>✓ {feature}</li>
                  ))}
                </ul>
                <Link to="/interviewer/step1" className="btn btn-primary">
                  {t('home.features.interviewer.cta')}
                </Link>
              </div>
            </div>

            {/* Candidate Mode */}
            <div className="feature-card feature-card-large">
              <div className="feature-image">
                <picture>
                  <source srcSet="/assets/illustrations/feature-candidate.webp" type="image/webp" />
                  <img 
                    src="/assets/illustrations/feature-candidate.png" 
                    alt="Candidate mode - Prepare for interviews"
                    loading="lazy"
                  />
                </picture>
              </div>
              <div className="feature-content">
                <h3 className="feature-title">
                  <img src="/assets/icons/feature-ai.svg" alt="" width="28" height="28" />
                  {t('home.features.candidate.title')}
                </h3>
                <p className="feature-description">
                  {t('home.features.candidate.description')}
                </p>
                <ul className="feature-list">
                  {candidateFeatures.map((feature, i: number) => (
                    <li key={i}>✓ {feature}</li>
                  ))}
                </ul>
                <Link to="/candidate/step1" className="btn btn-primary">
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
          <h2 className="section-title">{t('home.howItWorks.title')}</h2>
          <p className="section-subtitle">{t('home.howItWorks.subtitle')}</p>
          
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">1</div>
              <div className="step-icon">
                <img src="/assets/icons/upload.svg" alt="" width="32" height="32" />
              </div>
              <h3 className="step-title">{t('home.howItWorks.step1.title')}</h3>
              <p className="step-description">{t('home.howItWorks.step1.description')}</p>
            </div>

            <div className="step-card">
              <div className="step-number">2</div>
              <div className="step-icon">
                <img src="/assets/icons/feature-ai.svg" alt="" width="32" height="32" />
              </div>
              <h3 className="step-title">{t('home.howItWorks.step2.title')}</h3>
              <p className="step-description">{t('home.howItWorks.step2.description')}</p>
            </div>

            <div className="step-card">
              <div className="step-number">3</div>
              <div className="step-icon">
                <img src="/assets/icons/feature-analytics.svg" alt="" width="32" height="32" />
              </div>
              <h3 className="step-title">{t('home.howItWorks.step3.title')}</h3>
              <p className="step-description">{t('home.howItWorks.step3.description')}</p>
            </div>

            <div className="step-card">
              <div className="step-number">4</div>
              <div className="step-icon">
                <img src="/assets/icons/download.svg" alt="" width="32" height="32" />
              </div>
              <h3 className="step-title">{t('home.howItWorks.step4.title')}</h3>
              <p className="step-description">{t('home.howItWorks.step4.description')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits / Why ShortlistAI */}
      <section className="benefits-section">
        <div className="container">
          <h2 className="section-title">{t('home.benefits.title')}</h2>
          
          <div className="benefits-grid">
            <div className="benefit-card">
              <div className="benefit-icon">💰</div>
              <h3 className="benefit-title">{t('home.benefits.free.title')}</h3>
              <p className="benefit-description">{t('home.benefits.free.description')}</p>
            </div>

            <div className="benefit-card">
              <div className="benefit-icon">⚡</div>
              <h3 className="benefit-title">{t('home.benefits.fast.title')}</h3>
              <p className="benefit-description">{t('home.benefits.fast.description')}</p>
            </div>

            <div className="benefit-card">
              <div className="benefit-icon">🌍</div>
              <h3 className="benefit-title">{t('home.benefits.multilingual.title')}</h3>
              <p className="benefit-description">{t('home.benefits.multilingual.description')}</p>
            </div>

            <div className="benefit-card">
              <div className="benefit-icon">🤖</div>
              <h3 className="benefit-title">{t('home.benefits.ai.title')}</h3>
              <p className="benefit-description">{t('home.benefits.ai.description')}</p>
            </div>

            <div className="benefit-card">
              <div className="benefit-icon">🔒</div>
              <h3 className="benefit-title">{t('home.benefits.secure.title')}</h3>
              <p className="benefit-description">{t('home.benefits.secure.description')}</p>
            </div>

            <div className="benefit-card">
              <div className="benefit-icon">📱</div>
              <h3 className="benefit-title">{t('home.benefits.everywhere.title')}</h3>
              <p className="benefit-description">{t('home.benefits.everywhere.description')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="use-cases-section">
        <div className="container">
          <h2 className="section-title">{t('home.useCases.title')}</h2>
          
          <div className="use-cases-grid">
            <div className="use-case-card">
              <h3>{t('home.useCases.recruiters.title')}</h3>
              <p>{t('home.useCases.recruiters.description')}</p>
            </div>

            <div className="use-case-card">
              <h3>{t('home.useCases.managers.title')}</h3>
              <p>{t('home.useCases.managers.description')}</p>
            </div>

            <div className="use-case-card">
              <h3>{t('home.useCases.seekers.title')}</h3>
              <p>{t('home.useCases.seekers.description')}</p>
            </div>

            <div className="use-case-card">
              <h3>{t('home.useCases.startups.title')}</h3>
              <p>{t('home.useCases.startups.description')}</p>
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

