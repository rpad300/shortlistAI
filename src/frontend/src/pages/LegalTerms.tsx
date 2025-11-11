/**
 * Terms and Conditions page.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const LegalTerms: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <div className="step-container">
      <div className="step-content" style={{ maxWidth: '800px' }}>
        <h1>{t('legal.terms')}</h1>
        
        <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)' }}>
          <strong>{t('legal.base_language_notice')}</strong>
        </div>
        
        <div style={{ lineHeight: '1.8', color: 'var(--color-text-secondary)' }}>
          <h2>Terms and Conditions</h2>
          <p><strong>Last Updated</strong>: January 8, 2025</p>
          <p><strong>Version</strong>: 1.0</p>
          
          <h3>1. Acceptance of Terms</h3>
          <p>By accessing and using the ShortlistAI CV Analysis Platform, you agree to be bound by these Terms and Conditions.</p>
          
          <h3>2. Description of Service</h3>
          <p>ShortlistAI provides a free, AI-powered CV analysis service for interviewers and candidates.</p>
          
          <h3>3. Data Collection</h3>
          <p>We collect personal information, CVs, job postings, and analysis results to provide our service and build a headhunting database.</p>
          
          <h3>4. AI Processing</h3>
          <p>Your data may be processed by external AI providers including Google Gemini, OpenAI, Anthropic Claude, and others.</p>
          
          <h3>5. User Rights</h3>
          <p>You have the right to access, correct, and request deletion of your data. Contact us at privacy@shortlistai.com.</p>
          
          <h3>6. Liability</h3>
          <p>The service is provided "as is" without warranties. AI analysis is advisory only and should not be the sole basis for decisions.</p>
          
          <p style={{ marginTop: '2rem' }}>
            <strong>For full legal terms</strong>, see the complete English version at docs/legal/terms-en.md
          </p>
        </div>
        
        <div style={{ marginTop: '2rem' }}>
          <Link to="/">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default LegalTerms;

