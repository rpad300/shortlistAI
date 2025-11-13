/**
 * Interviewer Flow - Step 3: Key Points
 * 
 * Define most important requirements and priorities.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import Textarea from '@components/Textarea';
import Button from '@components/Button';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep3: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  const [keyPoints, setKeyPoints] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);
  const [error, setError] = useState('');
  const [hasSuggestions, setHasSuggestions] = useState(false);
  
  // Load AI suggestions when component mounts
  React.useEffect(() => {
    const loadSuggestions = async () => {
      const sessionId = sessionStorage.getItem('interviewer_session_id');
      if (!sessionId) {
        setLoadingSuggestions(false);
        return;
      }
      
      try {
        const response = await interviewerAPI.step3Suggestions(sessionId);
        const data = response.data;
        
        if (data.has_suggestions && data.suggested_key_points) {
          setKeyPoints(data.suggested_key_points);
          setHasSuggestions(true);
        }
      } catch (error) {
        console.error('Could not load AI suggestions:', error);
        // Continue without suggestions
      } finally {
        setLoadingSuggestions(false);
      }
    };
    
    loadSuggestions();
  }, []);
  
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
    <StepLayout>
      <div className="step-container">
        <div className="step-content">
        <h1>{t('interviewer.step3_title')}</h1>
        <p className="step-subtitle">Review and edit AI-suggested requirements, or add your own</p>
        
        {loadingSuggestions && (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>
            <p>🤖 AI is analyzing the job posting to suggest key points...</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            {hasSuggestions && !loadingSuggestions && (
              <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-accent-light)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--spacing-md)' }}>
                <strong>✨ AI Analysis:</strong> We've analyzed your job posting and suggested key points below. 
                Feel free to edit, add, or remove anything!
              </div>
            )}
            
            <Textarea
              label={hasSuggestions ? "Key Points (AI-suggested - edit as needed)" : "Key Points and Requirements"}
              value={keyPoints}
              onChange={setKeyPoints}
              placeholder={loadingSuggestions ? "Loading AI suggestions..." : `Example:\n\n• Must have: 5+ years Python experience\n• Required: Experience with FastAPI and React\n• Languages: English (fluent), French (preferred)\n• Nice to have: Cloud platforms (AWS, GCP)\n• Must accept: Remote work`}
              required
              rows={12}
              maxLength={5000}
              disabled={loadingSuggestions}
            />
            
            <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <strong>💡 Tip:</strong> {hasSuggestions 
                ? "Review the AI suggestions and add any specific requirements or hard blockers for your role." 
                : "Be specific about must-have skills, experience level, and any hard requirements."}
            </div>
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/interviewer/step2')}
            >
              {t('common.back')}
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
    </StepLayout>
  );
};

export default InterviewerStep3;

