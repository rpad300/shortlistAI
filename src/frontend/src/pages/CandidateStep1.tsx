/**
 * Candidate Flow - Step 1: Identification and Consent
 * 
 * Collects candidate details and required consents.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Input from '@components/Input';
import Checkbox from '@components/Checkbox';
import Button from '@components/Button';
import { candidateAPI } from '@services/api';
import '../pages/InterviewerStep1.css'; // Reuse same styles

const CandidateStep1: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    country: ''
  });
  
  // Consent state
  const [consents, setConsents] = useState({
    consent_terms: false,
    consent_privacy: false,
    consent_store_data: false,
    consent_future_contact: false
  });
  
  // UI state
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      newErrors.name = t('forms.required_field');
    }
    
    if (!formData.email.trim()) {
      newErrors.email = t('forms.required_field');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t('forms.invalid_email');
    }
    
    if (!consents.consent_terms) {
      newErrors.consent_terms = t('forms.required_field');
    }
    
    if (!consents.consent_privacy) {
      newErrors.consent_privacy = t('forms.required_field');
    }
    
    if (!consents.consent_store_data) {
      newErrors.consent_store_data = t('forms.required_field');
    }
    
    if (!consents.consent_future_contact) {
      newErrors.consent_future_contact = t('forms.required_field');
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try:
      const response = await candidateAPI.step1({
        ...formData,
        ...consents,
        language: localStorage.getItem('language') || 'en'
      });
      
      const { candidate_id, session_id, message } = response.data;
      
      // Store session ID for next steps
      sessionStorage.setItem('candidate_session_id', session_id);
      sessionStorage.setItem('candidate_id', candidate_id);
      
      // Navigate to step 2
      navigate('/candidate/step2');
      
    } catch (error: any) {
      console.error('Error in step 1:', error);
      setErrors({
        submit: error.response?.data?.detail || 'An error occurred. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="step-container">
      <div className="step-content">
        <h1>{t('candidate.step1_title')}</h1>
        <p className="step-subtitle">{t('candidate.subtitle')}</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <section className="form-section">
            <h2>{t('candidate.step1_title')}</h2>
            
            <Input
              label={t('forms.name')}
              value={formData.name}
              onChange={(value) => setFormData({ ...formData, name: value })}
              required
              error={errors.name}
            />
            
            <Input
              label={t('forms.email')}
              type="email"
              value={formData.email}
              onChange={(value) => setFormData({ ...formData, email: value })}
              required
              error={errors.email}
            />
            
            <Input
              label={t('forms.phone')}
              type="tel"
              value={formData.phone}
              onChange={(value) => setFormData({ ...formData, phone: value })}
              error={errors.phone}
            />
            
            <Input
              label={t('forms.country')}
              value={formData.country}
              onChange={(value) => setFormData({ ...formData, country: value })}
              error={errors.country}
            />
          </section>
          
          <section className="form-section">
            <h2>Consent</h2>
            
            <Checkbox
              label={
                <>
                  {t('forms.accept_terms')} -{' '}
                  <a href="/legal/terms" target="_blank">{t('legal.terms')}</a>
                </>
              }
              checked={consents.consent_terms}
              onChange={(checked) => setConsents({ ...consents, consent_terms: checked })}
              required
              error={errors.consent_terms}
            />
            
            <Checkbox
              label={
                <>
                  {t('forms.accept_privacy')} -{' '}
                  <a href="/legal/privacy" target="_blank">{t('legal.privacy')}</a>
                </>
              }
              checked={consents.consent_privacy}
              onChange={(checked) => setConsents({ ...consents, consent_privacy: checked })}
              required
              error={errors.consent_privacy}
            />
            
            <Checkbox
              label={t('forms.consent_store_data')}
              checked={consents.consent_store_data}
              onChange={(checked) => setConsents({ ...consents, consent_store_data: checked })}
              required
              error={errors.consent_store_data}
            />
            
            <Checkbox
              label={t('forms.consent_future_contact')}
              checked={consents.consent_future_contact}
              onChange={(checked) => setConsents({ ...consents, consent_future_contact: checked })}
              required
              error={errors.consent_future_contact}
            />
          </section>
          
          {errors.submit && (
            <div className="error-banner">{errors.submit}</div>
          )}
          
          <div className="form-actions">
            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={loading}
              disabled={loading}
            >
              {t('common.next')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CandidateStep1;

