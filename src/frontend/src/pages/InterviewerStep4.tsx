/**
 * Interviewer Flow - Step 4: Weighting and Hard Blockers
 */

import React, { useEffect, useMemo, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import Textarea from '@components/Textarea';
import Button from '@components/Button';
import StepHelper from '@components/StepHelper';
import AILoadingOverlay from '@components/AILoadingOverlay';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

type Weights = {
  technical_skills: number;
  experience: number;
  soft_skills: number;
  languages: number;
  education: number;
};

type WeightingSuggestion = {
  weights?: Partial<Weights>;
  hard_blockers?: string[];
  nice_to_have?: string[];
  summary?: string;
};

const CATEGORY_ORDER: Array<keyof Weights> = [
  'technical_skills',
  'experience',
  'soft_skills',
  'languages',
  'education',
];

const normalizeWeights = (input?: Partial<Weights>): Partial<Weights> | null => {
  if (!input) return null;
  const normalized: Partial<Weights> = {};
  CATEGORY_ORDER.forEach((category) => {
    const value = input[category];
    if (value !== undefined && value !== null) {
      const numeric = Number(value);
      if (!Number.isNaN(numeric)) {
        normalized[category] = numeric;
      }
    }
  });
  return normalized;
};

const InterviewerStep4: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  
  // Check if session exists on mount
  useEffect(() => {
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      console.warn('No session found. Redirecting to step 1.');
      navigate('/interviewer/step1');
    }
  }, [navigate]);
  
  const [weights, setWeights] = useState<Weights>({
    technical_skills: 40,
    experience: 25,
    soft_skills: 15,
    languages: 10,
    education: 10
  });
  
  const [hardBlockers, setHardBlockers] = useState<string>('');
  const [niceToHave, setNiceToHave] = useState<string>('');
  const [loadingSuggestions, setLoadingSuggestions] = useState<boolean>(true);
  const [hasSuggestions, setHasSuggestions] = useState<boolean>(false);
  const [suggestions, setSuggestions] = useState<WeightingSuggestion | null>(null);
  const [suggestedWeights, setSuggestedWeights] = useState<Partial<Weights> | null>(null);
  const [summary, setSummary] = useState<string>('');
  const [initialSuggestionsApplied, setInitialSuggestionsApplied] = useState<boolean>(false);
  const [userAdjusted, setUserAdjusted] = useState<boolean>(false);
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
  
  const totalWeight = useMemo(
    () => Object.values(weights).reduce((sum, w) => sum + w, 0),
    [weights]
  );
  const clampToPercentage = (value: number) => Math.max(0, Math.min(100, value));
  const formatPercent = (value?: number) =>
    typeof value === 'number' && !Number.isNaN(value) ? `${Math.round(value)}%` : '—';

  const applySuggestions = (data: WeightingSuggestion) => {
    if (!data) return;

    if (data.weights) {
      const normalizedWeights = normalizeWeights(data.weights);
      setSuggestedWeights(normalizedWeights);
      setWeights((prev) => {
        const next: Weights = { ...prev };
        CATEGORY_ORDER.forEach((category) => {
          const value = normalizedWeights?.[category];
          if (typeof value === 'number' && !Number.isNaN(value)) {
            next[category] = Math.round(value);
          }
        });
        return next;
      });
    }

    if (data.hard_blockers && data.hard_blockers.length > 0) {
      setHardBlockers(data.hard_blockers.join('\n'));
    }

    if (data.nice_to_have && data.nice_to_have.length > 0) {
      setNiceToHave(data.nice_to_have.join('\n'));
    }

    setSummary(data.summary || '');
    setHasSuggestions(true);
    setUserAdjusted(false);
  };

  useEffect(() => {
    const fetchSuggestions = async () => {
      const sessionId = sessionStorage.getItem('interviewer_session_id');
      if (!sessionId) {
        console.warn('No session ID found. User may need to restart from step 1.');
        setLoadingSuggestions(false);
        setHasSuggestions(false);
        return;
      }

      try {
        setLoadingSuggestions(true);
        setProcessingStatus('Requesting AI suggestions...');
        
        // Start processing (may return immediately if already cached)
        const { data } = await interviewerAPI.step4Suggestions(sessionId);
        
        // If suggestions are already available, use them
        if (data?.has_suggestions && data.status === 'success') {
          setSuggestions(data);
          setHasSuggestions(true);
          if (data.weights) {
            setSuggestedWeights(normalizeWeights(data.weights));
          }
          if (!initialSuggestionsApplied) {
            applySuggestions(data);
            setInitialSuggestionsApplied(true);
          } else {
            setSummary(data.summary || '');
          }
          setLoadingSuggestions(false);
          return;
        }
        
        // If processing, start polling
        if (data?.status === 'processing') {
          setProcessingStatus('AI is generating suggestions...');
          
          // Start polling for progress
          pollIntervalRef.current = setInterval(async () => {
            try {
              const progressResponse = await interviewerAPI.step4SuggestionsProgress(sessionId);
              const progressData = progressResponse.data;
              
              const progressInfo = progressData.progress || {};
              const statusText = progressInfo.status || 'Processing...';
              
              setProcessingStatus(statusText);
              
              // Check if complete
              if (progressData.complete && progressData.suggestions) {
                if (pollIntervalRef.current) {
                  clearInterval(pollIntervalRef.current);
                  pollIntervalRef.current = null;
                }
                
                const suggestionsData = progressData.suggestions;
                setSuggestions(suggestionsData);
                setHasSuggestions(true);
                if (suggestionsData.weights) {
                  setSuggestedWeights(normalizeWeights(suggestionsData.weights));
                }
                if (!initialSuggestionsApplied) {
                  applySuggestions(suggestionsData);
                  setInitialSuggestionsApplied(true);
                } else {
                  setSummary(suggestionsData.summary || '');
                }
                setLoadingSuggestions(false);
                return;
              }
              
              // Check if error
              if (progressData.status === 'error') {
                if (pollIntervalRef.current) {
                  clearInterval(pollIntervalRef.current);
                  pollIntervalRef.current = null;
                }
                setLoadingSuggestions(false);
                setHasSuggestions(false);
                setError(progressInfo.status || 'Failed to generate suggestions.');
                return;
              }
            } catch (pollError: any) {
              // Don't show error for polling timeouts, just continue
              if (pollError.code !== 'ECONNABORTED' && !pollError.message?.includes('timeout')) {
                console.error('Error polling suggestions progress:', pollError);
                
                // If session expired, stop polling
                if (pollError.response?.status === 404) {
                  if (pollIntervalRef.current) {
                    clearInterval(pollIntervalRef.current);
                    pollIntervalRef.current = null;
                  }
                  setLoadingSuggestions(false);
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
            if (loadingSuggestions) {
              setLoadingSuggestions(false);
              setError('Processing took too long. Please try again.');
            }
          }, 300000); // 5 minutes max
        } else {
          setHasSuggestions(false);
          setLoadingSuggestions(false);
        }
      } catch (err: any) {
        console.error('Could not load AI weighting suggestions', err);
        if (err.response?.status === 404 && err.response?.data?.detail === 'Session not found') {
          console.warn('Session expired or not found.');
          sessionStorage.removeItem('interviewer_session_id');
          sessionStorage.removeItem('interviewer_id');
          sessionStorage.removeItem('interviewer_report_code');
        }
        setHasSuggestions(false);
        setSummary('');
        setLoadingSuggestions(false);
      }
    };

    fetchSuggestions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language, initialSuggestionsApplied]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      setError('Session not found.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const blockersArray = hardBlockers
        .split('\n')
        .map(b => b.trim())
        .filter(b => b.length > 0);
      
      const niceToHaveArray = niceToHave
        .split('\n')
        .map(item => item.trim())
        .filter(item => item.length > 0);

      const response = await interviewerAPI.step4({
        session_id: sessionId,
        weights: weights,
        hard_blockers: blockersArray,
        nice_to_have: niceToHaveArray,
        language: i18n.language
      });
      
      // Save report code if generated
      if (response.data.report_code) {
        sessionStorage.setItem('interviewer_report_code', response.data.report_code);
        console.log('Report code saved:', response.data.report_code);
      }
      
      navigate('/interviewer/step5');
      
    } catch (error: any) {
      console.error('Error in step 4:', error);
      setError(error.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content" style={{ maxWidth: '700px' }}>
          <h1>{t('interviewer.step4_title')}</h1>
          <p className="step-subtitle">Configure scoring weights and must-have requirements</p>
        
        <StepHelper
          title="⚖️ What are weights and blockers?"
          type="info"
          defaultOpen={false}
          content={
            <div>
              <p><strong>Goal:</strong> Define how important each category is and identify absolute requirements.</p>
              <p style={{ marginTop: '12px' }}><strong>Category Weights (must total 100%):</strong></p>
              <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
                <li><strong>Technical Skills:</strong> Programming, tools, specific technologies</li>
                <li><strong>Experience:</strong> Years and type of relevant experience</li>
                <li><strong>Soft Skills:</strong> Communication, leadership, teamwork</li>
                <li><strong>Languages:</strong> Required spoken/written languages</li>
                <li><strong>Education:</strong> Degrees, certifications, academic background</li>
              </ul>
              <p style={{ marginTop: '12px' }}><strong>💡 AI will suggest optimal weights</strong> based on your job posting analysis!</p>
              <p style={{ marginTop: '8px' }}><strong>Hard Blockers:</strong> Mandatory requirements - candidates missing these get flagged ⚠️</p>
              <p style={{ marginTop: '8px' }}><strong>Nice-to-Have:</strong> Preferred but optional - helps differentiate top candidates.</p>
              <p style={{ marginTop: '12px' }}><strong>⏱️ AI processing:</strong> ~10-20 seconds</p>
            </div>
          }
        />
        
        <AILoadingOverlay 
          isVisible={loadingSuggestions}
          message={processingStatus || "AI is analyzing your job posting to suggest optimal weights and requirements"}
          estimatedSeconds={20}
        />
        
        <AILoadingOverlay 
          isVisible={loading}
          message="Saving evaluation criteria and creating report"
          estimatedSeconds={5}
        />
        
        <form onSubmit={handleSubmit} className="step-form">
          {!loadingSuggestions && hasSuggestions && (
            <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-accent-light)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--spacing-lg)' }}>
              <strong>✨ AI Recommendation:</strong>
              <p style={{ marginTop: 'var(--spacing-sm)' }}>
                {summary || 'We analyzed your job posting and proposed initial weights, hard blockers, and nice-to-have differentiators.'}
              </p>
              {suggestions && (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    applySuggestions(suggestions);
                    setUserAdjusted(false);
                    setInitialSuggestionsApplied(true);
                  }}
                  style={{ marginTop: 'var(--spacing-sm)' }}
                >
                  Apply AI suggestions again
                </Button>
              )}
            </div>
          )}

          <div className="form-section">
            <h2>Category Weights (Total: {totalWeight}%)</h2>
            
            {CATEGORY_ORDER.map((key) => {
              const value = weights[key];
              const aiValue = suggestedWeights?.[key];
              return (
              <div key={key} className="weight-slider-block">
                <div className="weight-slider-header">
                  <span>{key.replace('_', ' ').toUpperCase()}</span>
                  <div className="weight-slider-header-values">
                    {typeof aiValue === 'number' && !Number.isNaN(aiValue) && (
                      <span className="weight-slider-ai">AI: {formatPercent(aiValue)}</span>
                    )}
                    <span className="weight-slider-user">You: {formatPercent(value)}</span>
                  </div>
                </div>
                <div className="weight-slider">
                  <div className="weight-slider-track">
                    {typeof aiValue === 'number' && !Number.isNaN(aiValue) && (
                      <div
                        className="weight-slider-track-bar weight-slider-track-bar--ai"
                        style={{ width: `${clampToPercentage(aiValue)}%` }}
                      />
                    )}
                    <div
                      className="weight-slider-track-bar weight-slider-track-bar--user"
                      style={{ width: `${clampToPercentage(value)}%` }}
                    />
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={value}
                    onChange={(e) => {
                      setWeights({ ...weights, [key]: parseInt(e.target.value, 10) });
                      setUserAdjusted(true);
                      setInitialSuggestionsApplied(true);
                    }}
                    className="weight-slider-input"
                  />
                </div>
              </div>
            )})}

            {userAdjusted && (
              <div
                style={{
                  marginTop: 'var(--spacing-md)',
                  padding: 'var(--spacing-sm)',
                  backgroundColor: 'var(--color-bg-secondary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--color-text-secondary)',
                }}
              >
                ✅ {t('interviewer.step4_manual_adjust_notice', { defaultValue: 'You adjusted the weights manually. We will prioritize your custom values when generating the shortlist.' })}
              </div>
            )}
            
            {(totalWeight < 90 || totalWeight > 110) && (
              <div style={{ padding: 'var(--spacing-sm)', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderRadius: 'var(--radius-md)', marginTop: 'var(--spacing-md)' }}>
                ⚠️ Total weight should be close to 100% (current: {totalWeight}%)
              </div>
            )}
          </div>
          
          <div className="form-section">
            <Textarea
              label="Hard Blockers (one per line)"
              value={hardBlockers}
              onChange={(value) => {
                setHardBlockers(value);
                setUserAdjusted(true);
                setInitialSuggestionsApplied(true);
              }}
              placeholder={`Example:\nMust speak French\nMust have 5+ years experience\nMust accept on-site work`}
              rows={5}
            />
          </div>

          <div className="form-section">
            <Textarea
              label="Nice to Have (one per line)"
              value={niceToHave}
              onChange={(value) => {
                setNiceToHave(value);
                setUserAdjusted(true);
                setInitialSuggestionsApplied(true);
              }}
              placeholder={`Example:\nExperience with AI tooling\nLeadership in cross-functional teams\nBilingual in English and Spanish`}
              rows={4}
            />
          </div>
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button type="button" variant="outline" onClick={() => navigate('/interviewer/step3')}>
              {t('common.back')}
            </Button>
            <Button type="submit" variant="primary" loading={loading} disabled={loading}>
              {t('common.next')}
            </Button>
          </div>
        </form>
      </div>
    </div>
    </StepLayout>
  );
};

export default InterviewerStep4;

