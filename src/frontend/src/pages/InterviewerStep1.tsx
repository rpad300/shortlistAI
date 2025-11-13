/**
 * Interviewer Flow - Step 1: Identification and Consent
 * 
 * Collects interviewer details and required consents.
 */

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import Input from '@components/Input';
import Checkbox from '@components/Checkbox';
import Button from '@components/Button';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep1: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    country: '',
    company_name: '',
    existing_report_code: ''  // NEW: Optional report code to continue
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
  const [showContinueReport, setShowContinueReport] = useState(false);
  
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
    
    try {
      const response = await interviewerAPI.step1({
        ...formData,
        ...consents,
        language: localStorage.getItem('language') || 'en'
      });
      
      const { interviewer_id, session_id, report_code, is_continuing } = response.data;
      
      // Store session ID for next steps
      sessionStorage.setItem('interviewer_session_id', session_id);
      sessionStorage.setItem('interviewer_id', interviewer_id);
      
      // Store report code if generated or continuing
      if (report_code) {
        sessionStorage.setItem('interviewer_report_code', report_code);
      }
      
      // Navigate to appropriate step
      if (is_continuing) {
        // Skip to step 5 if continuing existing report
        alert(`Continuing report ${report_code}. You can now add more CVs!`);
        navigate('/interviewer/step5');
      } else {
        navigate('/interviewer/step2');
      }
      
    } catch (error: any) {
      console.error('Error in step 1:', error);
      const errorDetail = error.response?.data?.detail;
      const errorMessage = Array.isArray(errorDetail) 
        ? errorDetail.map((e: any) => e.msg || e).join(', ')
        : typeof errorDetail === 'string' 
          ? errorDetail 
          : 'An error occurred. Please try again.';
      setErrors({
        submit: errorMessage
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content">
          <h1>{t('interviewer.step1_title')}</h1>
          <p className="step-subtitle">{t('interviewer.subtitle')}</p>
        
        <form onSubmit={handleSubmit} className="step-form">
          <section className="form-section">
            <h2>{t('interviewer.step1_title')}</h2>
            
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
            
            <Input
              label={t('forms.company')}
              value={formData.company_name}
              onChange={(value) => setFormData({ ...formData, company_name: value })}
              error={errors.company_name}
            />
          </section>
          
          {/* Continue Existing Report Section */}
          <section className="form-section continue-report-section">
            <Button
              type="button"
              variant="outline"
              className="continue-report-btn"
              onClick={() => setShowContinueReport(!showContinueReport)}
            >
              {showContinueReport ? '➖' : '➕'} Continue Report (Optional)
            </Button>
            
            {showContinueReport && (
              <div className="continue-report-content">
                <Input
                  label="Report Code (e.g., REP-20250109-A3B7K2)"
                  value={formData.existing_report_code}
                  onChange={(value) => setFormData({ ...formData, existing_report_code: value.toUpperCase() })}
                  placeholder="REP-XXXXXXXX-XXXXXX"
                  error={errors.existing_report_code}
                />
                <p className="continue-report-help">
                  💡 If you have an existing report and want to add more candidates to it, enter the report code here.
                  You can find the report code in the Step 7 results or in the PDF report.
                </p>
              </div>
            )}
          </section>
          
          <section className="form-section">
            <h2>Consent</h2>
            
            <Checkbox
              label={
                <>
                  {(() => {
                    const text = t('forms.consent_terms');
                    const termsText = t('legal.terms');
                    // Extract text before "Terms and Conditions" or equivalent
                    const regex = /(.*?)(?:Terms and Conditions|Termos e Condições|Términos y Condiciones|Termes et Conditions|$)/i;
                    const match = text.match(regex);
                    const prefix = match && match[1] ? match[1].trim() + ' ' : text.replace(termsText, '').trim() + ' ';
                    return (
                      <>
                        {prefix}
                        <Link 
                          to="/legal/terms" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="consent-link"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {termsText}
                        </Link>
                      </>
                    );
                  })()}
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
                  {(() => {
                    const text = t('forms.consent_privacy');
                    const privacyText = t('legal.privacy');
                    // Extract text before "Privacy Policy" or equivalent
                    const regex = /(.*?)(?:Privacy Policy|Política de Privacidade|Politique de Confidentialité|Política de Privacidad|$)/i;
                    const match = text.match(regex);
                    const prefix = match && match[1] ? match[1].trim() + ' ' : text.replace(privacyText, '').trim() + ' ';
                    return (
                      <>
                        {prefix}
                        <Link 
                          to="/legal/privacy" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="consent-link"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {privacyText}
                        </Link>
                      </>
                    );
                  })()}
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
    </StepLayout>
  );
};

export default InterviewerStep1;

