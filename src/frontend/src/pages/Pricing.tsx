/**
 * Pricing Page
 * 
 * Communicates that ShortlistAI is 100% free with no hidden costs.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SEOHead, getFAQSchema } from '../components/SEOHead';
import Layout from '../components/Layout';
import './Pricing.css';

export const Pricing: React.FC = () => {
  const { t } = useTranslation();
  
  // FAQ structured data
  const faqData = [
    { question: t('pricing.faq.q1.q'), answer: t('pricing.faq.q1.a') },
    { question: t('pricing.faq.q2.q'), answer: t('pricing.faq.q2.a') },
    { question: t('pricing.faq.q3.q'), answer: t('pricing.faq.q3.a') },
    { question: t('pricing.faq.q4.q'), answer: t('pricing.faq.q4.a') },
    { question: t('pricing.faq.q5.q'), answer: t('pricing.faq.q5.a') }
  ];

  return (
    <Layout backgroundIntensity="low">
      <SEOHead 
        title="Pricing - 100% Free - ShortlistAI"
        description="ShortlistAI is completely free forever. No credit card, no signup, no hidden costs. Full access to AI-powered CV analysis, batch upload, PDF reports, and all features."
        keywords="free CV analysis, free recruiting tool, free interview preparation, no cost CV screening, free AI hiring tool"
        canonicalUrl="https://shortlistai.com/pricing"
        structuredData={getFAQSchema(faqData)}
      />
      {/* Header */}
      <section className="pricing-header">
        <div className="container">
          <h1 className="page-title">{t('pricing.title')}</h1>
          <p className="page-subtitle">{t('pricing.subtitle')}</p>
        </div>
      </section>

      {/* Pricing Card */}
      <section className="pricing-main-section">
        <div className="container">
          <div className="pricing-card-main">
            <div className="pricing-badge">{t('pricing.alwaysFree')}</div>
            <h2 className="pricing-plan-name">{t('pricing.plan')}</h2>
            <div className="pricing-price">
              <span className="price-amount">{t('pricing.price')}</span>
              <span className="price-period">{t('pricing.period')}</span>
            </div>
            <p className="pricing-subtitle">{t('pricing.planSubtitle')}</p>

            <div className="pricing-features">
              <h3>{t('pricing.included')}</h3>
              <ul className="pricing-feature-list">
                {t('pricing.features', { returnObjects: true }).map((feature: string, i: number) => (
                  <li key={i}>
                    <img src="/assets/icons/check-circle.svg" alt="" width="20" height="20" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="pricing-cta">
              <Link to="/interviewer/step1" className="btn btn-primary btn-xlarge">
                {t('pricing.cta')}
              </Link>
            </div>

            <p className="pricing-note">{t('pricing.note')}</p>
          </div>
        </div>
      </section>

      {/* Why Free Section */}
      <section className="why-free-section">
        <div className="container">
          <h2 className="section-title">{t('pricing.whyFree.title')}</h2>
          
          <div className="why-free-content">
            <div className="why-free-card">
              <h3>{t('pricing.whyFree.mission.title')}</h3>
              <p>{t('pricing.whyFree.mission.description')}</p>
            </div>

            <div className="why-free-card">
              <h3>{t('pricing.whyFree.growth.title')}</h3>
              <p>{t('pricing.whyFree.growth.description')}</p>
            </div>

            <div className="why-free-card">
              <h3>{t('pricing.whyFree.innovation.title')}</h3>
              <p>{t('pricing.whyFree.innovation.description')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison */}
      <section className="comparison-section">
        <div className="container">
          <h2 className="section-title">{t('pricing.comparison.title')}</h2>

          <div className="comparison-table-wrapper">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>{t('pricing.comparison.feature')}</th>
                  <th>{t('pricing.comparison.manual')}</th>
                  <th className="shortlist-column">{t('pricing.comparison.shortlist')}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>{t('pricing.comparison.row1.feature')}</strong></td>
                  <td>{t('pricing.comparison.row1.manual')}</td>
                  <td className="highlight">{t('pricing.comparison.row1.shortlist')}</td>
                </tr>
                <tr>
                  <td><strong>{t('pricing.comparison.row2.feature')}</strong></td>
                  <td>{t('pricing.comparison.row2.manual')}</td>
                  <td className="highlight">{t('pricing.comparison.row2.shortlist')}</td>
                </tr>
                <tr>
                  <td><strong>{t('pricing.comparison.row3.feature')}</strong></td>
                  <td>{t('pricing.comparison.row3.manual')}</td>
                  <td className="highlight">{t('pricing.comparison.row3.shortlist')}</td>
                </tr>
                <tr>
                  <td><strong>{t('pricing.comparison.row4.feature')}</strong></td>
                  <td>{t('pricing.comparison.row4.manual')}</td>
                  <td className="highlight">{t('pricing.comparison.row4.shortlist')}</td>
                </tr>
                <tr>
                  <td><strong>{t('pricing.comparison.row5.feature')}</strong></td>
                  <td>{t('pricing.comparison.row5.manual')}</td>
                  <td className="highlight">{t('pricing.comparison.row5.shortlist')}</td>
                </tr>
                <tr>
                  <td><strong>{t('pricing.comparison.row6.feature')}</strong></td>
                  <td>{t('pricing.comparison.row6.manual')}</td>
                  <td className="highlight">{t('pricing.comparison.row6.shortlist')}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="faq-section">
        <div className="container">
          <h2 className="section-title">{t('pricing.faq.title')}</h2>

          <div className="faq-list">
            <div className="faq-item">
              <h3>{t('pricing.faq.q1.q')}</h3>
              <p>{t('pricing.faq.q1.a')}</p>
            </div>

            <div className="faq-item">
              <h3>{t('pricing.faq.q2.q')}</h3>
              <p>{t('pricing.faq.q2.a')}</p>
            </div>

            <div className="faq-item">
              <h3>{t('pricing.faq.q3.q')}</h3>
              <p>{t('pricing.faq.q3.a')}</p>
            </div>

            <div className="faq-item">
              <h3>{t('pricing.faq.q4.q')}</h3>
              <p>{t('pricing.faq.q4.a')}</p>
            </div>

            <div className="faq-item">
              <h3>{t('pricing.faq.q5.q')}</h3>
              <p>{t('pricing.faq.q5.a')}</p>
            </div>

            <div className="faq-item">
              <h3>{t('pricing.faq.q6.q')}</h3>
              <p>{t('pricing.faq.q6.a')}</p>
            </div>

            <div className="faq-item">
              <h3>{t('pricing.faq.q7.q')}</h3>
              <p>{t('pricing.faq.q7.a')}</p>
            </div>

            <div className="faq-item">
              <h3>{t('pricing.faq.q8.q')}</h3>
              <p>{t('pricing.faq.q8.a')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="pricing-cta-section">
        <div className="container">
          <h2 className="cta-title">{t('pricing.finalCTA.title')}</h2>
          <p className="cta-subtitle">{t('pricing.finalCTA.subtitle')}</p>
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

export default Pricing;

