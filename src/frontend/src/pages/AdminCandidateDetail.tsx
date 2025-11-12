import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import './AdminCandidates.css';

interface Candidate {
  id: string;
  name: string;
  email: string;
  phone?: string;
  country?: string;
  consent_given: boolean;
  consent_timestamp?: string;
  created_at: string;
}

interface CV {
  id: string;
  file_url: string;
  version: number;
  language?: string;
  uploaded_by_flow: string;
  created_at: string;
}

interface Analysis {
  id: string;
  mode: string;
  provider: string;
  global_score?: number;
  language: string;
  created_at: string;
}

interface CandidateDetailData {
  candidate: Candidate;
  cvs: CV[];
  analyses: Analysis[];
  stats: {
    total_cvs: number;
    total_analyses: number;
  };
}

const AdminCandidateDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [data, setData] = useState<CandidateDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      loadCandidateDetails();
    }
  }, [id]);

  const loadCandidateDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/admin/candidates/${id}`);
      setData(response.data);
    } catch (error: any) {
      console.error('Error loading candidate details:', error);
      setError(error.response?.data?.detail || 'Error loading candidate details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score?: number) => {
    if (!score) return '';
    if (score >= 75) return 'var(--color-success)';
    if (score >= 50) return 'var(--color-warning)';
    return 'var(--color-error)';
  };

  if (loading) {
    return (
      <div className="admin-candidates">
        <div className="admin-loading">
          <div className="loading-spinner"></div>
          <p>Loading candidate details...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="admin-candidates">
        <div className="admin-content">
          <div className="error-banner">{error || 'Candidate not found'}</div>
          <Link to="/admin/candidates">← Back to Candidates</Link>
        </div>
      </div>
    );
  }

  const { candidate, cvs, analyses, stats } = data;

  return (
    <div className="admin-candidates">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/candidates" className="back-link">← Back to Candidates</Link>
            <h1>Candidate Details</h1>
          </div>
          <div className="admin-user-info">
            <span>Welcome, {user?.email?.split('@')[0]}</span>
            <button onClick={() => { logout(); navigate('/'); }} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="admin-content">
        {/* Candidate Info Card */}
        <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
          <h2>Candidate Information</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-lg)', marginTop: 'var(--spacing-lg)' }}>
            <div>
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>Name</div>
              <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: 'var(--font-weight-semibold)' }}>{candidate.name}</div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>Email</div>
              <div style={{ fontSize: 'var(--font-size-lg)' }}>{candidate.email}</div>
            </div>
            {candidate.phone && (
              <div>
                <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>Phone</div>
                <div style={{ fontSize: 'var(--font-size-lg)' }}>{candidate.phone}</div>
              </div>
            )}
            {candidate.country && (
              <div>
                <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>Country</div>
                <div style={{ fontSize: 'var(--font-size-lg)' }}>{candidate.country}</div>
              </div>
            )}
            <div>
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>Consent</div>
              <div>
                {candidate.consent_given ? (
                  <span className="badge badge-success">Given</span>
                ) : (
                  <span className="badge badge-warning">Not Given</span>
                )}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>Created</div>
              <div style={{ fontSize: 'var(--font-size-body)' }}>{formatDate(candidate.created_at)}</div>
            </div>
          </div>
        </div>

        {/* CVs Section */}
        <div className="candidates-section" style={{ marginBottom: 'var(--spacing-xl)' }}>
          <h2>CVs ({stats.total_cvs})</h2>
          {cvs.length === 0 ? (
            <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-md)' }}>No CVs uploaded</p>
          ) : (
            <div className="candidates-table" style={{ marginTop: 'var(--spacing-lg)' }}>
              <table>
                <thead>
                  <tr>
                    <th>Version</th>
                    <th>Language</th>
                    <th>Uploaded By</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {cvs.map((cv) => (
                    <tr key={cv.id}>
                      <td><span className="badge badge-primary">v{cv.version}</span></td>
                      <td>{cv.language?.toUpperCase() || 'N/A'}</td>
                      <td>{cv.uploaded_by_flow}</td>
                      <td>{formatDate(cv.created_at)}</td>
                      <td>
                        <a href={cv.file_url} target="_blank" rel="noopener noreferrer" className="btn-view">
                          Download CV
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Analyses Section */}
        <div className="candidates-section">
          <h2>Analyses ({stats.total_analyses})</h2>
          {analyses.length === 0 ? (
            <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-md)' }}>No analyses performed</p>
          ) : (
            <div className="candidates-table" style={{ marginTop: 'var(--spacing-lg)' }}>
              <table>
                <thead>
                  <tr>
                    <th>Mode</th>
                    <th>Provider</th>
                    <th>Score</th>
                    <th>Language</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {analyses.map((analysis) => (
                    <tr key={analysis.id}>
                      <td>
                        {analysis.mode === 'interviewer' ? (
                          <span className="badge badge-primary">Interviewer</span>
                        ) : (
                          <span className="badge badge-success">Candidate</span>
                        )}
                      </td>
                      <td>{analysis.provider}</td>
                      <td>
                        <span style={{ color: getScoreColor(analysis.global_score), fontWeight: 'var(--font-weight-semibold)' }}>
                          {analysis.global_score ? `${analysis.global_score.toFixed(1)}%` : 'N/A'}
                        </span>
                      </td>
                      <td>{analysis.language.toUpperCase()}</td>
                      <td>{formatDate(analysis.created_at)}</td>
                      <td>
                        <Link to={`/admin/analyses/${analysis.id}`} className="btn-view">
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminCandidateDetail;

