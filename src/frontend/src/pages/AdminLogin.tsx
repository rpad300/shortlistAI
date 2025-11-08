/**
 * Admin Login Page
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Input from '@components/Input';
import Button from '@components/Button';
import api from '@services/api';
import './InterviewerStep1.css';

const AdminLogin: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/api/admin/login', {
        username,
        password
      });
      
      const { access_token } = response.data;
      
      // Store token
      localStorage.setItem('admin_token', access_token);
      
      // Redirect to admin dashboard
      alert('Login successful! Admin dashboard coming soon...');
      navigate('/');
      
    } catch (error: any) {
      console.error('Login error:', error);
      setError(error.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content" style={{ maxWidth: '400px' }}>
        <h1>{t('admin.login')}</h1>
        <p className="step-subtitle">Admin Dashboard Access</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <Input
              label="Username"
              value={username}
              onChange={setUsername}
              required
              placeholder="admin"
            />
            
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              required
              placeholder="••••••••"
            />
            
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-tertiary)', marginTop: 'var(--spacing-md)' }}>
              <strong>Default credentials (MVP):</strong><br/>
              Username: admin<br/>
              Password: admin123
            </div>
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

