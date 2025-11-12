import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import { exportAnalysesToCSV } from '@utils/exportCSV';
import './AdminCandidates.css';

interface Analysis {
  id: string;
  mode: 'interviewer' | 'candidate';
  provider: string;
  global_score?: number;
  language: string;
  created_at: string;
  candidate_id: string;
  job_posting_id: string;
}

const AdminAnalyses: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modeFilter, setModeFilter] = useState('');
  const [providerFilter, setProviderFilter] = useState('');
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    hasMore: false
  });

  useEffect(() => {
    loadAnalyses();
  }, [pagination.offset, modeFilter, providerFilter]);

  const loadAnalyses = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
      });
      
      if (modeFilter) params.append('mode', modeFilter);
      if (providerFilter) params.append('provider', providerFilter);

      const response = await api.get(`/api/admin/analyses?${params}`);
      const data = response.data;
      
      setAnalyses(data.analyses);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        hasMore: data.offset + data.limit < data.total
      }));
    } catch (error: any) {
      console.error('Error loading analyses:', error);
      setError(error.response?.data?.detail || 'Error loading analyses');
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

  const getModeBadge = (mode: string) => {
    return mode === 'interviewer' ? (
      <span className="badge badge-primary">Interviewer</span>
    ) : (
      <span className="badge badge-success">Candidate</span>
    );
  };

  const getScoreColor = (score?: number): React.CSSProperties => {
    if (!score) return {};
    if (score >= 75) return { color: 'var(--color-success)' };
    if (score >= 50) return { color: 'var(--color-warning)' };
    return { color: 'var(--color-error)' };
  };

  return (
    <div className="admin-candidates">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/dashboard" className="back-link">← Back to Dashboard</Link>
            <h1>Analyses Management</h1>
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
        {error && <div className="error-banner">{error}</div>}

        <div className="candidates-controls">
          <div className="filter-box">
            <select value={modeFilter} onChange={(e) => setModeFilter(e.target.value)} className="filter-select">
              <option value="">All Modes</option>
              <option value="interviewer">Interviewer</option>
              <option value="candidate">Candidate</option>
            </select>
          </div>
          <div className="filter-box">
            <select value={providerFilter} onChange={(e) => setProviderFilter(e.target.value)} className="filter-select">
              <option value="">All Providers</option>
              <option value="gemini">Gemini</option>
              <option value="openai">OpenAI</option>
              <option value="claude">Claude</option>
              <option value="kimi">Kimi</option>
              <option value="minimax">Minimax</option>
            </select>
          </div>
        </div>

        <div className="candidates-section">
          <div className="section-header">
            <h2>Analyses ({pagination.total})</h2>
            <div style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'center' }}>
              <button onClick={() => exportAnalysesToCSV(analyses)} className="btn-secondary" style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}>
                Export CSV
              </button>
              <div className="pagination-info">
                Showing {pagination.offset + 1}-{Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total}
              </div>
            </div>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading analyses...</p>
            </div>
          ) : analyses.length === 0 ? (
            <div className="empty-state">
              <p>No analyses found.</p>
            </div>
          ) : (
            <div className="candidates-table">
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
                      <td>{getModeBadge(analysis.mode)}</td>
                      <td>{analysis.provider}</td>
                      <td>
                        <span style={getScoreColor(analysis.global_score)}>
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

          <div className="pagination">
            <button onClick={() => setPagination(prev => ({ ...prev, offset: Math.max(0, prev.offset - prev.limit) }))} disabled={pagination.offset === 0} className="btn-pagination">
              Previous
            </button>
            <span className="pagination-text">
              Page {Math.floor(pagination.offset / pagination.limit) + 1} of {Math.ceil(pagination.total / pagination.limit) || 1}
            </span>
            <button onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }))} disabled={!pagination.hasMore} className="btn-pagination">
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalyses;

