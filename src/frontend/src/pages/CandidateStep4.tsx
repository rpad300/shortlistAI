/**
 * Candidate Flow - Step 4: AI Analysis (Loading)
 * 
 * Triggers AI analysis and shows loading state.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import { candidateAPI } from '@services/api';
import './InterviewerStep1.css';

const CandidateStep4: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [status, setStatus] = useState('Starting analysis...');
  
  useEffect(() => {
    const runAnalysis = async () => {
      const sessionId = sessionStorage.getItem('candidate_session_id');
      if (!sessionId) {
        setStatus('Error: Session not found');
        return;
      }
      
      try {
        setStatus('Analyzing your CV against the job posting...');
        await candidateAPI.step4(sessionId);
        
        setStatus('Analysis complete! Preparing your results...');
        
        // Navigate to results after a short delay
        setTimeout(() => {
          navigate('/candidate/step5');
        }, 1500);
        
      } catch (error: any) {
        console.error('Error in analysis:', error);
        setStatus('Error: ' + (error.response?.data?.detail || 'Analysis failed'));
      }
    };
    
    runAnalysis();
  }, [navigate]);
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content">
        <h1>{t('candidate.step4_title')}</h1>
        <p className="step-subtitle">AI is analyzing your fit for this position</p>
        
        <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
          <div className="loading-spinner" style={{
            width: '64px',
            height: '64px',
            border: '4px solid var(--color-border)',
            borderTop: '4px solid var(--color-accent-primary)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto var(--spacing-xl)'
          }}></div>
          
          <p style={{ fontSize: 'var(--font-size-lg)', color: 'var(--color-text-primary)' }}>
            {status}
          </p>
          
          <p style={{ marginTop: 'var(--spacing-lg)', color: 'var(--color-text-tertiary)' }}>
            This usually takes 10-15 seconds...
          </p>
        </div>
      </div>
    </div>
    </StepLayout>
  );
};

export default CandidateStep4;

