/**
 * CV Preparation Wizard - Step 1: Consent & CV Upload
 * 
 * First step of the CV preparation wizard. Collects required consents
 * and allows user to upload their CV for analysis.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import ModernFormLayout from '@components/ModernFormLayout';
import FileUpload from '@components/FileUpload';
import Checkbox from '@components/Checkbox';
import Button from '@components/Button';
import { chatbotAPI } from '@services/api';
import './CVPrepWizard.css';

const CVPrepStep1: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  
  // Consent state
  const [consents, setConsents] = useState({
    consent_read_cv: false,
    consent_read_job_opportunity: false,
    consent_analyze_links: false,
    consent_store_data: false
  });
  
  const [consentErrors, setConsentErrors] = useState<Record<string, string>>({});
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!cvFile) {
      newErrors.cvFile = t('cvprep.cv_required', 'Please upload your CV.');
    }
    
    if (!consents.consent_read_cv) {
      newErrors.consent_read_cv = t('forms.required_field');
    }
    
    if (!consents.consent_read_job_opportunity) {
      newErrors.consent_read_job_opportunity = t('forms.required_field');
    }
    
    if (!consents.consent_analyze_links) {
      newErrors.consent_analyze_links = t('forms.required_field');
    }
    
    if (!consents.consent_store_data) {
      newErrors.consent_store_data = t('forms.required_field');
    }
    
    setConsentErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Create new chatbot session
      const language = i18n.language || localStorage.getItem('language') || 'en';
      const sessionResponse = await chatbotAPI.welcome({
        language,
        ...consents
      });
      
      const { session_id } = sessionResponse.data;
      
      // Store session ID for next steps
      sessionStorage.setItem('cvprep_session_id', session_id);
      
      // Upload CV
      if (cvFile) {
        await chatbotAPI.uploadCV(session_id, cvFile);
      }
      
      // Navigate to step 2 (Review CV Data)
      navigate('/cv-prep/step2');
      
    } catch (err: any) {
      console.error('Error in step 1:', err);
      setError(
        err.response?.data?.detail || 
        t('cvprep.step1_error', 'An error occurred. Please try again.')
      );
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <ModernFormLayout
      title={t('cvprep.step1_title', 'Step 1: Upload Your CV')}
      subtitle={t('cvprep.step1_subtitle', 'Upload your CV and provide necessary consents to begin the preparation process.')}
      step={t('cvprep.step', 'Step 1')}
      currentStep={1}
      totalSteps={12}
    >
      <form onSubmit={handleSubmit} className="cvprep-form">
        <div className="cvprep-section">
          <h2>{t('cvprep.upload_cv', 'Upload Your CV')}</h2>
          <p className="cvprep-description">
            {t('cvprep.upload_cv_description', 'Please upload your current CV in PDF or DOCX format. We will extract and analyze all relevant information.')}
          </p>
          
          <FileUpload
            onFileSelect={(files) => setCvFile(files.length > 0 ? files[0] : null)}
            multiple={false}
            accept=".pdf,.docx,.doc"
            maxSizeMB={10}
            label={t('cvprep.select_cv_file', 'Select CV File')}
          />
          
          {consentErrors.cvFile && (
            <p className="cvprep-error">{consentErrors.cvFile}</p>
          )}
          
          {cvFile && (
            <div className="cvprep-file-info">
              <p>✓ {t('cvprep.file_selected', 'File selected')}: {cvFile.name}</p>
            </div>
          )}
        </div>
        
        <div className="cvprep-section">
          <h2>{t('cvprep.consents', 'Required Consents')}</h2>
          <p className="cvprep-description">
            {t('cvprep.consents_description', 'To provide you with the best CV preparation service, we need your consent for:')}
          </p>
          
          <div className="cvprep-consents">
            <Checkbox
              label={t('cvprep.consent_read_cv', 'I consent to read and analyze my CV')}
              checked={consents.consent_read_cv}
              onChange={(checked) => setConsents({ ...consents, consent_read_cv: checked })}
            />
            {consentErrors.consent_read_cv && (
              <p className="cvprep-error">{consentErrors.consent_read_cv}</p>
            )}
            
            <Checkbox
              label={t('cvprep.consent_read_job', 'I consent to read and analyze the job opportunity')}
              checked={consents.consent_read_job_opportunity}
              onChange={(checked) => setConsents({ ...consents, consent_read_job_opportunity: checked })}
            />
            {consentErrors.consent_read_job_opportunity && (
              <p className="cvprep-error">{consentErrors.consent_read_job_opportunity}</p>
            )}
            
            <Checkbox
              label={t('cvprep.consent_analyze_links', 'I consent to analyze public links (LinkedIn, GitHub, portfolio)')}
              checked={consents.consent_analyze_links}
              onChange={(checked) => setConsents({ ...consents, consent_analyze_links: checked })}
            />
            {consentErrors.consent_analyze_links && (
              <p className="cvprep-error">{consentErrors.consent_analyze_links}</p>
            )}
            
            <Checkbox
              label={t('cvprep.consent_store_data', 'I consent to store my data for this session')}
              checked={consents.consent_store_data}
              onChange={(checked) => setConsents({ ...consents, consent_store_data: checked })}
            />
            {consentErrors.consent_store_data && (
              <p className="cvprep-error">{consentErrors.consent_store_data}</p>
            )}
          </div>
        </div>
        
        {error && (
          <div className="cvprep-error-banner">
            {error}
          </div>
        )}
        
        <div className="cvprep-form-actions">
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            disabled={loading || !cvFile || !Object.values(consents).every(Boolean)}
          >
            {loading ? t('common.loading', 'Loading...') : t('common.next', 'Next →')}
          </Button>
        </div>
      </form>
    </ModernFormLayout>
  );
};

export default CVPrepStep1;

