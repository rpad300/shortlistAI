import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import './AdminUsers.css';

interface AdminUser {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'admin' | 'super_admin';
  is_active: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

const AdminUsers: React.FC = () => {
  const { user, logout } = useAdminAuth();
  const navigate = useNavigate();
  const [admins, setAdmins] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedAdmin, setSelectedAdmin] = useState<AdminUser | null>(null);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 50,
    offset: 0,
    hasMore: false
  });

  useEffect(() => {
    // Check if user is super admin
    if (user?.role !== 'super_admin') {
      navigate('/admin/dashboard');
      return;
    }
    
    loadAdmins();
  }, [pagination.offset]);

  const loadAdmins = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/admin/list-users`);
      const data = response.data;
      
      setAdmins(data.admins);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        hasMore: data.offset + data.limit < data.total
      }));
    } catch (error: any) {
      console.error('Error loading admin users:', error);
      setError(error.response?.data?.detail || 'Error loading admin users');
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

  const getRoleBadge = (role: string) => {
    return role === 'super_admin' ? (
      <span className="badge badge-danger">Super Admin</span>
    ) : (
      <span className="badge badge-primary">Admin</span>
    );
  };

  const getStatusBadge = (isActive: boolean) => {
    return isActive ? (
      <span className="badge badge-success">Active</span>
    ) : (
      <span className="badge badge-warning">Inactive</span>
    );
  };

  const handleDelete = async (adminId: string) => {
    if (!confirm('Are you sure you want to deactivate this admin user?')) {
      return;
    }

    try {
      await api.delete(`/admin/delete-user/${adminId}`);
      loadAdmins(); // Reload the list
    } catch (error: any) {
      console.error('Error deleting admin:', error);
      alert(error.response?.data?.detail || 'Error deleting admin user');
    }
  };

  const CreateAdminModal = () => {
    const [formData, setFormData] = useState({
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'admin'
    });
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setSubmitting(true);

      try {
        // Create user via Supabase Auth Admin API
        await api.post('/admin/create-user', {
          email: formData.email,
          password: formData.password,
          email_confirm: true,
          user_metadata: {
            role: formData.role,
            first_name: formData.first_name,
            last_name: formData.last_name
          }
        });
        
        alert(`Admin user created successfully! Email: ${formData.email}`);
        setShowCreateModal(false);
        loadAdmins();
        setFormData({
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          role: 'admin'
        });
      } catch (error: any) {
        console.error('Error creating admin:', error);
        alert(error.response?.data?.detail || 'Error creating admin user');
      } finally {
        setSubmitting(false);
      }
    };

    return (
      <div className="modal-overlay">
        <div className="modal">
          <div className="modal-header">
            <h3>Create New Admin</h3>
            <button onClick={() => setShowCreateModal(false)} className="modal-close">×</button>
          </div>
          <form onSubmit={handleSubmit} className="modal-form">
            <div className="form-row">
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                  placeholder="admin@shortlistai.com"
                />
              </div>
              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                  minLength={8}
                  placeholder="Minimum 8 characters"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Role *</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                >
                  <option value="admin">Admin</option>
                  <option value="super_admin">Super Admin</option>
                </select>
              </div>
            </div>
            <div className="modal-actions">
              <button type="button" onClick={() => setShowCreateModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button type="submit" disabled={submitting} className="btn-primary">
                {submitting ? 'Creating...' : 'Create Admin'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="admin-users">
      <div className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin/dashboard" className="back-link">← Back to Dashboard</Link>
            <h1>Admin User Management</h1>
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

        <div className="users-section">
          <div className="section-header">
            <h2>Admin Users ({pagination.total})</h2>
            <button 
              onClick={() => setShowCreateModal(true)} 
              className="btn-primary"
            >
              Create New Admin
            </button>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading admin users...</p>
            </div>
          ) : admins.length === 0 ? (
            <div className="empty-state">
              <p>No admin users found.</p>
            </div>
          ) : (
            <div className="users-table">
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Last Login</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {admins.map((admin) => (
                    <tr key={admin.id}>
                      <td>
                        <div className="user-username">
                          <strong>{admin.username}</strong>
                        </div>
                      </td>
                      <td>
                        <div className="user-name">
                          {admin.first_name || admin.last_name 
                            ? `${admin.first_name || ''} ${admin.last_name || ''}`.trim()
                            : 'N/A'
                          }
                        </div>
                      </td>
                      <td>{admin.email}</td>
                      <td>{getRoleBadge(admin.role)}</td>
                      <td>{getStatusBadge(admin.is_active)}</td>
                      <td>
                        {admin.last_login_at 
                          ? formatDate(admin.last_login_at) 
                          : 'Never'
                        }
                      </td>
                      <td>{formatDate(admin.created_at)}</td>
                      <td>
                        <div className="user-actions">
                          <button 
                            onClick={() => {
                              setSelectedAdmin(admin);
                              setShowEditModal(true);
                            }}
                            className="btn-sm btn-secondary"
                          >
                            Edit
                          </button>
                          {admin.email !== user?.email && (
                            <button 
                              onClick={() => handleDelete(admin.id)}
                              className="btn-sm btn-danger"
                            >
                              Deactivate
                            </button>
                          )}
                        </div>
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

      {/* Create Admin Modal */}
      {showCreateModal && <CreateAdminModal />}
      
      {/* Edit Admin Modal - Simplified for now */}
      {showEditModal && selectedAdmin && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Edit Admin: {selectedAdmin.username}</h3>
              <button onClick={() => setShowEditModal(false)} className="modal-close">×</button>
            </div>
            <div className="modal-content">
              <p>Edit functionality coming soon...</p>
              <button onClick={() => setShowEditModal(false)} className="btn-primary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUsers;
