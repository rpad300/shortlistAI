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
  candidate_label?: string;  // Name or identifier from CV summary
  file_name?: string;  // Original CV filename
  summary?: {
    full_name?: string;
    current_role?: string;
    experience_years?: number;
    primary_skills?: string[];
    soft_skills?: string[];
    languages?: string[];
  };
  global_score: number;
  categories: Record<string, number>;
  strengths: string[];
  risks: string[];
  questions: string[];
  hard_blocker_flags: string[];
}

interface ExecutiveRecommendation {
  top_recommendation?: {
    candidate_name: string;
    candidate_index: number;
    summary: string;
  };
  executive_summary?: string;
  key_insights?: string[];
}

const InterviewerStep7: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [results, setResults] = useState<CandidateResult[]>([]);
  const [executiveRec, setExecutiveRec] = useState<ExecutiveRecommendation | null>(null);
  const [reportCode, setReportCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState<number | null>(null);
  
  useEffect(() => {
    const fetchResults = async () => {
      const sessionId = sessionStorage.getItem('interviewer_session_id');
      const savedReportCode = sessionStorage.getItem('interviewer_report_code');
      
      if (!sessionId) {
        setError('Session not found');
        setLoading(false);
        return;
      }
      
      if (savedReportCode) {
        setReportCode(savedReportCode);
      }
      
      try {
        const response = await interviewerAPI.step7(sessionId);
        setResults(response.data.results || []);
        setExecutiveRec(response.data.executive_recommendation || null);
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
        
        {/* Report Code Banner */}
        {reportCode && (
          <div style={{
            backgroundColor: 'var(--color-accent-primary)',
            color: 'white',
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--spacing-lg)',
            textAlign: 'center',
            fontSize: 'var(--font-size-lg)',
            fontWeight: 'bold'
          }}>
            📋 Report Code: {reportCode}
            <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 'normal', marginTop: '4px' }}>
              Use this code to add more candidates later
            </div>
          </div>
        )}
        
        {/* Executive Recommendation */}
        {executiveRec && (
          <div className="form-section" style={{ 
            backgroundColor: 'var(--color-bg-secondary)', 
            padding: 'var(--spacing-xl)', 
            borderRadius: 'var(--radius-lg)',
            marginBottom: 'var(--spacing-xl)',
            border: '2px solid var(--color-accent-primary)'
          }}>
            <h2 style={{ marginTop: 0, color: 'var(--color-accent-primary)' }}>
              📊 Executive Recommendation
            </h2>
            
            {executiveRec.top_recommendation && (
              <div style={{ 
                padding: 'var(--spacing-md)', 
                backgroundColor: 'var(--color-success)', 
                color: 'white',
                borderRadius: 'var(--radius-md)',
                marginBottom: 'var(--spacing-lg)'
              }}>
                <h3 style={{ margin: '0 0 var(--spacing-sm) 0' }}>
                  ✅ Top Candidate: {executiveRec.top_recommendation.candidate_name}
                </h3>
                <p style={{ margin: 0, fontSize: 'var(--font-size-md)' }}>
                  {executiveRec.top_recommendation.summary}
                </p>
              </div>
            )}
            
            {executiveRec.executive_summary && (
              <div style={{ 
                marginBottom: 'var(--spacing-lg)', 
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap'
              }}>
                <h3>Summary</h3>
                <p>{executiveRec.executive_summary}</p>
              </div>
            )}
            
            {executiveRec.key_insights && executiveRec.key_insights.length > 0 && (
              <div>
                <h3>Key Insights</h3>
                <ul style={{ lineHeight: '1.8' }}>
                  {executiveRec.key_insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
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
                      <div>
                        <strong>
                          {result.summary?.full_name || result.candidate_label || `Candidate ${idx + 1}`}
                        </strong>
                        {result.summary?.current_role && (
                          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                            {result.summary.current_role}
                          </div>
                        )}
                        {result.summary?.experience_years && (
                          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                            {result.summary.experience_years} years experience
                          </div>
                        )}
                      </div>
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
            <h2>
              {results[selectedCandidate].summary?.full_name || 
               results[selectedCandidate].candidate_label || 
               `Candidate ${selectedCandidate + 1}`} - Detailed Analysis
            </h2>
            {results[selectedCandidate].summary && (
              <div style={{ 
                padding: 'var(--spacing-md)', 
                backgroundColor: 'var(--color-bg-primary)', 
                borderRadius: 'var(--radius-md)',
                marginBottom: 'var(--spacing-lg)',
                fontSize: 'var(--font-size-sm)'
              }}>
                {results[selectedCandidate].summary.current_role && (
                  <div><strong>Role:</strong> {results[selectedCandidate].summary.current_role}</div>
                )}
                {results[selectedCandidate].summary.experience_years && (
                  <div><strong>Experience:</strong> {results[selectedCandidate].summary.experience_years} years</div>
                )}
                {results[selectedCandidate].summary.primary_skills && results[selectedCandidate].summary.primary_skills.length > 0 && (
                  <div><strong>Key Skills:</strong> {results[selectedCandidate].summary.primary_skills.slice(0, 5).join(', ')}</div>
                )}
                {results[selectedCandidate].summary.languages && results[selectedCandidate].summary.languages.length > 0 && (
                  <div><strong>Languages:</strong> {results[selectedCandidate].summary.languages.join(', ')}</div>
                )}
                {results[selectedCandidate].file_name && (
                  <div style={{ marginTop: 'var(--spacing-xs)', color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-xs)' }}>
                    📄 {results[selectedCandidate].file_name}
                  </div>
                )}
              </div>
            )}
            
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
            onClick={async () => {
              const sessionId = sessionStorage.getItem('interviewer_session_id');
              if (!sessionId) {
                alert('Session not found');
                return;
              }
              
              try {
                setLoading(true);
                const response = await interviewerAPI.downloadReport(sessionId);
                
                // Create blob from response
                const blob = new Blob([response.data], { type: 'application/pdf' });
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                
                // Generate filename with timestamp
                const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
                link.download = `candidate_analysis_report_${timestamp}.pdf`;
                
                // Trigger download
                document.body.appendChild(link);
                link.click();
                
                // Cleanup
                window.URL.revokeObjectURL(url);
                document.body.removeChild(link);
                
                setLoading(false);
              } catch (error: any) {
                console.error('Error downloading PDF:', error);
                alert('Failed to generate PDF report: ' + (error.response?.data?.detail || error.message));
                setLoading(false);
              }
            }}
            disabled={loading}
          >
            📄 {loading ? 'Generating PDF...' : 'Generate PDF Report'}
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

