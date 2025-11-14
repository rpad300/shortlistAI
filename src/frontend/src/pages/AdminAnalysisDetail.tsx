import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import './AdminCandidates.css';

interface Analysis {
  id: string;
  mode: string;
  provider: string;
  global_score?: number;
  language: string;
  created_at: string;
  candidate_id?: string;
  job_posting_id?: string;
  cv_id?: string;
  detailed_analysis?: any;
  strengths?: string[];
  risks?: string[];
  questions?: string[];
  hard_blocker_flags?: string[];
  categories?: Record<string, number>;
}

const AdminAnalysisDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      loadAnalysisDetails();
    }
  }, [id]);

  const loadAnalysisDetails = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get(`/admin/analyses/${id}`);
      setAnalysis(response.data.analysis);
    } catch (error: any) {
      console.error('Error loading analysis details:', error);
      setError(error.response?.data?.detail || 'Error loading analysis details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score?: number): React.CSSProperties => {
    if (!score) return { color: 'var(--color-text-secondary)' };
    if (score >= 80) return { color: 'var(--color-success)' };
    if (score >= 60) return { color: 'var(--color-warning)' };
    return { color: 'var(--color-error)' };
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="admin-loading">
          <div className="loading-spinner"></div>
          <p>Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="admin-dashboard">
        <div className="admin-header">
          <div className="admin-header-content">
            <h1>Analysis Details</h1>
            <div className="admin-user-info">
              <span>Welcome, {user?.username}</span>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          </div>
        </div>
        <div className="admin-content">
          <div className="error-banner">
            {error || 'Analysis not found'}
            <button onClick={() => navigate('/admin/analyses')} style={{ marginLeft: '10px', padding: '5px 10px' }}>
              Back to Analyses
            </button>
          </div>
        </div>
      </div>
    );
  }

  const detailed = analysis.detailed_analysis || {};

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div className="admin-header-content">
          <h1>Analysis Details</h1>
          <div className="admin-user-info">
            <span>Welcome, {user?.username}</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="admin-content">
        <div style={{ marginBottom: 'var(--spacing-lg)' }}>
          <Link to="/admin/analyses" className="btn-view" style={{ display: 'inline-block', marginBottom: 'var(--spacing-md)' }}>
            ← Back to Analyses
          </Link>
        </div>

        {/* Overview Section */}
        <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
          <h2>Overview</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-lg)' }}>
            <div className="stat-card">
              <div className="stat-label">Mode</div>
              <div className="stat-number">
                {analysis.mode === 'interviewer' ? (
                  <span className="badge badge-primary">Interviewer</span>
                ) : (
                  <span className="badge badge-success">Candidate</span>
                )}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Provider</div>
              <div className="stat-number">{analysis.provider.toUpperCase()}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Global Score</div>
              <div className="stat-number" style={getScoreColor(analysis.global_score)}>
                {analysis.global_score ? `${analysis.global_score.toFixed(1)}%` : 'N/A'}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Language</div>
              <div className="stat-number">{analysis.language.toUpperCase()}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Created</div>
              <div className="stat-number" style={{ fontSize: '0.9rem' }}>{formatDate(analysis.created_at)}</div>
            </div>
          </div>
        </div>

        {/* Links Section */}
        <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
          <h2>Related Resources</h2>
          <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-lg)', flexWrap: 'wrap' }}>
            {analysis.candidate_id && (
              <Link to={`/admin/candidates/${analysis.candidate_id}`} className="btn-view">
                View Candidate
              </Link>
            )}
            {analysis.cv_id && (
              <span className="btn-view" style={{ opacity: 0.7, cursor: 'not-allowed' }}>
                CV ID: {analysis.cv_id.substring(0, 8)}...
              </span>
            )}
            {analysis.job_posting_id && (
              <span className="btn-view" style={{ opacity: 0.7, cursor: 'not-allowed' }}>
                Job Posting ID: {analysis.job_posting_id.substring(0, 8)}...
              </span>
            )}
          </div>
        </div>

        {/* Score Breakdown */}
        {analysis.categories && Object.keys(analysis.categories).length > 0 && (
          <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
            <h2>Score Breakdown</h2>
            <div className="candidates-table" style={{ marginTop: 'var(--spacing-lg)' }}>
              <table>
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analysis.categories).map(([category, score]) => (
                    <tr key={category}>
                      <td>{category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                      <td style={getScoreColor(score as number)}>
                        {(score as number).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Strengths */}
        {analysis.strengths && analysis.strengths.length > 0 && (
          <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
            <h2>Strengths</h2>
            <ul style={{ marginTop: 'var(--spacing-lg)', paddingLeft: 'var(--spacing-lg)' }}>
              {analysis.strengths.map((strength, idx) => (
                <li key={idx} style={{ marginBottom: 'var(--spacing-sm)' }}>{strength}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Risks */}
        {analysis.risks && analysis.risks.length > 0 && (
          <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
            <h2>Risks</h2>
            <ul style={{ marginTop: 'var(--spacing-lg)', paddingLeft: 'var(--spacing-lg)' }}>
              {analysis.risks.map((risk, idx) => (
                <li key={idx} style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-warning)' }}>{risk}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Hard Blockers */}
        {analysis.hard_blocker_flags && analysis.hard_blocker_flags.length > 0 && (
          <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
            <h2>Hard Blocker Flags</h2>
            <ul style={{ marginTop: 'var(--spacing-lg)', paddingLeft: 'var(--spacing-lg)' }}>
              {analysis.hard_blocker_flags.map((flag, idx) => (
                <li key={idx} style={{ marginBottom: 'var(--spacing-sm)', color: 'var(--color-error)' }}>{flag}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Questions */}
        {analysis.questions && analysis.questions.length > 0 && (
          <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
            <h2>Suggested Questions</h2>
            <ul style={{ marginTop: 'var(--spacing-lg)', paddingLeft: 'var(--spacing-lg)' }}>
              {analysis.questions.map((question, idx) => (
                <li key={idx} style={{ marginBottom: 'var(--spacing-sm)' }}>{question}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Detailed Analysis */}
        {detailed && Object.keys(detailed).length > 0 && (
          <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
            <h2>Detailed Analysis</h2>
            <div style={{ marginTop: 'var(--spacing-lg)' }}>
              <pre style={{ 
                background: 'var(--color-bg-secondary)', 
                padding: 'var(--spacing-md)', 
                borderRadius: 'var(--border-radius)',
                overflow: 'auto',
                fontSize: '0.9rem',
                lineHeight: '1.5'
              }}>
                {JSON.stringify(detailed, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Raw Data */}
        <div className="candidates-section">
          <h2>Raw Data</h2>
          <div style={{ marginTop: 'var(--spacing-lg)' }}>
            <pre style={{ 
              background: 'var(--color-bg-secondary)', 
              padding: 'var(--spacing-md)', 
              borderRadius: 'var(--border-radius)',
              overflow: 'auto',
              fontSize: '0.85rem',
              lineHeight: '1.4'
            }}>
              {JSON.stringify(analysis, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalysisDetail;

