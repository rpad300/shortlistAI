/**
 * Interviewer Flow - Step 4: Weighting and Hard Blockers
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Input from '@components/Input';
import Textarea from '@components/Textarea';
import Button from '@components/Button';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep4: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  const [weights, setWeights] = useState({
    technical_skills: 40,
    experience: 25,
    soft_skills: 15,
    languages: 10,
    education: 10
  });
  
  const [hardBlockers, setHardBlockers] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      setError('Session not found.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const blockersArray = hardBlockers
        .split('\n')
        .map(b => b.trim())
        .filter(b => b.length > 0);
      
      await interviewerAPI.step4({
        session_id: sessionId,
        weights: weights,
        hard_blockers: blockersArray,
        language: i18n.language
      });
      
      navigate('/interviewer/step5');
      
    } catch (error: any) {
      console.error('Error in step 4:', error);
      setError(error.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content" style={{ maxWidth: '700px' }}>
        <h1>{t('interviewer.step4_title')}</h1>
        <p className="step-subtitle">Configure scoring weights and must-have requirements</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <h2>Category Weights (Total: {totalWeight}%)</h2>
            
            {Object.entries(weights).map(([key, value]) => (
              <div key={key} style={{ marginBottom: 'var(--spacing-md)' }}>
                <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-xs)' }}>
                  <span>{key.replace('_', ' ').toUpperCase()}</span>
                  <span><strong>{value}%</strong></span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={value}
                  onChange={(e) => setWeights({ ...weights, [key]: parseInt(e.target.value) })}
                  style={{ width: '100%' }}
                />
              </div>
            ))}
            
            {(totalWeight < 90 || totalWeight > 110) && (
              <div style={{ padding: 'var(--spacing-sm)', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderRadius: 'var(--radius-md)', marginTop: 'var(--spacing-md)' }}>
                ⚠️ Total weight should be close to 100% (current: {totalWeight}%)
              </div>
            )}
          </div>
          
          <div className="form-section">
            <Textarea
              label="Hard Blockers (one per line)"
              value={hardBlockers}
              onChange={setHardBlockers}
              placeholder={`Example:\nMust speak French\nMust have 5+ years experience\nMust accept on-site work`}
              rows={5}
            />
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button type="button" variant="outline" onClick={() => navigate('/interviewer/step3')}>
              {t('common.previous')}
            </Button>
            <Button type="submit" variant="primary" loading={loading} disabled={loading}>
              {t('common.next')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InterviewerStep4;

