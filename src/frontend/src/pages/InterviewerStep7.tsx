/**
 * Interviewer Flow - Step 7: Results
 * 
 * Display ranked candidates with scores and details.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import Button from '@components/Button';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

interface TechnicalSkill {
  skill: string;
  score: number;
  justification: string;
}

interface SoftSkill {
  skill: string;
  score: number;
  justification: string;
}

interface NotableAchievement {
  achievement: string;
  impact: string;
}

interface ScoreBreakdown {
  technical_skills?: {
    weight_percent: number;
    score: number;
    justification: string;
  };
  soft_skills?: {
    weight_percent: number;
    score: number;
    justification: string;
  };
  professional_experience?: {
    weight_percent: number;
    score: number;
    justification: string;
  };
  education_certifications?: {
    weight_percent: number;
    score: number;
    justification: string;
  };
  culture_fit?: {
    weight_percent: number;
    score: number;
    justification: string;
  };
  global_score?: number;
  global_score_justification?: string;
}

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
  recommendation?: string;  // Brief hiring recommendation from AI
  intro_pitch?: string;  // Candidate intro pitch
  gap_strategies?: string[];  // Strategies to address gaps/risks
  preparation_tips?: string[];  // Study topics for interview
  // Detailed analysis fields
  profile_summary?: string;
  swot_analysis?: {
    strengths?: string[];
    weaknesses?: string[];
    opportunities?: string[];
    threats?: string[];
  };
  technical_skills_detailed?: TechnicalSkill[];
  soft_skills_detailed?: SoftSkill[];
  missing_critical_technical_skills?: string[];
  missing_important_soft_skills?: string[];
  professional_experience_analysis?: {
    relevance_to_position?: string;
    career_progression?: string;
    professional_stability?: string;
  };
  education_and_certifications?: {
    relevance?: string;
    adequacy?: string;
    certifications?: string[];
  };
  notable_achievements?: NotableAchievement[];
  culture_fit_assessment?: {
    score: number;
    justification: string;
  };
  score_breakdown?: ScoreBreakdown;
  enrichment?: {
    company?: {
      name?: string;
      website?: string;
      description?: string;
      industry?: string;
      size?: string;
      location?: string;
      social_media?: Record<string, string>;
      recent_news?: Array<Record<string, any>>;
      ai_summary?: string;
    };
    candidate?: {
      name?: string;
      professional_summary?: string;
      linkedin_profile?: string;
      github_profile?: string;
      portfolio_url?: string;
      publications?: Array<Record<string, string>>;
      awards?: string[];
      ai_summary?: string;
      result_count?: number;
    };
  };
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
  const [hardBlockers, setHardBlockers] = useState<string[]>([]);
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
        const response = await interviewerAPI.step7(sessionId, savedReportCode || undefined);
        setResults(response.data.results || []);
        setExecutiveRec(response.data.executive_recommendation || null);
        setHardBlockers(response.data.hard_blockers || []);
        if (response.data.report_code) {
          setReportCode(response.data.report_code);
          sessionStorage.setItem('interviewer_report_code', response.data.report_code);
        }
      } catch (error: any) {
        console.error('Error fetching results:', error);
        const detail = error.response?.data?.detail;
        if (detail) {
          setError(detail);
        } else if (savedReportCode) {
          setError('Session expired and the report could not be recovered. Please restart the flow.');
        } else {
          setError('Failed to load results. Please restart the flow.');
        }
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
  
  if (error || results.length === 0) {
    return (
      <StepLayout>
        <div className="step-container">
          <div className="step-content">
            <div className="error-banner">{error || 'No results found'}</div>
            <Button onClick={() => navigate('/interviewer/step1')}>Start Over</Button>
          </div>
        </div>
      </StepLayout>
    );
  }
  
  return (
    <StepLayout>
      <div className="step-container" style={{ padding: 'var(--spacing-md)', minHeight: '100vh' }}>
        <div className="step-content" style={{ 
        maxWidth: '1400px', 
        width: '100%',
        overflow: 'visible',
        wordWrap: 'break-word',
        overflowWrap: 'break-word',
        fontSize: '1rem'
      }}>
        <h1>{t('interviewer.step7_title')}</h1>
        <p className="step-subtitle">Ranked candidates for your position</p>
        
        {/* Report Code Banner */}
        {reportCode && (
          <div className="report-code-banner">
            📋 Report Code: {reportCode}
            <div className="report-code-subtitle">
              Use this code to add more candidates later
            </div>
          </div>
        )}
        
        {/* Executive Recommendation */}
        {executiveRec && (
          <div className="executive-rec-section">
            <h2>
              📊 Executive Recommendation
            </h2>
            
            {executiveRec.top_recommendation && (
              <div className="top-candidate-box">
                <h3>
                  ✅ Top Candidate: {executiveRec.top_recommendation.candidate_name}
                </h3>
                <p>
                  {executiveRec.top_recommendation.summary}
                </p>
              </div>
            )}
            
            {executiveRec.executive_summary && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>Summary</h3>
                <p>{executiveRec.executive_summary}</p>
              </div>
            )}
            
            {executiveRec.key_insights && executiveRec.key_insights.length > 0 && (
              <div>
                <h3>Key Insights</h3>
                <ul>
                  {executiveRec.key_insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {/* Hard Blockers Section */}
        {hardBlockers.length > 0 && (
          <div className="hard-blockers-section">
            <h2>
              🚫 Hard Blockers (Must-Have Requirements)
            </h2>
            <ul>
              {hardBlockers.map((blocker, idx) => (
                <li key={idx}>{blocker}</li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Ranking Table */}
        <div className="form-section">
          <h2>Candidate Ranking ({results.length} total)</h2>
          
          <div className="ranking-table-container">
            <table className="ranking-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate</th>
                  <th>Global Score</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {results.map((result, idx) => (
                  <tr key={result.analysis_id}>
                    <td style={{ fontWeight: 'bold' }}>#{idx + 1}</td>
                    <td style={{ maxWidth: '300px' }}>
                      <div>
                        <span className="candidate-name">
                          {result.summary?.full_name || result.candidate_label || `Candidate ${idx + 1}`}
                        </span>
                        {result.summary?.current_role && (
                          <div className="candidate-role">
                            {result.summary.current_role}
                          </div>
                        )}
                        {result.summary?.experience_years && (
                          <div className="candidate-experience">
                            {result.summary.experience_years} years experience
                          </div>
                        )}
                      </div>
                      {result.hard_blocker_flags.length > 0 && (
                        <span className="candidate-blocker">
                          ⚠️ Blocker
                        </span>
                      )}
                    </td>
                    <td>
                      <div className={
                        result.global_score >= 4 ? 'score-high' : 
                        result.global_score >= 3 ? 'score-medium' : 
                        'score-low'
                      }>
                        {result.global_score.toFixed(1)}/5
                      </div>
                    </td>
                    <td>
                      <Button
                        variant="outline"
                        onClick={() => setSelectedCandidate(selectedCandidate === idx ? null : idx)}
                      >
                        {selectedCandidate === idx ? t('interviewer.step7.hide_details') : t('interviewer.step7.view_details')}
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
          <div className="detailed-view-section">
            <h2>
              {results[selectedCandidate].summary?.full_name || 
               results[selectedCandidate].candidate_label || 
               `${t('interviewer.step7.candidate', { defaultValue: 'Candidate' })} ${selectedCandidate + 1}`} - {t('interviewer.step7.detailed_analysis')}
            </h2>
            {/* Profile Summary */}
            {results[selectedCandidate].profile_summary && (
              <div className="profile-summary-card">
                <h3>📋 {t('interviewer.step7.profile_summary')}</h3>
                <p>{results[selectedCandidate].profile_summary}</p>
              </div>
            )}

            {results[selectedCandidate].summary && (
              <div className="summary-info-card">
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
                  <div className="summary-file-name">
                    📄 {results[selectedCandidate].file_name}
                  </div>
                )}
              </div>
            )}

            {/* SWOT Analysis */}
            {results[selectedCandidate].swot_analysis && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>📊 {t('interviewer.step7.swot_analysis')}</h3>
                <div className="swot-grid">
                  <div className="swot-card swot-card-strengths">
                    <h4>{t('interviewer.step7.strengths')}</h4>
                    <ul>
                      {(results[selectedCandidate].swot_analysis.strengths || []).map((s, i) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="swot-card swot-card-weaknesses">
                    <h4>{t('interviewer.step7.weaknesses')}</h4>
                    <ul>
                      {(results[selectedCandidate].swot_analysis.weaknesses || []).map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="swot-card swot-card-opportunities">
                    <h4>{t('interviewer.step7.opportunities')}</h4>
                    <ul>
                      {(results[selectedCandidate].swot_analysis.opportunities || []).map((o, i) => (
                        <li key={i}>{o}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="swot-card swot-card-threats">
                    <h4>{t('interviewer.step7.threats')}</h4>
                    <ul>
                      {(results[selectedCandidate].swot_analysis.threats || []).map((t, i) => (
                        <li key={i}>{t}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
            
            <div className="category-scores-grid">
              {Object.entries(results[selectedCandidate].categories).map(([category, score]) => (
                <div key={category} className="category-score-card">
                  <div className="category-score-value">
                    {score}/5
                  </div>
                  <div className="category-score-label">
                    {category.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
            
            {/* Technical Skills Detailed */}
            {results[selectedCandidate].technical_skills_detailed && results[selectedCandidate].technical_skills_detailed.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>🔧 {t('interviewer.step7.technical_skills')}</h3>
                <p className="skills-legend">
                  {t('interviewer.step7.technical_skills_legend')}
                </p>
                <div className="skills-table-container">
                  <table className="skills-table">
                    <thead>
                      <tr>
                        <th>{t('interviewer.step7.skill')}</th>
                        <th>{t('interviewer.step7.score')}</th>
                        <th>{t('interviewer.step7.justification')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results[selectedCandidate].technical_skills_detailed.map((skill, i) => (
                        <tr key={i}>
                          <td>{skill.skill}</td>
                          <td className="skills-table-center">{skill.score}/5</td>
                          <td>{skill.justification}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {results[selectedCandidate].missing_critical_technical_skills && results[selectedCandidate].missing_critical_technical_skills.length > 0 && (
                  <div className="missing-skills-warning">
                    <strong>⚠️ {t('interviewer.step7.missing_technical_skills')}:</strong>
                    <ul>
                      {results[selectedCandidate].missing_critical_technical_skills.map((skill, i) => (
                        <li key={i}>{skill}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Soft Skills Detailed */}
            {results[selectedCandidate].soft_skills_detailed && results[selectedCandidate].soft_skills_detailed.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>🤝 {t('interviewer.step7.soft_skills')}</h3>
                <p className="skills-legend">
                  {t('interviewer.step7.soft_skills_legend')}
                </p>
                <div className="skills-table-container">
                  <table className="skills-table">
                    <thead>
                      <tr>
                        <th>{t('interviewer.step7.skill')}</th>
                        <th>{t('interviewer.step7.score')}</th>
                        <th>{t('interviewer.step7.justification')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results[selectedCandidate].soft_skills_detailed.map((skill, i) => (
                        <tr key={i}>
                          <td>{skill.skill}</td>
                          <td className="skills-table-center">{skill.score}/5</td>
                          <td>{skill.justification}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {results[selectedCandidate].missing_important_soft_skills && results[selectedCandidate].missing_important_soft_skills.length > 0 && (
                  <div className="missing-skills-warning">
                    <strong>⚠️ {t('interviewer.step7.missing_soft_skills')}:</strong>
                    <ul>
                      {results[selectedCandidate].missing_important_soft_skills.map((skill, i) => (
                        <li key={i}>{skill}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Professional Experience Analysis */}
            {results[selectedCandidate].professional_experience_analysis && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>💼 {t('interviewer.step7.professional_experience')}</h3>
                <div className="analysis-section-card">
                  {results[selectedCandidate].professional_experience_analysis.relevance_to_position && (
                    <div>
                      <strong>{t('interviewer.step7.relevance_to_position')}:</strong>
                      <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                        {results[selectedCandidate].professional_experience_analysis.relevance_to_position}
                      </p>
                    </div>
                  )}
                  {results[selectedCandidate].professional_experience_analysis.career_progression && (
                    <div>
                      <strong>{t('interviewer.step7.career_progression')}:</strong>
                      <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                        {results[selectedCandidate].professional_experience_analysis.career_progression}
                      </p>
                    </div>
                  )}
                  {results[selectedCandidate].professional_experience_analysis.professional_stability && (
                    <div>
                      <strong>{t('interviewer.step7.professional_stability')}:</strong>
                      <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                        {results[selectedCandidate].professional_experience_analysis.professional_stability}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Education and Certifications */}
            {results[selectedCandidate].education_and_certifications && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>🎓 {t('interviewer.step7.education_certifications')}</h3>
                <div className="analysis-section-card">
                  {results[selectedCandidate].education_and_certifications.relevance && (
                    <div>
                      <strong>{t('interviewer.step7.relevance_adequacy')}:</strong>
                      <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                        {results[selectedCandidate].education_and_certifications.relevance}
                      </p>
                    </div>
                  )}
                  {results[selectedCandidate].education_and_certifications.adequacy && (
                    <div>
                      <strong>{t('interviewer.step7.evaluation')}:</strong>
                      <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                        {results[selectedCandidate].education_and_certifications.adequacy}
                      </p>
                    </div>
                  )}
                  {results[selectedCandidate].education_and_certifications.certifications && results[selectedCandidate].education_and_certifications.certifications.length > 0 && (
                    <div>
                      <strong>{t('interviewer.step7.certifications')}:</strong>
                      <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                        {results[selectedCandidate].education_and_certifications.certifications.map((cert, i) => (
                          <li key={i}>{cert}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Notable Achievements */}
            {results[selectedCandidate].notable_achievements && results[selectedCandidate].notable_achievements.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>🏆 {t('interviewer.step7.notable_achievements')}</h3>
                <div className="analysis-section-card">
                  {results[selectedCandidate].notable_achievements.map((achievement, i) => (
                    <div key={i} style={{ marginBottom: '1rem' }}>
                      <strong>{achievement.achievement}</strong>
                      <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
                        <em>{t('interviewer.step7.impact')}:</em> {achievement.impact}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Culture Fit Assessment */}
            {results[selectedCandidate].culture_fit_assessment && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>🌐 {t('interviewer.step7.culture_fit')}</h3>
                <p className="skills-legend">
                  {t('interviewer.step7.culture_fit_legend')}
                </p>
                <div className="analysis-section-card">
                  <div className="category-score-value" style={{ fontSize: '1.5rem', marginBottom: '0.75rem' }}>
                    {t('interviewer.step7.culture_fit_score')}: {results[selectedCandidate].culture_fit_assessment.score}/5
                  </div>
                  <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                    {results[selectedCandidate].culture_fit_assessment.justification}
                  </p>
                </div>
              </div>
            )}

            {/* Score Breakdown */}
            {results[selectedCandidate].score_breakdown && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3>📊 {t('interviewer.step7.score_breakdown')}</h3>
                {results[selectedCandidate].score_breakdown.global_score !== undefined && (
                  <div className="report-code-banner" style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                      {t('interviewer.step7.global_score')}: {results[selectedCandidate].score_breakdown.global_score}/100
                    </div>
                  </div>
                )}
                <div className="skills-table-container">
                  <table className="skills-table">
                    <thead>
                      <tr>
                        <th>{t('interviewer.step7.criterion')}</th>
                        <th>{t('interviewer.step7.weight_percent')}</th>
                        <th>{t('interviewer.step7.score')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results[selectedCandidate].score_breakdown.technical_skills && (
                        <tr>
                          <td>{t('interviewer.step7.technical_skills_label')}</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.technical_skills.weight_percent}%</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.technical_skills.score}/100</td>
                        </tr>
                      )}
                      {results[selectedCandidate].score_breakdown.soft_skills && (
                        <tr>
                          <td>{t('interviewer.step7.soft_skills_label')}</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.soft_skills.weight_percent}%</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.soft_skills.score}/100</td>
                        </tr>
                      )}
                      {results[selectedCandidate].score_breakdown.professional_experience && (
                        <tr>
                          <td>{t('interviewer.step7.professional_experience_label')}</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.professional_experience.weight_percent}%</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.professional_experience.score}/100</td>
                        </tr>
                      )}
                      {results[selectedCandidate].score_breakdown.education_certifications && (
                        <tr>
                          <td>{t('interviewer.step7.education_certifications_label')}</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.education_certifications.weight_percent}%</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.education_certifications.score}/100</td>
                        </tr>
                      )}
                      {results[selectedCandidate].score_breakdown.culture_fit && (
                        <tr>
                          <td>{t('interviewer.step7.culture_fit_label')}</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.culture_fit.weight_percent}%</td>
                          <td className="skills-table-center">{results[selectedCandidate].score_breakdown.culture_fit.score}/100</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                {results[selectedCandidate].score_breakdown.global_score_justification && (
                  <div className="analysis-section-card" style={{ marginTop: '1rem' }}>
                    <strong>{t('interviewer.step7.global_score_justification')}:</strong>
                    <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap', margin: '0.5rem 0 0 0' }}>
                      {results[selectedCandidate].score_breakdown.global_score_justification}
                    </p>
                  </div>
                )}
              </div>
            )}

            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ color: '#10B981' }}>✓ Strengths</h3>
              <ul>
                {results[selectedCandidate].strengths.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ color: '#F59E0B' }}>⚠️ Risks & Gaps</h3>
              <ul>
                {results[selectedCandidate].risks.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
            
            {results[selectedCandidate].hard_blocker_flags && results[selectedCandidate].hard_blocker_flags.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: '#EF4444' }}>🚫 Hard Blocker Violations</h3>
                <ul>
                  {results[selectedCandidate].hard_blocker_flags.map((flag, i) => (
                    <li key={i} style={{ color: '#EF4444' }}>{flag}</li>
                  ))}
                </ul>
              </div>
            )}
            
            <div style={{ marginBottom: '1.5rem' }}>
              <h3>❓ Suggested Interview Questions</h3>
              <ol style={{ paddingLeft: '1.5rem', lineHeight: '1.8' }}>
                {results[selectedCandidate].questions.map((q, i) => (
                  <li key={i} style={{ marginBottom: '0.75rem' }}>{q}</li>
                ))}
              </ol>
            </div>
            
            {results[selectedCandidate].intro_pitch && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: '#0066FF' }}>🎤 Intro Pitch</h3>
                <div className="analysis-section-card">
                  <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                    {results[selectedCandidate].intro_pitch}
                  </p>
                </div>
              </div>
            )}
            
            {results[selectedCandidate].gap_strategies && results[selectedCandidate].gap_strategies.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: '#0066FF' }}>💡 Strategies to Address Gaps & Risks</h3>
                <ul>
                  {results[selectedCandidate].gap_strategies.map((strategy, i) => (
                    <li key={i}>{strategy}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {results[selectedCandidate].preparation_tips && results[selectedCandidate].preparation_tips.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: '#0066FF' }}>📚 Study Topics for Interview</h3>
                <p className="skills-legend" style={{ marginBottom: '0.75rem' }}>
                  Topics to study to address the identified risks and gaps:
                </p>
                <ul>
                  {results[selectedCandidate].preparation_tips.map((tip, i) => (
                    <li key={i}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {results[selectedCandidate].recommendation && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: '#0066FF' }}>💡 AI Recommendation</h3>
                <div className="analysis-section-card">
                  <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                    {results[selectedCandidate].recommendation}
                  </p>
                </div>
              </div>
            )}
            
            {results[selectedCandidate].enrichment && (results[selectedCandidate].enrichment.company || results[selectedCandidate].enrichment.candidate) && (
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ color: '#0066FF' }}>🔍 Enrichment Data (Brave Search)</h3>
                <div className="analysis-section-card" style={{ overflow: 'visible' }}>
                  {results[selectedCandidate].enrichment?.company && (
                    <div style={{ marginBottom: '1rem' }}>
                      <h4 style={{ marginBottom: '0.75rem' }}>Company Information</h4>
                      {results[selectedCandidate].enrichment.company.name && (
                        <div><strong>Name:</strong> {results[selectedCandidate].enrichment.company.name}</div>
                      )}
                      {results[selectedCandidate].enrichment.company.website && (
                        <div style={{ wordBreak: 'break-all', marginBottom: '0.75rem' }}><strong>Website:</strong> <a href={results[selectedCandidate].enrichment.company.website} target="_blank" rel="noopener noreferrer" style={{ color: '#0066FF', textDecoration: 'none' }}>{results[selectedCandidate].enrichment.company.website}</a></div>
                      )}
                      {results[selectedCandidate].enrichment.company.description && (
                        <div style={{ wordWrap: 'break-word', overflowWrap: 'break-word', marginBottom: '0.75rem' }}><strong>Description:</strong> {results[selectedCandidate].enrichment.company.description}</div>
                      )}
                      {results[selectedCandidate].enrichment.company.industry && (
                        <div><strong>Industry:</strong> {results[selectedCandidate].enrichment.company.industry}</div>
                      )}
                      {results[selectedCandidate].enrichment.company.size && (
                        <div><strong>Size:</strong> {results[selectedCandidate].enrichment.company.size}</div>
                      )}
                      {results[selectedCandidate].enrichment.company.location && (
                        <div><strong>Location:</strong> {results[selectedCandidate].enrichment.company.location}</div>
                      )}
                      {results[selectedCandidate].enrichment.company.ai_summary && (
                        <div className="analysis-section-card" style={{ marginTop: '0.75rem', padding: '0.875rem 1rem' }}>
                          <strong>AI Summary:</strong>
                          <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap', margin: '0.5rem 0 0 0' }}>
                            {results[selectedCandidate].enrichment.company.ai_summary}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                  {results[selectedCandidate].enrichment.candidate && (
                    <div>
                      <h4 style={{ marginBottom: '0.75rem' }}>Candidate Professional Profile</h4>
                      {results[selectedCandidate].enrichment.candidate.professional_summary && (
                        <div style={{ wordWrap: 'break-word', overflowWrap: 'break-word', marginBottom: '0.75rem' }}><strong>Summary:</strong> {results[selectedCandidate].enrichment.candidate.professional_summary}</div>
                      )}
                      {results[selectedCandidate].enrichment.candidate.linkedin_profile && (
                        <div style={{ wordBreak: 'break-all', marginBottom: '0.75rem' }}><strong>LinkedIn:</strong> <a href={results[selectedCandidate].enrichment.candidate.linkedin_profile} target="_blank" rel="noopener noreferrer" style={{ color: '#0066FF', textDecoration: 'none' }}>{results[selectedCandidate].enrichment.candidate.linkedin_profile}</a></div>
                      )}
                      {results[selectedCandidate].enrichment.candidate.github_profile && (
                        <div style={{ wordBreak: 'break-all', marginBottom: '0.75rem' }}><strong>GitHub:</strong> <a href={results[selectedCandidate].enrichment.candidate.github_profile} target="_blank" rel="noopener noreferrer" style={{ color: '#0066FF', textDecoration: 'none' }}>{results[selectedCandidate].enrichment.candidate.github_profile}</a></div>
                      )}
                      {results[selectedCandidate].enrichment.candidate.portfolio_url && (
                        <div style={{ wordBreak: 'break-all', marginBottom: '0.75rem' }}><strong>Portfolio:</strong> <a href={results[selectedCandidate].enrichment.candidate.portfolio_url} target="_blank" rel="noopener noreferrer" style={{ color: '#0066FF', textDecoration: 'none' }}>{results[selectedCandidate].enrichment.candidate.portfolio_url}</a></div>
                      )}
                      {results[selectedCandidate].enrichment.candidate.publications && results[selectedCandidate].enrichment.candidate.publications.length > 0 && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <strong>Publications:</strong>
                          <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                            {results[selectedCandidate].enrichment.candidate.publications.map((pub: any, i: number) => (
                              <li key={i}>
                                {pub.title && <span>{pub.title}</span>}
                                {pub.url && <span> - <a href={pub.url} target="_blank" rel="noopener noreferrer" style={{ color: '#0066FF', textDecoration: 'none' }}>Link</a></span>}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {results[selectedCandidate].enrichment.candidate.awards && results[selectedCandidate].enrichment.candidate.awards.length > 0 && (
                        <div style={{ marginTop: '0.75rem' }}>
                          <strong>Awards:</strong>
                          <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                            {results[selectedCandidate].enrichment.candidate.awards.map((award: string, i: number) => (
                              <li key={i}>{award}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {results[selectedCandidate].enrichment.candidate.ai_summary && (
                        <div className="analysis-section-card" style={{ marginTop: '0.75rem', padding: '0.875rem 1rem' }}>
                          <strong>AI Summary:</strong>
                          <p style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap', margin: '0.5rem 0 0 0' }}>
                            {results[selectedCandidate].enrichment.candidate.ai_summary}
                          </p>
                        </div>
                      )}
                      {results[selectedCandidate].enrichment.candidate.result_count && (
                        <div className="skills-legend" style={{ marginTop: '0.75rem' }}>
                          Found {results[selectedCandidate].enrichment.candidate.result_count} search results
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
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
    </StepLayout>
  );
};

export default InterviewerStep7;

