/**
 * Privacy Policy page.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const LegalPrivacy: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <div className="step-container">
      <div className="step-content" style={{ maxWidth: '800px' }}>
        <h1>{t('legal.privacy')}</h1>
        
        <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)' }}>
          <strong>{t('legal.base_language_notice')}</strong>
        </div>
        
        <div style={{ lineHeight: '1.8', color: 'var(--color-text-secondary)' }}>
          <h2>Privacy Policy</h2>
          <p><strong>Last Updated</strong>: January 8, 2025</p>
          <p><strong>Version</strong>: 1.0</p>
          
          <h3>Information We Collect</h3>
          <p>We collect name, email, phone, country, CVs, job postings, and AI analysis results.</p>
          
          <h3>How We Use Your Data</h3>
          <p>To provide CV analysis, improve our service, build a headhunting database, and contact you about opportunities.</p>
          
          <h3>AI Processing</h3>
          <p>Your data is processed by Google Gemini, OpenAI, Anthropic Claude, and other AI providers.</p>
          
          <h3>Data Storage</h3>
          <p>Stored in Supabase PostgreSQL (EU region: London) with encryption and security measures.</p>
          
          <h3>Your Rights (GDPR)</h3>
          <ul>
            <li>Access your data</li>
            <li>Correct inaccurate data</li>
            <li>Request deletion</li>
            <li>Data portability</li>
            <li>Object to processing</li>
          </ul>
          
          <h3>Contact for Privacy</h3>
          <p><strong>Email</strong>: privacy@shortlistai.com</p>
          
          <p style={{ marginTop: '2rem' }}>
            <strong>For full privacy policy</strong>, see docs/legal/privacy-en.md
          </p>
        </div>
        
        <div style={{ marginTop: '2rem' }}>
          <Link to="/">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default LegalPrivacy;

