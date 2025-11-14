/**
 * Admin Login Page
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import Input from '@components/Input';
import Button from '@components/Button';
import './InterviewerStep1.css';

const AdminLogin: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, isAuthenticated, loading: authLoading } = useAdminAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      navigate('/admin/dashboard');
    }
  }, [isAuthenticated, authLoading, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setLoading(true);
    setError('');
    
    try {
      const success = await login(email, password);
      
      if (success) {
        navigate('/admin/dashboard');
      } else {
        setError('Invalid username or password');
      }
      
    } catch (error: any) {
      console.error('Login error:', error);
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="step-container">
        <div className="step-content" style={{ maxWidth: '400px', textAlign: 'center' }}>
          <div className="loading-spinner"></div>
          <p>Checking authentication...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="step-container">
      <div className="step-content" style={{ maxWidth: '400px' }}>
        <h1>{t('admin.login')}</h1>
        <p className="step-subtitle">Admin Dashboard Access</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={setEmail}
              required
              placeholder="admin@shortlistai.com"
              autoComplete="email"
            />
            
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              required
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={loading}
              disabled={loading}
            >
              {t('admin.login')}
            </Button>
          </div>
          
          <div style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
            <a href="/" style={{ fontSize: 'var(--font-size-sm)' }}>
              ← Back to Home
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;

