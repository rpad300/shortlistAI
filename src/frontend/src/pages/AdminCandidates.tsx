import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import { exportCandidatesToCSV } from '@utils/exportCSV';
import './AdminCandidates.css';

interface Candidate {
  id: string;
  email: string;
  name: string;
  phone?: string;
  country?: string;
  consent_given: boolean;
  consent_timestamp?: string;
  created_at: string;
  updated_at: string;
}

interface CandidatesResponse {
  total: number;
  limit: number;
  offset: number;
  candidates: Candidate[];
}

const AdminCandidates: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    hasMore: false
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [countryFilter, setCountryFilter] = useState('');

  useEffect(() => {
    loadCandidates();
  }, [pagination.offset, searchTerm, countryFilter]);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
      });

      const response = await api.get(`/api/admin/candidates?${params}`);
      const data: CandidatesResponse = response.data;
      
      setCandidates(data.candidates);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        hasMore: data.offset + data.limit < data.total
      }));
    } catch (error: any) {
      console.error('Error loading candidates:', error);
      setError(error.response?.data?.detail || 'Error loading candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleNextPage = () => {
    if (pagination.hasMore) {
      setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }));
    }
  };

  const handlePrevPage = () => {
    if (pagination.offset > 0) {
      setPagination(prev => ({ ...prev, offset: Math.max(0, prev.offset - prev.limit) }));
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

  const getConsentBadge = (consentGiven: boolean) => {
    return consentGiven ? (
      <span className="badge badge-success">Consent Given</span>
    ) : (
      <span className="badge badge-warning">No Consent</span>
    );
  };

  return (
    <div className="admin-candidates">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/dashboard" className="back-link">← Back to Dashboard</Link>
            <h1>Candidates Management</h1>
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
        {error && <div className="error-banner">{error}</div>}

        {/* Filters and Search */}
        <div className="candidates-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          <div className="filter-box">
            <select
              value={countryFilter}
              onChange={(e) => setCountryFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Countries</option>
              {/* This would be populated from actual data in a real implementation */}
              <option value="US">United States</option>
              <option value="UK">United Kingdom</option>
              <option value="CA">Canada</option>
              <option value="AU">Australia</option>
            </select>
          </div>
        </div>

        {/* Candidates List */}
        <div className="candidates-section">
          <div className="section-header">
            <h2>Candidates ({pagination.total})</h2>
            <div style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'center' }}>
              <button onClick={() => exportCandidatesToCSV(candidates)} className="btn-secondary" style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}>
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
              <p>Loading candidates...</p>
            </div>
          ) : candidates.length === 0 ? (
            <div className="empty-state">
              <p>No candidates found.</p>
            </div>
          ) : (
            <div className="candidates-table">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Country</th>
                    <th>Consent</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.map((candidate) => (
                    <tr key={candidate.id}>
                      <td>
                        <div className="candidate-name">
                          <strong>{candidate.name}</strong>
                          {candidate.phone && (
                            <div className="candidate-phone">{candidate.phone}</div>
                          )}
                        </div>
                      </td>
                      <td>{candidate.email}</td>
                      <td>{candidate.country || 'N/A'}</td>
                      <td>
                        {getConsentBadge(candidate.consent_given)}
                        {candidate.consent_timestamp && (
                          <div className="consent-date">
                            {formatDate(candidate.consent_timestamp)}
                          </div>
                        )}
                      </td>
                      <td>{formatDate(candidate.created_at)}</td>
                      <td>
                        <Link 
                          to={`/admin/candidates/${candidate.id}`}
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
          )}

          {/* Pagination */}
          <div className="pagination">
            <button
              onClick={handlePrevPage}
              disabled={pagination.offset === 0}
              className="btn-pagination"
            >
              Previous
            </button>
            <span className="pagination-text">
              Page {Math.floor(pagination.offset / pagination.limit) + 1} of {Math.ceil(pagination.total / pagination.limit)}
            </span>
            <button
              onClick={handleNextPage}
              disabled={!pagination.hasMore}
              className="btn-pagination"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminCandidates;
