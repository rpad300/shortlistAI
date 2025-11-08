/**
 * Candidate Flow - Step 2: Job Posting Input
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Textarea from '@components/Textarea';
import FileUpload from '@components/FileUpload';
import Button from '@components/Button';
import { candidateAPI } from '@services/api';
import './InterviewerStep1.css';

const CandidateStep2: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  const [jobText, setJobText] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [useFile, setUseFile] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('candidate_session_id');
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
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('language', i18n.language);
      
      if (files.length > 0) {
        formData.append('file', files[0]);
      } else {
        formData.append('raw_text', jobText);
      }
      
      await candidateAPI.step2(formData);
      navigate('/candidate/step3');
      
    } catch (error: any) {
      console.error('Error in step 2:', error);
      setError(error.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content">
        <h1>{t('candidate.step2_title')}</h1>
        <p className="step-subtitle">Provide the job posting you're applying for</p>
        
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
            <Button type="button" variant="outline" onClick={() => navigate('/candidate/step1')}>
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

export default CandidateStep2;

