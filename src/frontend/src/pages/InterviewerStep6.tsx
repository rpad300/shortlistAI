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
  const [currentCv, setCurrentCv] = useState(0);
  const [totalCvs, setTotalCvs] = useState(0);
  
  useEffect(() => {
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      setStatus('Error: Session not found. Please restart from step 1.');
      setProgress(0);
      setTimeout(() => {
        navigate('/interviewer/step1');
      }, 3000);
      return;
    }
    
    let pollInterval: ReturnType<typeof setInterval> | null = null;
    let isMounted = true;
    
    const startAnalysis = async () => {
      try {
        setStatus('Starting analysis...');
        setProgress(5);
        
        // Start analysis (returns immediately)
        const response = await interviewerAPI.step6(sessionId);
        
        if (response.data.status === 'already_running') {
          // Analysis already running, just poll
          setStatus('Analysis already in progress...');
        } else {
          setStatus('Analysis started! Processing CVs...');
          setTotalCvs(response.data.total_cvs || 0);
        }
        
        // Start polling for progress
        pollInterval = setInterval(async () => {
          try {
            const progressResponse = await interviewerAPI.step6Progress(sessionId);
            const progressData = progressResponse.data;
            
            if (!isMounted) return;
            
            const progressInfo = progressData.progress || {};
            const current = progressInfo.current || 0;
            const total = progressInfo.total || totalCvs || 1;
            const statusText = progressInfo.status || 'Processing...';
            
            setCurrentCv(current);
            setTotalCvs(total);
            setStatus(statusText);
            
            // Calculate progress percentage
            const progressPercent = total > 0 ? Math.min(95, (current / total) * 100) : 20;
            setProgress(progressPercent);
            
            // Check if complete
            if (progressData.complete) {
              if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
              }
              
              setProgress(100);
              setStatus('Analysis complete! Preparing results...');
              
              // Navigate to results after short delay
              setTimeout(() => {
                if (isMounted) {
                  navigate('/interviewer/step7');
                }
              }, 1500);
            } else if (progressData.status === 'error') {
              if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
              }
              
              setStatus(`Error: ${progressInfo.status || 'Analysis failed'}`);
              setProgress(0);
            }
          } catch (pollError: any) {
            // Don't log timeout errors as they're expected during long operations
            const isTimeout = pollError.code === 'ECONNABORTED' || pollError.message?.includes('timeout');
            if (!isTimeout) {
              console.error('Error polling progress:', pollError);
            }
            
            // Continue polling unless it's a 404 (session expired)
            // Timeouts are OK - we'll retry on next poll
            if (pollError.response?.status === 404) {
              if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
              }
              
              sessionStorage.removeItem('interviewer_session_id');
              sessionStorage.removeItem('interviewer_id');
              sessionStorage.removeItem('interviewer_report_code');
              setStatus('Session expired. Redirecting...');
              setTimeout(() => {
                if (isMounted) {
                  navigate('/interviewer/step1');
                }
              }, 3000);
            }
            // For timeouts, just continue polling - don't break the loop
          }
        }, 3000); // Poll every 3 seconds (reduces server load)
        
      } catch (error: any) {
        console.error('Error starting analysis:', error);
        const errorDetail = error.response?.data?.detail || 'Failed to start analysis';
        setStatus(`Error: ${errorDetail}`);
        setProgress(0);
        
        // If session expired, redirect to step 1
        if (error.response?.status === 404 && errorDetail.includes('Session')) {
          sessionStorage.removeItem('interviewer_session_id');
          sessionStorage.removeItem('interviewer_id');
          sessionStorage.removeItem('interviewer_report_code');
          setTimeout(() => {
            navigate('/interviewer/step1');
          }, 3000);
        }
      }
    };
    
    startAnalysis();
    
    // Cleanup on unmount
    return () => {
      isMounted = false;
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [navigate, totalCvs]);
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content">
        <h1>{t('interviewer.step6_title')}</h1>
        <p className="step-subtitle">AI is analyzing all candidates against your job posting</p>
        
        <div className="analysis-loading-container">
          <div className="loading-spinner-modern"></div>
          
          <p className="analysis-status-text">
            {status}
          </p>
          
          {/* Progress bar */}
          <div className="progress-bar-container">
            <div 
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          
          {totalCvs > 0 && (
            <p className="analysis-progress-text">
              Analyzing CV {currentCv} of {totalCvs}...
            </p>
          )}
          <p className="analysis-time-text">
            {totalCvs > 0 
              ? `This may take ${Math.ceil(totalCvs * 2)}-${Math.ceil(totalCvs * 5)} minutes for ${totalCvs} CV${totalCvs > 1 ? 's' : ''}...`
              : 'This may take a few minutes for multiple CVs...'}
          </p>
        </div>
      </div>
    </div>
    </StepLayout>
  );
};

export default InterviewerStep6;

