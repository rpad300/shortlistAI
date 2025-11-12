import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import { exportCompaniesToCSV } from '@utils/exportCSV';
import './AdminCandidates.css';

interface Company {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

const AdminCompanies: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    hasMore: false
  });

  useEffect(() => {
    loadCompanies();
  }, [pagination.offset]);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
      });

      const response = await api.get(`/api/admin/companies?${params}`);
      const data = response.data;
      
      setCompanies(data.companies);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        hasMore: data.offset + data.limit < data.total
      }));
    } catch (error: any) {
      console.error('Error loading companies:', error);
      setError(error.response?.data?.detail || 'Error loading companies');
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

  const filteredCompanies = companies.filter(company => 
    company.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="admin-candidates">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/dashboard" className="back-link">← Back to Dashboard</Link>
            <h1>Companies Management</h1>
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
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by company name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
        </div>

        <div className="candidates-section">
          <div className="section-header">
            <h2>Companies ({filteredCompanies.length})</h2>
            <button onClick={() => exportCompaniesToCSV(filteredCompanies)} className="btn-secondary" style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}>
              Export CSV
            </button>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading companies...</p>
            </div>
          ) : filteredCompanies.length === 0 ? (
            <div className="empty-state">
              <p>No companies found.</p>
            </div>
          ) : (
            <div className="candidates-table">
              <table>
                <thead>
                  <tr>
                    <th>Company Name</th>
                    <th>Created</th>
                    <th>Last Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCompanies.map((company) => (
                    <tr key={company.id}>
                      <td><strong>{company.name}</strong></td>
                      <td>{formatDate(company.created_at)}</td>
                      <td>{formatDate(company.updated_at)}</td>
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

export default AdminCompanies;

