import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import { exportJobPostingsToCSV } from '@utils/exportCSV';
import './AdminCandidates.css';

interface JobPosting {
  id: string;
  raw_text: string;
  language?: string;
  created_at: string;
  company_id?: string;
  interviewer_id?: string;
  candidate_id?: string;
}

const AdminJobPostings: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    hasMore: false
  });

  useEffect(() => {
    loadJobPostings();
  }, [pagination.offset]);

  const loadJobPostings = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
      });

      const response = await api.get(`/api/admin/job-postings?${params}`);
      const data = response.data;
      
      setJobPostings(data.job_postings);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        hasMore: data.offset + data.limit < data.total
      }));
    } catch (error: any) {
      console.error('Error loading job postings:', error);
      setError(error.response?.data?.detail || 'Error loading job postings');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="admin-candidates">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/dashboard" className="back-link">← Back to Dashboard</Link>
            <h1>Job Postings Management</h1>
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

        <div className="candidates-section">
          <div className="section-header">
            <h2>Job Postings ({pagination.total})</h2>
            <button onClick={() => exportJobPostingsToCSV(jobPostings)} className="btn-secondary" style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}>
              Export CSV
            </button>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading job postings...</p>
            </div>
          ) : jobPostings.length === 0 ? (
            <div className="empty-state">
              <p>No job postings found.</p>
            </div>
          ) : (
            <div className="candidates-table">
              <table>
                <thead>
                  <tr>
                    <th>Job Description</th>
                    <th>Language</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobPostings.map((posting) => (
                    <tr key={posting.id}>
                      <td>
                        <div style={{ maxWidth: '400px' }}>
                          {truncateText(posting.raw_text, 150)}
                        </div>
                      </td>
                      <td>{posting.language?.toUpperCase() || 'N/A'}</td>
                      <td>{formatDate(posting.created_at)}</td>
                      <td>
                        <button className="btn-view" onClick={() => alert(posting.raw_text)}>
                          View Full
                        </button>
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

export default AdminJobPostings;

