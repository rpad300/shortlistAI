/**
 * Interviewer Flow - Step 5: Upload CVs (Batch)
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import FileUpload from '@components/FileUpload';
import Button from '@components/Button';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep5: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      setError('Session not found.');
      return;
    }
    
    if (files.length === 0) {
      setError('Please upload at least one CV.');
      return;
    }
    
    setLoading(true);
    setError('');
    setUploadProgress(`Uploading ${files.length} CVs...`);
    
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      files.forEach(file => {
        formData.append('files', file);
      });
      
      const response = await interviewerAPI.step5(formData);
      
      const { files_processed, files_failed } = response.data;
      
      if (files_failed > 0) {
        setUploadProgress(`✅ Processed ${files_processed} CVs. ${files_failed} failed.`);
        // Still allow to proceed
        setTimeout(() => navigate('/interviewer/step6'), 2000);
      } else {
        navigate('/interviewer/step6');
      }
      
    } catch (error: any) {
      console.error('Error in step 5:', error);
      setError(error.response?.data?.detail || 'An error occurred uploading CVs.');
      setUploadProgress('');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content">
        <h1>{t('interviewer.step5_title')}</h1>
        <p className="step-subtitle">Upload all CVs you want to analyze (multiple files supported)</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <FileUpload
              onFileSelect={setFiles}
              multiple={true}
              accept=".pdf,.docx,.doc"
              maxSizeMB={10}
              label="Upload CVs (PDF, DOCX)"
            />
            
            {files.length > 0 && (
              <div style={{ marginTop: 'var(--spacing-md)', padding: 'var(--spacing-md)', backgroundColor: 'var(--color-accent-light)', borderRadius: 'var(--radius-md)' }}>
                <strong>{files.length} CV(s) selected</strong>
              </div>
            )}
          </div>
          
          {uploadProgress && (
            <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--spacing-md)' }}>
              {uploadProgress}
            </div>
          )}
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button type="button" variant="outline" onClick={() => navigate('/interviewer/step4')}>
              {t('common.previous')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={loading || files.length === 0}
            >
              {loading ? 'Uploading...' : `Upload ${files.length} CV(s)`}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InterviewerStep5;

