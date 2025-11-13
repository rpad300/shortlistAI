/**
 * Privacy Policy page.
 * Displays comprehensive privacy policy with multilingual support.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Layout } from '@components/Layout';

const LegalPrivacy: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <Layout>
      <div className="step-container">
        <div className="step-content" style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem' }}>
          <h1>{t('legal.privacy')}</h1>
          
          <div style={{ 
            marginBottom: '2rem', 
            padding: '1rem', 
            backgroundColor: 'var(--color-bg-secondary)', 
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)'
          }}>
            <strong>{t('legal.base_language_notice')}</strong>
          </div>
          
          <div style={{ 
            lineHeight: '1.8', 
            color: 'var(--color-text-secondary)',
            fontSize: '0.95rem'
          }}>
            <div style={{ marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '2px solid var(--color-border)' }}>
              <p><strong>{t('legal.last_updated')}</strong>: January 8, 2025</p>
              <p><strong>{t('legal.version')}</strong>: 1.0</p>
            </div>
            
            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>1. Introduction</h2>
              <p>
                ShortlistAI ("we", "us", "our") operates a CV analysis platform. This Privacy Policy explains how we collect, use, store, and protect your personal data.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>2. Information We Collect</h2>
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>2.1 Information You Provide</h3>
                <p><strong>For All Users:</strong></p>
                <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                  <li>Name</li>
                  <li>Email address</li>
                  <li>Phone number</li>
                  <li>Country</li>
                </ul>
                <p style={{ marginTop: '1rem' }}><strong>For Interviewers:</strong></p>
                <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                  <li>Company name (optional)</li>
                  <li>Job posting content</li>
                  <li>CVs of candidates (you must have permission to upload these)</li>
                </ul>
                <p style={{ marginTop: '1rem' }}><strong>For Candidates:</strong></p>
                <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                  <li>Your CV</li>
                  <li>Job posting you're applying for</li>
                </ul>
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>2.2 Automatically Collected Information</h3>
                <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                  <li>IP address</li>
                  <li>Browser type and version</li>
                  <li>Device information</li>
                  <li>Usage patterns and analytics</li>
                  <li>Cookies and similar technologies</li>
                </ul>
              </div>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>3. How We Use Your Information</h2>
              <p>We use your information to:</p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li><strong>Provide the Service</strong>: Analyze CVs and provide insights</li>
                <li><strong>Improve Quality</strong>: Refine AI models and prompts</li>
                <li><strong>Headhunting</strong>: Match candidates to future opportunities</li>
                <li><strong>Communication</strong>: Send analysis results and relevant opportunities</li>
                <li><strong>Support</strong>: Respond to inquiries and issues</li>
              </ul>
              <p style={{ marginTop: '1rem' }}>
                <strong>Legal Bases</strong>: We process your data based on consent, legitimate interests (improving service quality), and contract (to provide the service you requested).
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>4. AI Processing and Third-Party Services</h2>
              <p>Your data is processed by external AI providers:</p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li><strong>Google Gemini</strong> - Text analysis and generation</li>
                <li><strong>OpenAI</strong> - GPT models for advanced analysis</li>
                <li><strong>Anthropic Claude</strong> - Natural language processing</li>
                <li><strong>Kimi</strong> - Alternative AI processing</li>
                <li><strong>Minimax</strong> - Alternative AI processing</li>
              </ul>
              <p style={{ marginTop: '1rem' }}>
                <strong>What We Send</strong>: Job posting text, CV text (extracted from uploaded files), and analysis prompts. We do NOT send passwords, API keys, or payment information.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>5. Data Storage and Security</h2>
              <p><strong>Where Data is Stored:</strong></p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li><strong>Database</strong>: Supabase PostgreSQL (EU region: eu-west-2, London)</li>
                <li><strong>Files</strong>: Supabase Storage (same region)</li>
                <li><strong>Backups</strong>: Automated backups within Supabase infrastructure</li>
              </ul>
              <p style={{ marginTop: '1rem' }}>
                <strong>Security Measures:</strong> Encryption at rest and in transit (HTTPS, TLS), Row Level Security (RLS) on all database tables, admin-only access to full database, regular security audits, and API rate limiting.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>6. Your Rights</h2>
              <p>Under GDPR and similar data protection laws, you have the right to:</p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li><strong>Access</strong>: Request a copy of your personal data we hold</li>
                <li><strong>Correction</strong>: Request correction of inaccurate or incomplete data</li>
                <li><strong>Deletion</strong>: Request deletion of your data, subject to legal and technical limitations</li>
                <li><strong>Portability</strong>: Request your data in a structured, machine-readable format</li>
                <li><strong>Object</strong>: Object to processing of your data for certain purposes</li>
                <li><strong>Withdraw Consent</strong>: Withdraw consent at any time</li>
                <li><strong>Lodge Complaint</strong>: Lodge a complaint with a supervisory authority</li>
              </ul>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>7. How to Exercise Your Rights</h2>
              <p>
                To exercise any of these rights, contact us at:
              </p>
              <p>
                <strong>Email</strong>: <a href={`mailto:${t('legal.contact.privacy')}`} style={{ color: 'var(--color-primary)' }}>{t('legal.contact.privacy')}</a><br />
                <strong>Subject</strong>: Data Rights Request
              </p>
              <p style={{ marginTop: '0.5rem' }}>
                We will respond within 30 days of receiving your request.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>8. Cookies and Tracking</h2>
              <p>
                We use essential cookies (authentication, session management), preference cookies (language, theme), and analytics cookies (anonymized). For detailed information, see our <Link to="/legal/cookies" style={{ color: 'var(--color-primary)' }}>Cookie Policy</Link>.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>9. Data Sharing</h2>
              <p>We share your data with:</p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li><strong>AI Providers</strong>: As described in section 4</li>
                <li><strong>Email Service</strong>: Resend (for transactional emails)</li>
                <li><strong>Infrastructure Providers</strong>: Supabase (database and storage)</li>
              </ul>
              <p style={{ marginTop: '1rem' }}>
                <strong>Important</strong>: We do NOT sell or rent your personal data to third parties for marketing purposes.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>10. International Transfers</h2>
              <p>
                Your data is primarily stored in the EU (London region). When processed by AI providers, data may be transferred to the United States (OpenAI, Google, Anthropic) or other regions. These transfers are necessary to provide the service and are covered by appropriate safeguards.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>11. Data Retention</h2>
              <p>
                <strong>Active Data</strong>: Retained indefinitely for headhunting purposes<br />
                <strong>Deleted Data</strong>: Removed from active systems within 30 days of deletion request<br />
                <strong>Backups</strong>: May be retained for up to 90 days for disaster recovery
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>12. Contact Us</h2>
              <p>
                For privacy-related questions or concerns:
              </p>
              <p>
                <strong>Email</strong>: <a href={`mailto:${t('legal.contact.privacy')}`} style={{ color: 'var(--color-primary)' }}>{t('legal.contact.privacy')}</a><br />
                <strong>Subject</strong>: Privacy Inquiry
              </p>
              <p style={{ marginTop: '1rem' }}>
                For data rights requests:
              </p>
              <p>
                <strong>Email</strong>: <a href={`mailto:${t('legal.contact.privacy')}`} style={{ color: 'var(--color-primary)' }}>{t('legal.contact.privacy')}</a><br />
                <strong>Subject</strong>: Data Rights Request
              </p>
            </section>

            <div style={{ 
              marginTop: '3rem', 
              padding: '1.5rem', 
              backgroundColor: 'var(--color-bg-secondary)', 
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border)'
            }}>
              <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>Summary of Key Points</h3>
              <ul style={{ marginLeft: '1.5rem' }}>
                <li>✅ <strong>We collect</strong>: Name, email, phone, CVs, job postings</li>
                <li>✅ <strong>We use it for</strong>: CV analysis, headhunting, service improvement</li>
                <li>✅ <strong>We share with</strong>: AI providers (Gemini, OpenAI, Claude, etc.)</li>
                <li>✅ <strong>Your rights</strong>: Access, correction, deletion, portability</li>
                <li>✅ <strong>Storage</strong>: EU region (London)</li>
                <li>✅ <strong>Contact</strong>: {t('legal.contact.privacy')}</li>
              </ul>
            </div>
          </div>
          
          <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)' }}>
            <Link to="/" style={{ color: 'var(--color-primary)', textDecoration: 'none' }}>
              {t('legal.back_to_home')}
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default LegalPrivacy;
