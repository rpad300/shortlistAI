/**
 * Candidate Flow - Step 3: Upload CV
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import FileUpload from '@components/FileUpload';
import Button from '@components/Button';
import { candidateAPI } from '@services/api';
import './InterviewerStep1.css';

const CandidateStep3: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('candidate_session_id');
    if (!sessionId) {
      setError('Session not found.');
      return;
    }
    
    if (files.length === 0) {
      setError('Please upload your CV.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('file', files[0]);
      
      await candidateAPI.step3(formData);
      navigate('/candidate/step4');
      
    } catch (error: any) {
      console.error('Error in step 3:', error);
      setError(error.response?.data?.detail || 'An error occurred uploading CV.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content">
        <h1>{t('candidate.step3_title')}</h1>
        <p className="step-subtitle">Upload your CV for analysis</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <FileUpload
              onFileSelect={setFiles}
              multiple={false}
              accept=".pdf,.docx,.doc"
              maxSizeMB={10}
              label="Upload Your CV (PDF, DOCX)"
            />
            
            <div style={{ marginTop: 'var(--spacing-lg)', padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <strong>Tip:</strong> Make sure your CV is up-to-date and includes your contact information.
            </div>
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button type="button" variant="outline" onClick={() => navigate('/candidate/step2')}>
              {t('common.previous')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={loading || files.length === 0}
            >
              {loading ? 'Uploading...' : 'Analyze My Fit'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CandidateStep3;

