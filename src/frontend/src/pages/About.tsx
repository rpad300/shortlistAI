/**
 * About / How It Works Page
 * 
 * Explains what ShortlistAI is, how it works, and who it's for.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SEOHead } from '../components/SEOHead';
import Layout from '../components/Layout';
import './About.css';

export const About: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <Layout backgroundIntensity="low">
      <SEOHead 
        title="About & How It Works - ShortlistAI"
        description="Learn how ShortlistAI uses advanced AI to analyze CVs and help both interviewers and candidates. 100% free, multilingual, GDPR compliant platform powered by Gemini, OpenAI, and Claude."
        keywords="about ShortlistAI, how it works, AI CV analysis, hiring technology, interview preparation platform"
        canonicalUrl="https://shortlistai.com/about"
        pageType="about"
      />
      {/* Header */}
      <section className="about-header">
        <div className="container">
          <h1 className="page-title">{t('about.title')}</h1>
          <p className="page-subtitle">{t('about.subtitle')}</p>
        </div>
      </section>

      {/* Mission */}
      <section className="mission-section">
        <div className="container">
          <div className="mission-content">
            <h2 className="section-title">{t('about.mission.title')}</h2>
            <p className="mission-text">{t('about.mission.text1')}</p>
            <p className="mission-text"><strong>{t('about.mission.text2')}</strong></p>
            <p className="mission-text">{t('about.mission.text3')}</p>
          </div>
        </div>
      </section>

      {/* How It Works - Detailed */}
      <section className="how-works-detailed-section">
        <div className="container">
          <h2 className="section-title">{t('about.howItWorks.title')}</h2>

          <div className="workflow-tabs">
            <div className="workflow-tab">
              <h3>{t('features.forRecruiters')}</h3>
              
              <div className="workflow-steps">
                {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                  <div key={num} className="workflow-step">
                    <div className="workflow-step-number">Step {num}</div>
                    <div className="workflow-step-content">
                      <h4>{t(`about.howItWorks.interviewerSteps.step${num}.title`)}</h4>
                      <p>{t(`about.howItWorks.interviewerSteps.step${num}.desc`)}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="workflow-cta">
                <Link to="/interviewer/step1" className="btn btn-primary">
                  {t('about.howItWorks.tryInterviewer')}
                </Link>
              </div>
            </div>

            <div className="workflow-tab">
              <h3>{t('features.forCandidates')}</h3>
              
              <div className="workflow-steps">
                {[1, 2, 3, 4, 5, 6].map((num) => (
                  <div key={num} className="workflow-step">
                    <div className="workflow-step-number">Step {num}</div>
                    <div className="workflow-step-content">
                      <h4>{t(`about.howItWorks.candidateSteps.step${num}.title`)}</h4>
                      <p>{t(`about.howItWorks.candidateSteps.step${num}.desc`)}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="workflow-cta">
                <Link to="/candidate/step1" className="btn btn-primary">
                  {t('about.howItWorks.tryCandidate')}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology */}
      <section className="technology-section">
        <div className="container">
          <h2 className="section-title">{t('about.technology.title')}</h2>
          <p className="section-subtitle">{t('about.technology.subtitle')}</p>

          <div className="ai-providers-grid">
            <div className="ai-provider-card">
              <h3>{t('about.technology.gemini.title')}</h3>
              <p>{t('about.technology.gemini.desc')}</p>
            </div>

            <div className="ai-provider-card">
              <h3>{t('about.technology.openai.title')}</h3>
              <p>{t('about.technology.openai.desc')}</p>
            </div>

            <div className="ai-provider-card">
              <h3>{t('about.technology.claude.title')}</h3>
              <p>{t('about.technology.claude.desc')}</p>
            </div>

            <div className="ai-provider-card">
              <h3>{t('about.technology.others.title')}</h3>
              <p>{t('about.technology.others.desc')}</p>
            </div>
          </div>

          <div className="tech-note">
            <p>{t('about.technology.note')}</p>
          </div>
        </div>
      </section>

      {/* Privacy & Security */}
      <section className="privacy-section">
        <div className="container">
          <h2 className="section-title">{t('about.privacy.title')}</h2>
          
          <div className="privacy-grid">
            <div className="privacy-card">
              <h3>{t('about.privacy.gdpr.title')}</h3>
              <p>{t('about.privacy.gdpr.description')}</p>
            </div>

            <div className="privacy-card">
              <h3>{t('about.privacy.noTraining.title')}</h3>
              <p>{t('about.privacy.noTraining.description')}</p>
            </div>

            <div className="privacy-card">
              <h3>{t('about.privacy.secure.title')}</h3>
              <p>{t('about.privacy.secure.description')}</p>
            </div>

            <div className="privacy-card">
              <h3>{t('about.privacy.temporary.title')}</h3>
              <p>{t('about.privacy.temporary.description')}</p>
            </div>
          </div>

          <div className="privacy-cta">
            <p>
              <Link to="/legal/privacy" className="link-underline">{t('common.learnMore')}</Link>
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="about-cta-section">
        <div className="container">
          <h2 className="cta-title">{t('about.cta.title')}</h2>
          <p className="cta-subtitle">{t('about.cta.subtitle')}</p>
          <div className="cta-buttons">
            <Link to="/interviewer/step1" className="btn btn-primary btn-xlarge">
              {t('nav.analyzeCV')}
            </Link>
            <Link to="/candidate/step1" className="btn btn-secondary btn-xlarge">
              {t('nav.prepareInterview')}
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default About;

