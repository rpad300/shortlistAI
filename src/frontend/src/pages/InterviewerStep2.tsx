/**
 * Interviewer Flow - Step 2: Job Posting Input
 * 
 * Accepts job posting as text or file upload.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import Textarea from '@components/Textarea';
import FileUpload from '@components/FileUpload';
import Button from '@components/Button';
import StepHelper from '@components/StepHelper';
import AILoadingOverlay from '@components/AILoadingOverlay';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep2: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  const [jobText, setJobText] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [useFile, setUseFile] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [processingStatus, setProcessingStatus] = useState('');
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      setError('Session not found. Please start from Step 1.');
      return;
    }
    
    if (!jobText && files.length === 0) {
      setError('Please provide job posting text or upload a file.');
      return;
    }
    
    setLoading(true);
    setError('');
    setProcessingStatus('Starting processing...');
    
    try {
      let formData: FormData;
      
      // Se usar file upload
      if (useFile && files.length > 0) {
        formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('language', i18n.language);
        formData.append('file', files[0]);
      } else if (!useFile && jobText.trim()) {
        // Se usar texto
        formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('language', i18n.language);
        formData.append('raw_text', jobText);
      } else {
        setError('Por favor, forneça o job posting como texto ou upload de ficheiro.');
        setLoading(false);
        return;
      }
      
      // Start processing (returns immediately)
      const response = await interviewerAPI.step2(formData);
      
      if (response.data.status === 'already_running') {
        setProcessingStatus('Processing already in progress...');
      } else {
        setProcessingStatus('Processing started...');
      }
      
      // Start polling for progress
      pollIntervalRef.current = setInterval(async () => {
        try {
          const progressResponse = await interviewerAPI.step2Progress(sessionId);
          const progressData = progressResponse.data;
          
          const progressInfo = progressData.progress || {};
          const statusText = progressInfo.status || 'Processing...';
          
          setProcessingStatus(statusText);
          
          // Check if complete
          if (progressData.complete) {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            setLoading(false);
            navigate('/interviewer/step3');
            return;
          }
          
          // Check if error
          if (progressData.status === 'error') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            setLoading(false);
            setError(progressInfo.status || 'An error occurred during processing.');
            return;
          }
        } catch (pollError: any) {
          // Don't show error for polling timeouts, just continue
          if (pollError.code !== 'ECONNABORTED' && !pollError.message?.includes('timeout')) {
            console.error('Error polling progress:', pollError);
            
            // If session expired, stop polling
            if (pollError.response?.status === 404) {
              if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
                pollIntervalRef.current = null;
              }
              setLoading(false);
              setError('Session expired. Please restart from step 1.');
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
        if (loading) {
          setLoading(false);
          setError('Processing took too long. Please try again.');
        }
      }, 300000); // 5 minutes max
      
    } catch (error: any) {
      console.error('Error in step 2:', error);
      
      const errorDetail = error.response?.data?.detail;
      const errorMessage = Array.isArray(errorDetail) 
        ? errorDetail.map((e: any) => e.msg || e).join(', ')
        : typeof errorDetail === 'string' 
          ? errorDetail 
          : 'An error occurred. Please try again.';
      setError(errorMessage);
      setLoading(false);
    }
  };
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content">
        <h1>{t('interviewer.step2_title')}</h1>
        <p className="step-subtitle">Provide the job posting you want to analyze CVs against</p>
        
        <StepHelper
          title="📝 What to do in this step?"
          type="info"
          defaultOpen={true}
          content={
            <div>
              <p><strong>Goal:</strong> Provide the complete job description so our AI can understand the requirements.</p>
              <p style={{ marginTop: '12px' }}><strong>You can:</strong></p>
              <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
                <li>✍️ Paste the full job description text (recommended for best results)</li>
                <li>📄 Upload a job posting file (PDF, DOCX)</li>
              </ul>
              <p style={{ marginTop: '12px' }}><strong>💡 What happens next:</strong></p>
              <p>Our AI will analyze your job posting and automatically extract key requirements, skills, and qualifications. You'll be able to review and edit these in the next step.</p>
              <p style={{ marginTop: '12px' }}><strong>⏱️ Processing time:</strong> ~5-15 seconds</p>
            </div>
          }
        />
        
        <AILoadingOverlay 
          isVisible={loading}
          message={processingStatus || "AI is analyzing your job posting"}
          estimatedSeconds={15}
        />
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <div style={{ marginBottom: 'var(--spacing-md)' }}>
              <label>
                <input
                  type="radio"
                  checked={!useFile}
                  onChange={() => setUseFile(false)}
                  style={{ marginRight: 'var(--spacing-sm)' }}
                />
                Paste job posting text
              </label>
              <label style={{ marginLeft: 'var(--spacing-lg)' }}>
                <input
                  type="radio"
                  checked={useFile}
                  onChange={() => setUseFile(true)}
                  style={{ marginRight: 'var(--spacing-sm)' }}
                />
                Upload file
              </label>
            </div>
            
            {!useFile ? (
              <Textarea
                label="Job Posting"
                value={jobText}
                onChange={setJobText}
                placeholder="Paste the job posting text here..."
                required={!useFile}
                rows={12}
                maxLength={50000}
              />
            ) : (
              <FileUpload
                onFileSelect={setFiles}
                multiple={false}
                accept=".pdf,.docx,.doc,.txt"
                label="Upload Job Posting File"
              />
            )}
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/interviewer/step1')}
            >
              {t('common.back')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={loading || (!jobText && files.length === 0)}
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

export default InterviewerStep2;

