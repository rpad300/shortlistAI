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
      <StepLayout>
        <div className="step-container">
          <div className="step-content">
            <p>Loading results...</p>
          </div>
        </div>
      </StepLayout>
    );
  }
  
  if (error || !results) {
    return (
      <StepLayout>
        <div className="step-container">
          <div className="step-content">
            <div className="error-banner">{error || 'No results found'}</div>
            <Button onClick={() => navigate('/candidate/step1')}>Start Over</Button>
          </div>
        </div>
      </StepLayout>
    );
  }
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content" style={{ maxWidth: '1000px' }}>
          <h1>{t('candidate.step5_title')}</h1>
          <p className="step-subtitle">Your personalized interview preparation guide</p>
        
        {results.company_name && (
          <div className="company-info-banner">
            <p>
              🏢 Company: {results.company_name}
            </p>
            <p>
              ℹ️ This guide has been personalized for your application to {results.company_name}.
            </p>
          </div>
        )}
        
        <div className="form-section">
          <h2>Your Scores</h2>
          <div className="candidate-scores-grid">
            {Object.entries(results.categories).map(([category, score]) => (
              <div key={category} className="candidate-score-card">
                <div className="candidate-score-value">
                  {score}/5
                </div>
                <div className="candidate-score-label">
                  {category.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="form-section">
          <h2>Your Strengths</h2>
          <ul className="strengths-list">
            {results.strengths.map((strength, idx) => (
              <li key={idx}>
                ✓ {strength}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="form-section">
          <h2>⚠️ Areas to Address</h2>
          <ul className="gaps-list">
            {results.gaps.map((gap, idx) => (
              <li key={idx}>
                {gap}
              </li>
            ))}
          </ul>
        </div>
        
        {results.gap_strategies && results.gap_strategies.length > 0 && (
          <div className="form-section">
            <h2>💡 How to Address Gaps in the Interview</h2>
            <p className="skills-legend" style={{ marginBottom: '1rem' }}>
              Don't hide your gaps—address them proactively with these strategies:
            </p>
            {results.gap_strategies.map((strategy, idx) => (
              <div key={idx} className="gap-strategy-card">
                <h3>
                  {strategy.gap}
                </h3>
                <p>
                  {strategy.how_to_address}
                </p>
                {strategy.talking_points && strategy.talking_points.length > 0 && (
                  <ul>
                    {strategy.talking_points.map((point, pointIdx) => (
                      <li key={pointIdx}>
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
          <p className="skills-legend" style={{ marginBottom: '1rem', display: 'block' }}>
            Questions organized by category, with suggested answers based on your CV:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
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
                <div key={idx} className="question-card">
                  {category && (
                    <div className="question-category-badge">
                      {category.replace('_', ' ')}
                    </div>
                  )}
                  <h3>
                    {idx + 1}. {questionText}
                  </h3>
                  <div className="question-suggested-answer">
                    <strong>💡 Suggested Answer:</strong> {suggestedAnswer}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        
        <div className="form-section">
          <h2>🎯 Your Intro Pitch</h2>
          <div className="intro-pitch-card">
            "{results.intro_pitch}"
          </div>
        </div>
        
        {results.preparation_tips && results.preparation_tips.length > 0 && (
          <div className="form-section">
            <h2>📚 Preparation Checklist</h2>
            <ul className="preparation-checklist">
              {results.preparation_tips.map((tip, idx) => (
                <li key={idx}>
                  ☐ {tip}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="form-actions">
          <Button
            variant="outline"
            onClick={async () => {
              const sessionId = sessionStorage.getItem('candidate_session_id');
              if (sessionId) {
                try {
                  const response = await candidateAPI.downloadReport(sessionId);
                  const blob = new Blob([response.data], { type: 'application/pdf' });
                  const url = window.URL.createObjectURL(blob);
                  window.open(url, '_blank');
                  // Clean up the URL after a delay
                  setTimeout(() => window.URL.revokeObjectURL(url), 100);
                } catch (error) {
                  console.error('Error downloading report:', error);
                }
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

