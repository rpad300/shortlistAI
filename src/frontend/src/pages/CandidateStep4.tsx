/**
 * Candidate Flow - Step 4: AI Analysis (Loading)
 * 
 * Triggers AI analysis and shows loading state.
 */

import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import { candidateAPI } from '@services/api';
import './InterviewerStep1.css';

const CandidateStep4: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [status, setStatus] = useState('Starting analysis...');
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);
  
  useEffect(() => {
    const runAnalysis = async () => {
      const sessionId = sessionStorage.getItem('candidate_session_id');
      if (!sessionId) {
        setStatus('Error: Session not found');
        return;
      }
      
      try {
        setStatus('Starting analysis...');
        
        // Start analysis (returns immediately)
        const response = await candidateAPI.step4(sessionId);
        
        if (response.data.status === 'already_running') {
          setStatus('Analysis already in progress...');
        } else {
          setStatus('Analysis started! Processing...');
        }
        
        // Start polling for progress
        pollIntervalRef.current = setInterval(async () => {
          try {
            const progressResponse = await candidateAPI.step4Progress(sessionId);
            const progressData = progressResponse.data;
            
            const progressInfo = progressData.progress || {};
            const statusText = progressInfo.status || 'Processing...';
            
            setStatus(statusText);
            
            // Check if complete
            if (progressData.complete) {
              if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
                pollIntervalRef.current = null;
              }
              
              setStatus('Analysis complete! Preparing your results...');
              
              // Navigate to results after a short delay
              setTimeout(() => {
                navigate('/candidate/step5');
              }, 1500);
              return;
            }
            
            // Check if error
            if (progressData.status === 'error') {
              if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
                pollIntervalRef.current = null;
              }
              setStatus('Error: ' + (progressInfo.status || 'Analysis failed'));
              return;
            }
          } catch (pollError: any) {
            // Don't show error for polling timeouts, just continue
            if (pollError.code !== 'ECONNABORTED' && !pollError.message?.includes('timeout')) {
              console.error('Error polling analysis progress:', pollError);
              
              // If session expired, stop polling
              if (pollError.response?.status === 404) {
                if (pollIntervalRef.current) {
                  clearInterval(pollIntervalRef.current);
                  pollIntervalRef.current = null;
                }
                setStatus('Error: Session expired. Please restart from step 1.');
              }
            }
          }
        }, 2000); // Poll every 2 seconds
        
        // Cleanup after 5 minutes max
        setTimeout(() => {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          if (status.includes('Processing') || status.includes('Analyzing')) {
            setStatus('Error: Analysis took too long. Please try again.');
          }
        }, 300000); // 5 minutes max
        
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

