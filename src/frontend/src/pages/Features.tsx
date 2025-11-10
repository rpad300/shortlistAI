/**
 * Features Page
 * 
 * Detailed feature breakdown for both Interviewer and Candidate modes.
 * SEO-optimized with structured content.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SEOHead } from '../components/SEOHead';
import Layout from '../components/Layout';
import './Features.css';

export const Features: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <Layout backgroundIntensity="low">
      <SEOHead 
        title="Features - ShortlistAI"
        description="Discover powerful features: batch CV upload, AI-powered ranking, custom interview questions, PDF reports, multilingual support. Free for interviewers and candidates."
        keywords="CV screening features, AI recruitment tools, interview questions generator, candidate ranking, batch CV upload"
        canonicalUrl="https://shortlistai.com/features"
      />
      {/* Page Header */}
      <section className="page-header">
        <div className="container">
          <h1 className="page-title">{t('features.title')}</h1>
          <p className="page-subtitle">{t('features.subtitle')}</p>
        </div>
      </section>

      {/* Interviewer Features */}
      <section className="feature-detail-section">
        <div className="container">
          <div className="feature-detail-grid">
            <div className="feature-detail-image">
              <picture>
                <source srcSet="/assets/illustrations/feature-interviewer.webp" type="image/webp" />
                <img 
                  src="/assets/illustrations/feature-interviewer.png" 
                  alt="Interviewer mode features"
                  loading="lazy"
                />
              </picture>
            </div>
            
            <div className="feature-detail-content">
              <span className="feature-badge">{t('features.forRecruiters')}</span>
              <h2 className="feature-detail-title">{t('home.features.interviewer.title')}</h2>
              <p className="feature-detail-intro">{t('home.features.interviewer.description')}</p>

              <div className="feature-list-detailed">
                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/upload.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.interviewer.batchUpload.title')}</h3>
                    <p>{t('features.interviewer.batchUpload.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-analytics.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.interviewer.smartRanking.title')}</h3>
                    <p>{t('features.interviewer.smartRanking.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/warning.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.interviewer.hardBlockers.title')}</h3>
                    <p>{t('features.interviewer.hardBlockers.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-ai.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.interviewer.aiQuestions.title')}</h3>
                    <p>{t('features.interviewer.aiQuestions.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/download.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.interviewer.pdfReports.title')}</h3>
                    <p>{t('features.interviewer.pdfReports.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-email.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.interviewer.emailSummary.title')}</h3>
                    <p>{t('features.interviewer.emailSummary.description')}</p>
                  </div>
                </div>
              </div>

              <div className="feature-cta">
                <Link to="/interviewer/step1" className="btn btn-primary btn-large">
                  {t('home.features.interviewer.cta')}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Candidate Features */}
      <section className="feature-detail-section alternate">
        <div className="container">
          <div className="feature-detail-grid reverse">
            <div className="feature-detail-content">
              <span className="feature-badge candidate-badge">{t('features.forCandidates')}</span>
              <h2 className="feature-detail-title">{t('home.features.candidate.title')}</h2>
              <p className="feature-detail-intro">{t('features.candidate.intro')}</p>

              <div className="feature-list-detailed">
                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-analytics.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.candidate.fitScore.title')}</h3>
                    <p>{t('features.candidate.fitScore.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/check-circle.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.candidate.strengthsGaps.title')}</h3>
                    <p>{t('features.candidate.strengthsGaps.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-ai.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.candidate.predictedQuestions.title')}</h3>
                    <p>{t('features.candidate.predictedQuestions.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-document.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.candidate.suggestedAnswers.title')}</h3>
                    <p>{t('features.candidate.suggestedAnswers.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-ai.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.candidate.introPitch.title')}</h3>
                    <p>{t('features.candidate.introPitch.description')}</p>
                  </div>
                </div>

                <div className="feature-item">
                  <div className="feature-item-icon">
                    <img src="/assets/icons/feature-email.svg" alt="" width="24" height="24" />
                  </div>
                  <div className="feature-item-content">
                    <h3>{t('features.candidate.prepGuide.title')}</h3>
                    <p>{t('features.candidate.prepGuide.description')}</p>
                  </div>
                </div>
              </div>

              <div className="feature-cta">
                <Link to="/candidate/step1" className="btn btn-primary btn-large">
                  {t('home.features.candidate.cta')}
                </Link>
              </div>
            </div>

            <div className="feature-detail-image">
              <picture>
                <source srcSet="/assets/illustrations/feature-candidate.webp" type="image/webp" />
                <img 
                  src="/assets/illustrations/feature-candidate.png" 
                  alt="Candidate mode features"
                  loading="lazy"
                />
              </picture>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Features */}
      <section className="tech-features-section">
        <div className="container">
          <h2 className="section-title">{t('features.technology.title')}</h2>
          <p className="section-subtitle">{t('features.technology.subtitle')}</p>

          <div className="tech-grid">
            <div className="tech-card">
              <h3>{t('features.technology.multiAI.title')}</h3>
              <p>{t('features.technology.multiAI.description')}</p>
            </div>

            <div className="tech-card">
              <h3>{t('features.technology.smartExtraction.title')}</h3>
              <p>{t('features.technology.smartExtraction.description')}</p>
            </div>

            <div className="tech-card">
              <h3>{t('features.technology.multilingual.title')}</h3>
              <p>{t('features.technology.multilingual.description')}</p>
            </div>

            <div className="tech-card">
              <h3>{t('features.technology.privacyFirst.title')}</h3>
              <p>{t('features.technology.privacyFirst.description')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta-section">
        <div className="container">
          <h2 className="cta-title">{t('features.finalCTA.title')}</h2>
          <p className="cta-subtitle">{t('features.finalCTA.subtitle')}</p>
          <div className="cta-buttons">
            <Link to="/interviewer/step1" className="btn btn-primary btn-xlarge">
              {t('home.features.interviewer.title')}
            </Link>
            <Link to="/candidate/step1" className="btn btn-secondary btn-xlarge">
              {t('home.features.candidate.title')}
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Features;

