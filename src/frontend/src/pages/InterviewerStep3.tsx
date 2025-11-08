/**
 * Interviewer Flow - Step 3: Key Points
 * 
 * Define most important requirements and priorities.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Textarea from '@components/Textarea';
import Button from '@components/Button';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep3: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  const [keyPoints, setKeyPoints] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      setError('Session not found. Please start from Step 1.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await interviewerAPI.step3({
        session_id: sessionId,
        key_points: keyPoints,
        language: i18n.language
      });
      
      navigate('/interviewer/step4');
      
    } catch (error: any) {
      console.error('Error in step 3:', error);
      setError(error.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content">
        <h1>{t('interviewer.step3_title')}</h1>
        <p className="step-subtitle">Define the most important skills and requirements</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <Textarea
              label="Key Points and Requirements"
              value={keyPoints}
              onChange={setKeyPoints}
              placeholder={`Example:\n\n• Must have: 5+ years Python experience\n• Required: Experience with FastAPI and React\n• Languages: English (fluent), French (preferred)\n• Nice to have: Cloud platforms (AWS, GCP)\n• Must accept: Remote work`}
              required
              rows={12}
              maxLength={5000}
            />
            
            <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <strong>Tip:</strong> Be specific about must-have skills, experience level, and any hard requirements.
            </div>
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/interviewer/step2')}
            >
              {t('common.previous')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={loading}
            >
              {t('common.next')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InterviewerStep3;

