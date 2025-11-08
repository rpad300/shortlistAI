/**
 * Interviewer Flow - Step 7: Results
 * 
 * Display ranked candidates with scores and details.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Button from '@components/Button';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

interface CandidateResult {
  analysis_id: string;
  candidate_id: string;
  global_score: number;
  categories: Record<string, number>;
  strengths: string[];
  risks: string[];
  questions: string[];
  hard_blocker_flags: string[];
}

const InterviewerStep7: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [results, setResults] = useState<CandidateResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(null);
  
  useEffect(() => {
    const fetchResults = async () => {
      const sessionId = sessionStorage.getItem('interviewer_session_id');
      if (!sessionId) {
        setError('Session not found');
        setLoading(false);
        return;
      }
      
      try {
        const response = await interviewerAPI.step7(sessionId);
        setResults(response.data.results || []);
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
  
  if (error || results.length === 0) {
    return (
      <div className="step-container">
        <div className="step-content">
          <div className="error-banner">{error || 'No results found'}</div>
          <Button onClick={() => navigate('/interviewer/step1')}>Start Over</Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="step-container">
      <div className="step-content" style={{ maxWidth: '1200px' }}>
        <h1>{t('interviewer.step7_title')}</h1>
        <p className="step-subtitle">Ranked candidates for your position</p>
        
        {/* Ranking Table */}
        <div className="form-section">
          <h2>Candidate Ranking ({results.length} total)</h2>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: 'var(--color-bg-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: 'var(--spacing-md)', borderBottom: '2px solid var(--color-border)' }}>Rank</th>
                  <th style={{ padding: 'var(--spacing-md)', borderBottom: '2px solid var(--color-border)' }}>Candidate</th>
                  <th style={{ padding: 'var(--spacing-md)', borderBottom: '2px solid var(--color-border)' }}>Global Score</th>
                  <th style={{ padding: 'var(--spacing-md)', borderBottom: '2px solid var(--color-border)' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result, idx) => (
                  <tr key={result.analysis_id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: 'var(--spacing-md)', fontWeight: 'bold' }}>#{idx + 1}</td>
                    <td style={{ padding: 'var(--spacing-md)' }}>
                      Candidate {idx + 1}
                      {result.hard_blocker_flags.length > 0 && (
                        <span style={{ marginLeft: 'var(--spacing-sm)', color: 'var(--color-error)', fontSize: 'var(--font-size-sm)' }}>
                          ⚠️ Blocker
                        </span>
                      )}
                    </td>
                    <td style={{ padding: 'var(--spacing-md)' }}>
                      <div style={{ 
                        fontSize: 'var(--font-size-xl)', 
                        fontWeight: 'bold',
                        color: result.global_score >= 4 ? 'var(--color-success)' : 
                               result.global_score >= 3 ? 'var(--color-warning)' : 
                               'var(--color-error)'
                      }}>
                        {result.global_score.toFixed(1)}/5
                      </div>
                    </td>
                    <td style={{ padding: 'var(--spacing-md)' }}>
                      <Button
                        variant="outline"
                        onClick={() => setSelectedCandidate(selectedCandidate === idx ? null : idx)}
                      >
                        {selectedCandidate === idx ? 'Hide' : 'View'} Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Detailed View */}
        {selectedCandidate !== null && results[selectedCandidate] && (
          <div className="form-section" style={{ backgroundColor: 'var(--color-bg-secondary)', padding: 'var(--spacing-xl)', borderRadius: 'var(--radius-lg)' }}>
            <h2>Candidate {selectedCandidate + 1} - Detailed Analysis</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
              {Object.entries(results[selectedCandidate].categories).map(([category, score]) => (
                <div key={category} style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-primary)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', color: 'var(--color-accent-primary)' }}>
                    {score}/5
                  </div>
                  <div style={{ fontSize: 'var(--font-size-xs)', marginTop: 'var(--spacing-xs)' }}>
                    {category.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
            
            <div style={{ marginBottom: 'var(--spacing-lg)' }}>
              <h3 style={{ color: 'var(--color-success)' }}>✓ Strengths</h3>
              <ul>
                {results[selectedCandidate].strengths.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
            
            <div style={{ marginBottom: 'var(--spacing-lg)' }}>
              <h3 style={{ color: 'var(--color-warning)' }}>⚠️ Risks & Gaps</h3>
              <ul>
                {results[selectedCandidate].risks.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3>❓ Custom Interview Questions</h3>
              <ol>
                {results[selectedCandidate].questions.map((q, i) => (
                  <li key={i} style={{ marginBottom: 'var(--spacing-sm)' }}>{q}</li>
                ))}
              </ol>
            </div>
          </div>
        )}
        
        <div className="form-actions">
          <Button
            variant="outline"
            onClick={() => {
              const email = prompt('Enter your email to receive the full analysis:');
              if (email) {
                interviewerAPI.sendEmail(sessionStorage.getItem('interviewer_session_id')!, email);
                alert('Analysis summary sent to ' + email);
              }
            }}
          >
            📧 Email Me Results
          </Button>
          <Button variant="primary" onClick={() => navigate('/')}>
            Finish
          </Button>
        </div>
      </div>
    </div>
  );
};

export default InterviewerStep7;

