/**
 * Interviewer Flow - Step 6: AI Analysis (Processing)
 * 
 * Triggers AI analysis and shows progress.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep6: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [status, setStatus] = useState('Preparing analysis...');
  const [progress, setProgress] = useState(0);
  
  useEffect(() => {
    const runAnalysis = async () => {
      const sessionId = sessionStorage.getItem('interviewer_session_id');
      if (!sessionId) {
        setStatus('Error: Session not found');
        return;
      }
      
      try {
        setStatus('Analyzing CVs with AI...');
        setProgress(20);
        
        const response = await interviewerAPI.step6(sessionId);
        
        setProgress(80);
        setStatus('Analysis complete! Preparing results...');
        
        const { analyses_created } = response.data;
        
        setProgress(100);
        setStatus(`Successfully analyzed ${analyses_created} candidates!`);
        
        // Navigate to results after short delay
        setTimeout(() => {
          navigate('/interviewer/step7');
        }, 1500);
        
      } catch (error: any) {
        console.error('Error in analysis:', error);
        setStatus('Error: ' + (error.response?.data?.detail || 'Analysis failed'));
        setProgress(0);
      }
    };
    
    runAnalysis();
  }, [navigate]);
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content">
        <h1>{t('interviewer.step6_title')}</h1>
        <p className="step-subtitle">AI is analyzing all candidates against your job posting</p>
        
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
          
          <p style={{ fontSize: 'var(--font-size-lg)', color: 'var(--color-text-primary)', marginBottom: 'var(--spacing-lg)' }}>
            {status}
          </p>
          
          {/* Progress bar */}
          <div style={{
            width: '100%',
            maxWidth: '400px',
            height: '8px',
            backgroundColor: 'var(--color-bg-secondary)',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            margin: '0 auto'
          }}>
            <div style={{
              width: `${progress}%`,
              height: '100%',
              backgroundColor: 'var(--color-accent-primary)',
              transition: 'width 0.5s ease-in-out'
            }}></div>
          </div>
          
          <p style={{ marginTop: 'var(--spacing-lg)', color: 'var(--color-text-tertiary)' }}>
            This may take 20-30 seconds for multiple CVs...
          </p>
        </div>
      </div>
    </div>
    </StepLayout>
  );
};

export default InterviewerStep6;

