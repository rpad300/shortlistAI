/**
 * Candidate Flow - Step 5: Results
 * 
 * Display analysis results with preparation guidance.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import Button from '@components/Button';
import { candidateAPI } from '@services/api';
import './InterviewerStep1.css';

interface GapStrategy {
  gap: string;
  how_to_address: string;
  talking_points: string[];
}

interface AnalysisResults {
  categories: Record<string, number>;
  strengths: string[];
  gaps: string[];
  questions: string[];
  suggested_answers: string[];
  gap_strategies: GapStrategy[];
  preparation_tips: string[];
  intro_pitch: string;
  company_name?: string;
}

const CandidateStep5: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    const fetchResults = async () => {
      const sessionId = sessionStorage.getItem('candidate_session_id');
      if (!sessionId) {
        setError('Session not found');
        setLoading(false);
        return;
      }
      
      try {
        const response = await candidateAPI.step5(sessionId);
        setResults(response.data);
      } catch (error: any) {
        console.error('Error fetching results:', error);
        setError(error.response?.data?.detail || 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };
    
    fetchResults();
  }, []);
  
  if (loading) {
    return (
      <div className="step-container">
        <div className="step-content">
          <p>Loading results...</p>
        </div>
      </div>
    );
  }
  
  if (error || !results) {
    return (
      <div className="step-container">
        <div className="step-content">
          <div className="error-banner">{error || 'No results found'}</div>
          <Button onClick={() => navigate('/candidate/step1')}>Start Over</Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="step-container">
      <div className="step-content" style={{ maxWidth: '900px' }}>
        <h1>{t('candidate.step5_title')}</h1>
        <p className="step-subtitle">Your personalized interview preparation guide</p>
        
        {results.company_name && (
          <div style={{
            padding: 'var(--spacing-md)',
            backgroundColor: 'var(--color-accent-light)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--spacing-lg)',
            borderLeft: '4px solid var(--color-accent-primary)'
          }}>
            <p style={{ fontSize: 'var(--font-size-base)', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>
              🏢 Company: {results.company_name}
            </p>
            <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', margin: 0 }}>
              ℹ️ This guide has been personalized for your application to {results.company_name}.
            </p>
          </div>
        )}
        
        <div className="form-section">
          <h2>Your Scores</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-md)' }}>
            {Object.entries(results.categories).map(([category, score]) => (
              <div key={category} style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 'bold', color: 'var(--color-accent-primary)' }}>
                  {score}/5
                </div>
                <div style={{ fontSize: 'var(--font-size-sm)', marginTop: 'var(--spacing-xs)' }}>
                  {category.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="form-section">
          <h2>Your Strengths</h2>
          <ul>
            {results.strengths.map((strength, idx) => (
              <li key={idx} style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-success)' }}>
                ✓ {strength}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="form-section">
          <h2>⚠️ Areas to Address</h2>
          <ul>
            {results.gaps.map((gap, idx) => (
              <li key={idx} style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-warning)' }}>
                {gap}
              </li>
            ))}
          </ul>
        </div>
        
        {results.gap_strategies && results.gap_strategies.length > 0 && (
          <div className="form-section">
            <h2>💡 How to Address Gaps in the Interview</h2>
            <p style={{ marginBottom: 'var(--spacing-md)', color: 'var(--color-text-secondary)' }}>
              Don't hide your gaps—address them proactively with these strategies:
            </p>
            {results.gap_strategies.map((strategy, idx) => (
              <div key={idx} style={{ 
                marginBottom: 'var(--spacing-lg)', 
                padding: 'var(--spacing-md)', 
                backgroundColor: 'var(--color-bg-secondary)', 
                borderRadius: 'var(--radius-md)',
                borderLeft: '4px solid var(--color-accent-primary)'
              }}>
                <h3 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-accent-primary)' }}>
                  {strategy.gap}
                </h3>
                <p style={{ marginBottom: 'var(--spacing-sm)', fontStyle: 'italic' }}>
                  {strategy.how_to_address}
                </p>
                {strategy.talking_points && strategy.talking_points.length > 0 && (
                  <ul style={{ marginTop: 'var(--spacing-sm)' }}>
                    {strategy.talking_points.map((point, pointIdx) => (
                      <li key={pointIdx} style={{ marginBottom: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                        → {point}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
        
        <div className="form-section">
          <h2>❓ Likely Interview Questions</h2>
          <p style={{ marginBottom: 'var(--spacing-md)', color: 'var(--color-text-secondary)' }}>
            Questions organized by category, with suggested answers based on your CV:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
            {results.questions.map((question, idx) => {
              // Parse question if it's a string that might be an object
              let questionText = question;
              let suggestedAnswer = results.suggested_answers[idx] || '';
              let category = '';
              
              // If question is an object (from new format)
              if (typeof question === 'object' && question !== null && 'question' in question) {
                const q = question as any;
                questionText = q.question;
                suggestedAnswer = q.suggested_answer || suggestedAnswer;
                category = q.category || '';
              }
              
              return (
                <div key={idx} style={{
                  padding: 'var(--spacing-md)',
                  backgroundColor: 'var(--color-bg-secondary)',
                  borderRadius: 'var(--radius-md)',
                  borderLeft: '4px solid var(--color-accent-primary)'
                }}>
                  {category && (
                    <div style={{
                      display: 'inline-block',
                      padding: '4px 12px',
                      backgroundColor: 'var(--color-accent-primary)',
                      color: 'white',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: 'var(--font-size-xs)',
                      marginBottom: 'var(--spacing-sm)',
                      textTransform: 'uppercase',
                      fontWeight: 600
                    }}>
                      {category.replace('_', ' ')}
                    </div>
                  )}
                  <h3 style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-text-primary)' }}>
                    {idx + 1}. {questionText}
                  </h3>
                  <div style={{
                    padding: 'var(--spacing-sm)',
                    backgroundColor: 'var(--color-accent-light)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-secondary)'
                  }}>
                    <strong>💡 Suggested Answer:</strong> {suggestedAnswer}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        <div className="form-section">
          <h2>🎯 Your Intro Pitch</h2>
          <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-accent-light)', borderRadius: 'var(--radius-md)', fontStyle: 'italic' }}>
            "{results.intro_pitch}"
          </div>
        </div>
        
        {results.preparation_tips && results.preparation_tips.length > 0 && (
          <div className="form-section">
            <h2>📚 Preparation Checklist</h2>
            <ul>
              {results.preparation_tips.map((tip, idx) => (
                <li key={idx} style={{ marginBottom: 'var(--spacing-sm)' }}>
                  ☐ {tip}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="form-actions">
          <Button
            variant="outline"
            onClick={() => {
              const sessionId = sessionStorage.getItem('candidate_session_id');
              if (sessionId) {
                window.open(`http://localhost:8000/api/candidate/step6/report/${sessionId}`, '_blank');
              }
            }}
          >
            📄 Download PDF Guide
          </Button>
          <Button variant="primary" onClick={() => navigate('/')}>
            Finish
          </Button>
        </div>
      </div>
    </div>
    </StepLayout>
  );
};

export default CandidateStep5;

