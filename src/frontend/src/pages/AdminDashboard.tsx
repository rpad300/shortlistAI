import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import './AdminDashboard.css';

interface DashboardStats {
  overview: {
    total_candidates: number;
    total_companies: number;
    total_interviewers: number;
    total_job_postings: number;
    total_analyses: number;
    total_cvs: number;
  };
  activity: {
    analyses_this_month: number;
    new_candidates_this_month: number;
    new_companies_this_month: number;
    new_job_postings_this_month: number;
  };
  ai_usage: {
    total_api_calls: number;
    cost_this_month: number;
    average_response_time: number;
    success_rate: number;
  };
  providers?: Record<string, { calls: number; cost: number }>;
  languages?: Record<string, number>;
}

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Prevent multiple simultaneous calls

  useEffect(() => {
    // Only load stats when user is authenticated and we don't have stats yet
    if (user && !stats && !isLoading) {
      loadDashboardStats();
    } else if (!user) {
      // Reset stats when user logs out
      setStats(null);
      setLoading(false);
      setIsLoading(false);
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadDashboardStats = async () => {
    // Prevent multiple simultaneous calls
    if (isLoading) {
      console.log('[AdminDashboard] Already loading, skipping...');
      return;
    }
    
    setIsLoading(true);
    try {
      setLoading(true);
      setError('');
      console.log('[AdminDashboard] Fetching dashboard stats...');
      const response = await api.get('/admin/dashboard/detailed-stats');
      console.log('[AdminDashboard] Response received:', response);
      console.log('[AdminDashboard] Response.data:', response.data);
      console.log('[AdminDashboard] Response.data type:', typeof response.data);
      console.log('[AdminDashboard] Response.data keys:', response.data ? Object.keys(response.data) : 'null');
      
      if (response.data) {
        console.log('[AdminDashboard] Setting stats with:', response.data);
        setStats(response.data);
        setError(''); // Clear any previous errors on success
        console.log('[AdminDashboard] Stats set, checking overview:', response.data.overview);
      } else {
        console.warn('[AdminDashboard] Response data is empty');
        setError('No data received from server');
      }
    } catch (error: any) {
      console.error('[AdminDashboard] Error loading dashboard stats:', error);
      console.error('[AdminDashboard] Error response:', error.response);
      setError(error.response?.data?.detail || error.message || 'Error loading dashboard statistics');
    } finally {
      setLoading(false);
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Debug: Log current state
  console.log('[AdminDashboard] Render - loading:', loading, 'stats:', stats, 'error:', error);
  if (stats) {
    console.log('[AdminDashboard] Render - stats.overview:', stats.overview);
  }

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="admin-loading">
          <div className="loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div className="admin-header-content">
          <h1>Admin Dashboard</h1>
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
            <button onClick={loadDashboardStats} style={{ marginLeft: '10px', padding: '5px 10px' }}>
              Retry
            </button>
          </div>
        )}
        
        {!stats && !loading && !error && (
          <div className="error-banner">
            No data available. <button onClick={loadDashboardStats} style={{ marginLeft: '10px', padding: '5px 10px' }}>Retry</button>
          </div>
        )}
        
        {/* Debug: Show raw stats */}
        {stats && (
          <div style={{ padding: '1rem', background: '#f0f0f0', marginBottom: '1rem', fontSize: '0.8rem', color: '#000' }}>
            <strong>DEBUG:</strong> stats exists: {stats ? 'YES' : 'NO'}, 
            stats.overview: {stats.overview ? 'YES' : 'NO'},
            stats.overview?.total_candidates: {stats.overview?.total_candidates},
            Condition check: {stats && stats.overview ? 'TRUE' : 'FALSE'}
          </div>
        )}
        
        {/* Force render test */}
        {stats && stats.overview ? (
          <>
            {/* Overview Statistics */}
            <div className="stats-grid" style={{ border: '2px solid red', padding: '1rem' }}>
              <div style={{ color: 'red', fontSize: '1.5rem', marginBottom: '1rem' }}>
                DEBUG: Stats grid is rendering! Stats.overview exists: {stats.overview ? 'YES' : 'NO'}
              </div>
              <div className="stat-card">
                <div className="stat-number">{stats.overview.total_candidates}</div>
                <div className="stat-label">Total Candidates</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{stats.overview.total_analyses}</div>
                <div className="stat-label">Total Analyses</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{stats.overview.total_companies}</div>
                <div className="stat-label">Total Companies</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{stats.overview.total_interviewers}</div>
                <div className="stat-label">Total Interviewers</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{stats.overview.total_job_postings}</div>
                <div className="stat-label">Job Postings</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{stats.overview.total_cvs}</div>
                <div className="stat-label">CVs Processed</div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="activity-section">
              <h2>Recent Activity</h2>
              <div className="activity-grid">
                <div className="activity-card">
                  <h3>Analyses This Month</h3>
                  <div className="activity-number">{stats.activity.analyses_this_month}</div>
                </div>
                <div className="activity-card">
                  <h3>New Candidates</h3>
                  <div className="activity-number">{stats.activity.new_candidates_this_month}</div>
                </div>
                <div className="activity-card">
                  <h3>New Companies</h3>
                  <div className="activity-number">{stats.activity.new_companies_this_month}</div>
                </div>
                <div className="activity-card">
                  <h3>New Job Postings</h3>
                  <div className="activity-number">{stats.activity.new_job_postings_this_month}</div>
                </div>
              </div>
            </div>

            {/* Management Links */}
            <div className="management-section">
              <h2>Data Management</h2>
              <div className="management-grid">
                <Link to="/admin/candidates" className="management-card">
                  <h3>Candidates</h3>
                  <p>View and manage all candidates</p>
                </Link>
                <Link to="/admin/analyses" className="management-card">
                  <h3>Analyses</h3>
                  <p>View all AI analyses and results</p>
                </Link>
                <Link to="/admin/companies" className="management-card">
                  <h3>Companies</h3>
                  <p>Manage company information</p>
                </Link>
                <Link to="/admin/interviewers" className="management-card">
                  <h3>Interviewers</h3>
                  <p>View interviewer contacts</p>
                </Link>
                <Link to="/admin/job-postings" className="management-card">
                  <h3>Job Postings</h3>
                  <p>Manage job postings</p>
                </Link>
                <Link to="/admin/prompts" className="management-card">
                  <h3>🤖 AI Prompts</h3>
                  <p>Manage and edit AI prompt templates</p>
                </Link>
                <Link to="/admin/ai-settings" className="management-card">
                  <h3>⚙️ AI Provider Settings</h3>
                  <p>Configure default AI provider</p>
                </Link>
                <Link to="/admin/ai-usage" className="management-card">
                  <h3>AI Usage Logs</h3>
                  <p>Track AI provider usage and costs</p>
                </Link>
                {/* Only show Admin Users Management for super admins */}
                {user?.role === 'super_admin' && (
                  <Link to="/admin/users" className="management-card">
                    <h3>Admin Users</h3>
                    <p>Manage administrator accounts</p>
                  </Link>
                )}
              </div>
            </div>

            {/* AI Providers */}
            {stats.providers && (
            <div className="providers-section">
              <h2>AI Provider Usage</h2>
              <div className="providers-grid">
                {Object.entries(stats.providers).map(([provider, data]) => (
                  <div key={provider} className="provider-card">
                    <h3>{provider.toUpperCase()}</h3>
                    <div className="provider-stats">
                      <div>Calls: {data.calls}</div>
                      <div>Cost: ${data.cost.toFixed(4)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            )}

            {/* Language Distribution */}
            {stats.languages && (
            <div className="languages-section">
              <h2>Language Distribution</h2>
              <div className="languages-grid">
                {Object.entries(stats.languages).map(([lang, count]) => (
                  <div key={lang} className="language-card">
                    <span className="language-code">{lang.toUpperCase()}</span>
                    <span className="language-count">{count}</span>
                  </div>
                ))}
              </div>
            </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
