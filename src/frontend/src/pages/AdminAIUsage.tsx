import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import { exportAIUsageToCSV } from '@utils/exportCSV';
import './AdminCandidates.css';

interface AIUsageLog {
  id: string;
  mode: 'interviewer' | 'candidate';
  provider: string;
  language: string;
  created_at: string;
  candidate_id: string;
  job_posting_id: string;
  global_score?: number;
  estimated_cost: number;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
}

interface UsageSummary {
  total_calls: number;
  total_cost: number;
  provider_breakdown: Record<string, { 
    calls: number; 
    cost: number;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  }>;
}

const AdminAIUsage: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [logs, setLogs] = useState<AIUsageLog[]>([]);
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [providerFilter, setProviderFilter] = useState('');
  const [modeFilter, setModeFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  
  // Pagination
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 100,
    offset: 0,
    hasMore: false
  });

  useEffect(() => {
    loadUsageLogs();
  }, [pagination.offset, providerFilter, modeFilter, languageFilter, startDate, endDate]);

  const loadUsageLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
      });
      
      if (providerFilter) params.append('provider', providerFilter);
      if (modeFilter) params.append('mode', modeFilter);
      if (languageFilter) params.append('language', languageFilter);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await api.get(`/admin/ai-usage?${params}`);
      const data = response.data;
      
      setLogs(data.logs || []);
      setSummary(data.summary || null);
      setPagination(prev => ({
        ...prev,
        total: data.total || 0,
        hasMore: (data.offset || 0) + (data.limit || 100) < (data.total || 0)
      }));
    } catch (error: any) {
      console.error('Error loading AI usage logs:', error);
      setError(error.response?.data?.detail || 'Error loading AI usage logs');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = () => {
    // Reset to first page when filters change
    setPagination(prev => ({ ...prev, offset: 0 }));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getProviderBadge = (provider: string) => {
    const colors: Record<string, string> = {
      gemini: 'badge-primary',
      openai: 'badge-success',
      claude: 'badge-warning',
      kimi: 'badge-danger',
      minimax: 'badge-primary'
    };
    return (
      <span className={`badge ${colors[provider] || 'badge-primary'}`}>
        {provider.toUpperCase()}
      </span>
    );
  };

  const getModeBadge = (mode: string) => {
    return mode === 'interviewer' ? (
      <span className="badge badge-primary">Interviewer</span>
    ) : (
      <span className="badge badge-success">Candidate</span>
    );
  };

  const handleExport = () => {
    exportAIUsageToCSV(logs);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handlePrevious = () => {
    if (pagination.offset > 0) {
      setPagination(prev => ({
        ...prev,
        offset: Math.max(0, prev.offset - prev.limit)
      }));
    }
  };

  const handleNext = () => {
    if (pagination.hasMore) {
      setPagination(prev => ({
        ...prev,
        offset: prev.offset + prev.limit
      }));
    }
  };

  if (loading && logs.length === 0) {
    return (
      <div className="admin-candidates">
        <div className="admin-loading">
          <div className="loading-spinner"></div>
          <p>Loading AI usage logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-candidates">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/dashboard" className="back-link">← Back to Admin Dashboard</Link>
            <h1>AI Usage Logs</h1>
          </div>
          <div className="admin-user-info">
            <span>Welcome, {user?.username}</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="admin-content">
        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
            <button onClick={loadUsageLogs} style={{ marginLeft: '10px', padding: '5px 10px' }}>
              Retry
            </button>
          </div>
        )}

        {/* Summary Statistics */}
        {summary && (
          <div className="candidates-section" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>Usage Summary</h2>
            <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
              <div className="stat-card">
                <div className="stat-number">{summary.total_calls.toLocaleString()}</div>
                <div className="stat-label">Total API Calls</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">${summary.total_cost.toFixed(6)}</div>
                <div className="stat-label">Total Cost (Token-Based)</div>
              </div>
            </div>
            
            {Object.keys(summary.provider_breakdown).length > 0 && (
              <div>
                <h3 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Provider Breakdown</h3>
                <div className="providers-grid">
                  {Object.entries(summary.provider_breakdown).map(([provider, data]) => (
                    <div key={provider} className="provider-card">
                      <h3>{provider.toUpperCase()}</h3>
                      <div className="provider-stats">
                        <div>Calls: {data.calls.toLocaleString()}</div>
                        <div>Cost: ${data.cost.toFixed(6)}</div>
                        {(data.total_tokens || 0) > 0 && (
                          <>
                            <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                              Tokens: {(data.total_tokens || 0).toLocaleString()}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                              In: {(data.input_tokens || 0).toLocaleString()} | Out: {(data.output_tokens || 0).toLocaleString()}
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Filters */}
        <div className="candidates-section">
          <div className="section-header">
            <h2>Usage Logs</h2>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <span className="pagination-info">
                Showing {pagination.offset + 1}-{Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total}
              </span>
              <button onClick={handleExport} className="btn-secondary">
                Export CSV
              </button>
            </div>
          </div>

          <div className="candidates-controls">
            <div className="filter-box">
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                Provider
              </label>
              <select
                className="filter-select"
                value={providerFilter}
                onChange={(e) => {
                  setProviderFilter(e.target.value);
                  handleFilterChange();
                }}
              >
                <option value="">All Providers</option>
                <option value="gemini">Gemini</option>
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
                <option value="kimi">Kimi</option>
                <option value="minimax">Minimax</option>
              </select>
            </div>

            <div className="filter-box">
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                Mode
              </label>
              <select
                className="filter-select"
                value={modeFilter}
                onChange={(e) => {
                  setModeFilter(e.target.value);
                  handleFilterChange();
                }}
              >
                <option value="">All Modes</option>
                <option value="interviewer">Interviewer</option>
                <option value="candidate">Candidate</option>
              </select>
            </div>

            <div className="filter-box">
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                Language
              </label>
              <select
                className="filter-select"
                value={languageFilter}
                onChange={(e) => {
                  setLanguageFilter(e.target.value);
                  handleFilterChange();
                }}
              >
                <option value="">All Languages</option>
                <option value="en">English</option>
                <option value="pt">Portuguese</option>
                <option value="fr">French</option>
                <option value="es">Spanish</option>
              </select>
            </div>

            <div className="filter-box">
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                Start Date
              </label>
              <input
                type="date"
                className="search-input"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  handleFilterChange();
                }}
              />
            </div>

            <div className="filter-box">
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                End Date
              </label>
              <input
                type="date"
                className="search-input"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  handleFilterChange();
                }}
              />
            </div>
          </div>

          {/* Logs Table */}
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading logs...</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="empty-state">
              <p>No usage logs found</p>
            </div>
          ) : (
            <>
              <div className="candidates-table">
                <table>
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Provider</th>
                      <th>Mode</th>
                      <th>Language</th>
                      <th>Tokens</th>
                      <th>Score</th>
                      <th>Cost</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id}>
                        <td>{formatDate(log.created_at)}</td>
                        <td>{getProviderBadge(log.provider)}</td>
                        <td>{getModeBadge(log.mode)}</td>
                        <td>{log.language.toUpperCase()}</td>
                        <td>
                          {log.input_tokens != null && log.output_tokens != null ? (
                            <div style={{ fontSize: '0.875rem' }}>
                              <div>In: {(log.input_tokens || 0).toLocaleString()}</div>
                              <div>Out: {(log.output_tokens || 0).toLocaleString()}</div>
                              <div style={{ fontWeight: 600, marginTop: '0.25rem' }}>
                                Total: {(log.total_tokens || ((log.input_tokens || 0) + (log.output_tokens || 0))).toLocaleString()}
                              </div>
                            </div>
                          ) : (
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>N/A</span>
                          )}
                        </td>
                        <td>
                          {log.global_score !== undefined && log.global_score !== null ? (
                            <span style={{ fontWeight: 600 }}>
                              {(log.global_score * 100).toFixed(1)}%
                            </span>
                          ) : (
                            <span style={{ color: 'var(--text-secondary)' }}>N/A</span>
                          )}
                        </td>
                        <td>${log.estimated_cost.toFixed(6)}</td>
                        <td>
                          <Link
                            to={`/admin/analyses/${log.id}`}
                            className="btn-view"
                          >
                            View Details
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="pagination">
                <button
                  className="btn-pagination"
                  onClick={handlePrevious}
                  disabled={pagination.offset === 0}
                >
                  Previous
                </button>
                <span className="pagination-text">
                  Page {Math.floor(pagination.offset / pagination.limit) + 1} of {Math.ceil(pagination.total / pagination.limit)}
                </span>
                <button
                  className="btn-pagination"
                  onClick={handleNext}
                  disabled={!pagination.hasMore}
                >
                  Next
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminAIUsage;

