/**
 * Interviewer Flow - Step 2: Job Posting Input
 * 
 * Accepts job posting as text or file upload.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Textarea from '@components/Textarea';
import FileUpload from '@components/FileUpload';
import Button from '@components/Button';
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
    
    try {
      // Se usar file upload
      if (useFile && files.length > 0) {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('language', i18n.language);
        formData.append('file', files[0]);
        
        const response = await interviewerAPI.step2(formData);
        navigate('/interviewer/step3');
        return;
      }
      
      // Se usar texto
      if (!useFile && jobText.trim()) {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('language', i18n.language);
        formData.append('raw_text', jobText);
        
        const response = await interviewerAPI.step2(formData);
        navigate('/interviewer/step3');
        return;
      }
      
      // Se nenhum dos dois
      setError('Por favor, forneça o job posting como texto ou upload de ficheiro.');
      setLoading(false);
      return;
    } catch (error: any) {
      console.error('Error in step 2:', error);
      const errorDetail = error.response?.data?.detail;
      const errorMessage = Array.isArray(errorDetail) 
        ? errorDetail.map((e: any) => e.msg || e).join(', ')
        : typeof errorDetail === 'string' 
          ? errorDetail 
          : 'An error occurred. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content">
        <h1>{t('interviewer.step2_title')}</h1>
        <p className="step-subtitle">Provide the job posting you want to analyze CVs against</p>
        
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
              {t('common.previous')}
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
  );
};

export default InterviewerStep2;

