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
        
        <div className="analysis-loading-container">
          <div className="loading-spinner-modern"></div>
          
          <p className="analysis-status-text">
            {status}
          </p>
          
          <p className="analysis-time-text">
            This usually takes 10-15 seconds...
          </p>
        </div>
      </div>
    </div>
    </StepLayout>
  );
};

export default CandidateStep4;

