/**
 * Candidate Flow - Step 5: Results
 * 
 * Display analysis results with preparation guidance.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Button from '@components/Button';
import { candidateAPI } from '@services/api';
import './InterviewerStep1.css';

interface AnalysisResults {
  categories: Record<string, number>;
  strengths: string[];
  gaps: string[];
  questions: string[];
  suggested_answers: string[];
  intro_pitch: string;
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
          <h2>Areas to Address</h2>
          <ul>
            {results.gaps.map((gap, idx) => (
              <li key={idx} style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-warning)' }}>
                • {gap}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="form-section">
          <h2>Likely Interview Questions</h2>
          <ol>
            {results.questions.map((question, idx) => (
              <li key={idx} style={{ marginBottom: 'var(--spacing-md)' }}>
                <strong>{question}</strong>
                <p style={{ marginTop: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                  {results.suggested_answers[idx] || 'Prepare a specific example from your experience'}
                </p>
              </li>
            ))}
          </ol>
        </div>
        
        <div className="form-section">
          <h2>Suggested Intro Pitch</h2>
          <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-accent-light)', borderRadius: 'var(--radius-md)', fontStyle: 'italic' }}>
            "{results.intro_pitch}"
          </div>
        </div>
        
        <div className="form-actions">
          <Button
            variant="outline"
            onClick={() => {
              const email = prompt('Enter your email to receive this preparation guide:');
              if (email) {
                candidateAPI.sendEmail(sessionStorage.getItem('candidate_session_id')!, email);
                alert('Preparation guide sent to ' + email);
              }
            }}
          >
            📧 Email Me This Guide
          </Button>
          <Button variant="primary" onClick={() => navigate('/')}>
            Finish
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CandidateStep5;

