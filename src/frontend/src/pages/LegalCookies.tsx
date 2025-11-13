/**
 * Cookie Policy page.
 * Displays comprehensive cookie policy with multilingual support.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Layout } from '@components/Layout';

const LegalCookies: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <Layout>
      <div className="step-container">
        <div className="step-content" style={{ maxWidth: '900px', margin: '0 auto', padding: '2rem' }}>
          <h1>{t('legal.cookies')}</h1>
          
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
                This Cookie Policy explains how ShortlistAI ("we", "us", "our") uses cookies and similar tracking technologies on our CV Analysis Platform ("Platform"). This policy should be read together with our <Link to="/legal/privacy" style={{ color: 'var(--color-primary)' }}>Privacy Policy</Link> and <Link to="/legal/terms" style={{ color: 'var(--color-primary)' }}>Terms and Conditions</Link>.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>2. What Are Cookies?</h2>
              <p>
                Cookies are small text files that are placed on your device (computer, tablet, or mobile) when you visit a website. They are widely used to make websites work more efficiently and provide information to website owners.
              </p>
              <p>Cookies can be:</p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li><strong>Session cookies</strong>: Temporary cookies that expire when you close your browser</li>
                <li><strong>Persistent cookies</strong>: Cookies that remain on your device for a set period or until you delete them</li>
                <li><strong>First-party cookies</strong>: Set by the website you are visiting</li>
                <li><strong>Third-party cookies</strong>: Set by other services (e.g., analytics providers)</li>
              </ul>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>3. Types of Cookies We Use</h2>
              
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.75rem' }}>3.1 Strictly Necessary Cookies</h3>
                <p>
                  These cookies are essential for the Platform to function properly. They enable core functionality such as:
                </p>
                <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                  <li><strong>Session Management</strong>: Maintaining your session while you use the Platform</li>
                  <li><strong>Authentication</strong>: Keeping you logged in (for Admin users)</li>
                  <li><strong>Security</strong>: Protecting against fraud and abuse</li>
                  <li><strong>Consent Management</strong>: Remembering your cookie preferences</li>
                </ul>
                <p style={{ marginTop: '0.75rem', fontStyle: 'italic' }}>
                  <strong>Legal Basis</strong>: These cookies are necessary for the performance of a contract (providing the service you requested). They cannot be disabled.
                </p>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.75rem' }}>3.2 Functionality Cookies</h3>
                <p>
                  These cookies allow the Platform to remember choices you make and provide enhanced, personalized features:
                </p>
                <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                  <li><strong>Language Preference</strong>: Remembering your selected language (English, Portuguese, French, Spanish)</li>
                  <li><strong>Theme Preference</strong>: Remembering your light/dark mode preference</li>
                  <li><strong>UI Preferences</strong>: Remembering interface settings and preferences</li>
                </ul>
                <p style={{ marginTop: '0.75rem', fontStyle: 'italic' }}>
                  <strong>Legal Basis</strong>: These cookies are based on your consent. You can disable them, but some features may not work as expected.
                </p>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.75rem' }}>3.3 Analytics Cookies</h3>
                <p>
                  These cookies help us understand how visitors interact with the Platform by collecting and reporting information anonymously:
                </p>
                <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                  <li><strong>Usage Statistics</strong>: Page views, session duration, bounce rates</li>
                  <li><strong>Performance Metrics</strong>: Load times, error rates</li>
                  <li><strong>User Flow</strong>: How users navigate through the Platform</li>
                  <li><strong>Feature Adoption</strong>: Which features are most used</li>
                </ul>
                <p style={{ marginTop: '0.75rem', fontStyle: 'italic' }}>
                  <strong>Legal Basis</strong>: These cookies require your consent. We use anonymized data that cannot identify you personally.
                </p>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ color: 'var(--color-text-primary)', marginBottom: '0.75rem' }}>3.4 Marketing Cookies (Currently Not Used)</h3>
                <p>
                  We currently do NOT use marketing or advertising cookies. If we introduce them in the future, we will update this policy and request your consent.
                </p>
              </div>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>4. Third-Party Cookies</h2>
              <p>
                Currently, we do NOT use third-party cookies. If we add any analytics services (e.g., Google Analytics) in the future, they will be listed here with links to their privacy policies.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>5. Local Storage and Similar Technologies</h2>
              <p>
                In addition to cookies, we use browser local storage to:
              </p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li>Store your language preference</li>
                <li>Store your theme preference (light/dark mode)</li>
                <li>Cache UI state for better performance</li>
              </ul>
              <p style={{ marginTop: '0.75rem' }}>
                <strong>Data Stored</strong>: Language code (en, pt, fr, es), theme preference (light, dark), and other non-personal, non-identifiable UI state.
              </p>
              <p style={{ marginTop: '0.5rem' }}>
                <strong>Retention</strong>: Data persists until you clear your browser storage or change preferences.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>6. How to Manage Cookies</h2>
              <p>
                You can control cookies through your browser settings. Most browsers allow you to:
              </p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li>See what cookies you have and delete them individually</li>
                <li>Block third-party cookies</li>
                <li>Block all cookies</li>
                <li>Delete all cookies when you close your browser</li>
                <li>Get notified when a cookie is set</li>
              </ul>
              <p style={{ marginTop: '1rem' }}>
                <strong>Impact of Disabling Cookies</strong>: If you disable cookies, the Platform may not function properly. Your preferences (language, theme) will not be saved, and we will not be able to improve the Platform based on usage data.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>7. Cookies We Currently Use</h2>
              <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ backgroundColor: 'var(--color-bg-secondary)' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid var(--color-border)' }}>Cookie Name</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid var(--color-border)' }}>Purpose</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid var(--color-border)' }}>Type</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', border: '1px solid var(--color-border)' }}>Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}><code>session_id</code></td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Session management</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Strictly Necessary</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Session</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}><code>auth_token</code></td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Admin authentication</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Strictly Necessary</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>24 hours</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}><code>csrf_token</code></td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Security protection</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Strictly Necessary</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Session</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}><code>i18next</code></td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Language preference</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Functionality</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>1 year</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}><code>theme</code></td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Theme preference</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>Functionality</td>
                      <td style={{ padding: '0.75rem', border: '1px solid var(--color-border)' }}>1 year</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>8. Updates to This Policy</h2>
              <p>
                We may update this Cookie Policy from time to time to reflect changes in our use of cookies, new features or services, legal or regulatory requirements, or user feedback. We will update the "Last Updated" date at the top of this policy. For significant changes, we may notify you via email or a notice on the Platform.
              </p>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>9. Your Rights</h2>
              <p>
                Under GDPR and similar data protection laws, you have the right to:
              </p>
              <ul style={{ marginLeft: '2rem', marginTop: '0.5rem' }}>
                <li><strong>Be Informed</strong>: Know what cookies we use and why</li>
                <li><strong>Give Consent</strong>: Choose which cookies to accept</li>
                <li><strong>Withdraw Consent</strong>: Change your cookie preferences at any time</li>
                <li><strong>Access</strong>: Request information about cookies we use</li>
                <li><strong>Delete</strong>: Clear cookies from your device at any time</li>
              </ul>
            </section>

            <section style={{ marginBottom: '2.5rem' }}>
              <h2 style={{ color: 'var(--color-text-primary)', marginBottom: '1rem' }}>10. Contact Us</h2>
              <p>
                For questions about our use of cookies:
              </p>
              <p>
                <strong>Email</strong>: <a href={`mailto:${t('legal.contact.privacy')}`} style={{ color: 'var(--color-primary)' }}>{t('legal.contact.privacy')}</a><br />
                <strong>Subject</strong>: Cookie Policy Inquiry
              </p>
              <p style={{ marginTop: '1rem' }}>
                For data protection questions, see our <Link to="/legal/privacy" style={{ color: 'var(--color-primary)' }}>Privacy Policy</Link>.
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
                <li>✅ <strong>We use</strong>: Essential cookies (session, auth), functionality cookies (language, theme), analytics cookies (anonymized)</li>
                <li>✅ <strong>We do NOT use</strong>: Marketing or advertising cookies</li>
                <li>✅ <strong>Third-party cookies</strong>: Currently none (if added, will be listed)</li>
                <li>✅ <strong>Your control</strong>: Manage cookies through browser settings or our consent tool</li>
                <li>✅ <strong>Local storage</strong>: Used for preferences (language, theme)</li>
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

export default LegalCookies;

