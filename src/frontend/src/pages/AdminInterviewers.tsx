import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import { exportInterviewersToCSV } from '@utils/exportCSV';
import './AdminCandidates.css';

interface Interviewer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  country?: string;
  company_id?: string;
  consent_given: boolean;
  created_at: string;
}

const AdminInterviewers: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [interviewers, setInterviewers] = useState<Interviewer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    hasMore: false
  });

  useEffect(() => {
    loadInterviewers();
  }, [pagination.offset]);

  const loadInterviewers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
      });

      const response = await api.get(`/api/admin/interviewers?${params}`);
      const data = response.data;
      
      setInterviewers(data.interviewers);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        hasMore: data.offset + data.limit < data.total
      }));
    } catch (error: any) {
      console.error('Error loading interviewers:', error);
      setError(error.response?.data?.detail || 'Error loading interviewers');
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

  return (
    <div className="admin-candidates">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/dashboard" className="back-link">← Back to Dashboard</Link>
            <h1>Interviewers Management</h1>
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
            <h2>Interviewers ({pagination.total})</h2>
            <button onClick={() => exportInterviewersToCSV(interviewers)} className="btn-secondary" style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}>
              Export CSV
            </button>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading interviewers...</p>
            </div>
          ) : interviewers.length === 0 ? (
            <div className="empty-state">
              <p>No interviewers found.</p>
            </div>
          ) : (
            <div className="candidates-table">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Country</th>
                    <th>Consent</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {interviewers.map((interviewer) => (
                    <tr key={interviewer.id}>
                      <td><strong>{interviewer.name}</strong></td>
                      <td>{interviewer.email}</td>
                      <td>{interviewer.phone || 'N/A'}</td>
                      <td>{interviewer.country || 'N/A'}</td>
                      <td>
                        {interviewer.consent_given ? (
                          <span className="badge badge-success">Yes</span>
                        ) : (
                          <span className="badge badge-warning">No</span>
                        )}
                      </td>
                      <td>{formatDate(interviewer.created_at)}</td>
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

export default AdminInterviewers;

