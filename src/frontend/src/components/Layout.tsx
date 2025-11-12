/**
 * Layout Component
 * 
 * Provides consistent layout with Navbar, Footer, and AnimatedBackground
 * for all pages.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Logo from './Logo';
import Navbar from './Navbar';
import AnimatedBackground from './AnimatedBackground';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
  backgroundIntensity?: 'low' | 'medium' | 'high';
  showFooter?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ 
  children, 
  backgroundIntensity = 'medium',
  showFooter = true 
}) => {
  const { t } = useTranslation();

  const changeLanguage = (lang: string) => {
    localStorage.setItem('language', lang);
    window.location.reload();
  };

  return (
    <>
      <AnimatedBackground intensity={backgroundIntensity} />
      
      <div className="layout">
        <Navbar />
        
        <main className="layout-main">
          {children}
        </main>

        {showFooter && (
          <footer className="layout-footer">
            <div className="container">
              <div className="footer-grid">
                <div className="footer-brand">
                  <Logo width={160} height={40} variant="auto" />
                  <p className="footer-tagline">{t('footer.tagline')}</p>
                  <p className="footer-description">{t('footer.description')}</p>
                </div>

                <div className="footer-links">
                  <h4>{t('footer.product')}</h4>
                  <ul>
                    <li><Link to="/interviewer/step1">{t('home.features.interviewer.title')}</Link></li>
                    <li><Link to="/candidate/step1">{t('home.features.candidate.title')}</Link></li>
                    <li><Link to="/features">{t('nav.features')}</Link></li>
                    <li><Link to="/how-it-works">{t('nav.about')}</Link></li>
                  </ul>
                </div>

                <div className="footer-links">
                  <h4>{t('footer.company')}</h4>
                  <ul>
                    <li><Link to="/about">{t('nav.about')}</Link></li>
                    <li><Link to="/pricing">{t('nav.pricing')}</Link></li>
                    <li><a href="mailto:privacy@shortlistai.com">Contact</a></li>
                  </ul>
                </div>

                <div className="footer-links">
                  <h4>{t('footer.legal')}</h4>
                  <ul>
                    <li><a href="/legal/terms">{t('legal.terms')}</a></li>
                    <li><a href="/legal/privacy">{t('legal.privacy')}</a></li>
                    <li><a href="/legal/cookies">{t('legal.cookies')}</a></li>
                    <li><a href="/admin/login" className="admin-link">{t('footer.admin')}</a></li>
                  </ul>
                </div>

                <div className="footer-links">
                  <h4>{t('footer.languages')}</h4>
                  <ul>
                    <li><button onClick={() => changeLanguage('en')}>🇬🇧 {t('languages.en')}</button></li>
                    <li><button onClick={() => changeLanguage('pt')}>🇵🇹 {t('languages.pt')}</button></li>
                    <li><button onClick={() => changeLanguage('fr')}>🇫🇷 {t('languages.fr')}</button></li>
                    <li><button onClick={() => changeLanguage('es')}>🇪🇸 {t('languages.es')}</button></li>
                  </ul>
                </div>
              </div>

              <div className="footer-bottom">
                <p className="footer-copyright">{t('footer.copyright')}</p>
                <p className="footer-powered">{t('footer.powered')}</p>
              </div>
            </div>
          </footer>
        )}
      </div>
    </>
  );
};

export default Layout;

