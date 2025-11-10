/**
 * Navbar Component
 * 
 * Modern navigation bar with glassmorphism, sticky positioning,
 * theme switcher, and language selector.
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Logo from './Logo';
import ThemeSwitcher from './ThemeSwitcher';
import LanguageSelector from './LanguageSelector';
import './Navbar.css';

export const Navbar: React.FC = () => {
  const { t } = useTranslation();
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Handle scroll for glassmorphism effect
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location]);

  const navLinks = [
    { to: '/', label: t('nav.home') },
    { to: '/features', label: t('nav.features') },
    { to: '/about', label: t('nav.about') },
    { to: '/pricing', label: t('nav.pricing') }
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <Logo width={160} height={40} variant="auto" />
        </Link>

        {/* Desktop Navigation */}
        <div className="navbar-links">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`navbar-link ${isActive(link.to) ? 'active' : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* CTA Buttons */}
        <div className="navbar-actions">
          <Link to="/interviewer/step1" className="navbar-btn navbar-btn-primary">
            {t('nav.analyzeCV')}
          </Link>
          <Link to="/candidate/step1" className="navbar-btn navbar-btn-secondary">
            {t('nav.prepareInterview')}
          </Link>
        </div>

        {/* Theme & Language Controls */}
        <div className="navbar-controls">
          <ThemeSwitcher />
          <LanguageSelector />
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="navbar-mobile-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
          aria-expanded={mobileMenuOpen}
        >
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="navbar-mobile-menu">
          <div className="navbar-mobile-links">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={`navbar-mobile-link ${isActive(link.to) ? 'active' : ''}`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="navbar-mobile-actions">
            <Link to="/interviewer/step1" className="navbar-btn navbar-btn-primary navbar-btn-full">
              Analyze CVs
            </Link>
            <Link to="/candidate/step1" className="navbar-btn navbar-btn-secondary navbar-btn-full">
              Prepare Interview
            </Link>
          </div>

          <div className="navbar-mobile-controls">
            <ThemeSwitcher />
            <LanguageSelector />
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;

