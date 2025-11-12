import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import './AdminPrompts.css';

interface Prompt {
  id: string;
  prompt_key: string;
  name: string;
  content: string;
  category: string;
  description?: string;
  variables: string[];
  language: string;
  model_preferences: Record<string, any>;
  version: number;
  is_active: boolean;
  is_default: boolean;
  usage_count: number;
  last_used_at?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  admin_notes?: string;
}

interface PromptVersion {
  id: string;
  prompt_id: string;
  version: number;
  content: string;
  variables: string[];
  model_preferences: Record<string, any>;
  change_description?: string;
  created_at: string;
  created_by?: string;
}

const AdminPrompts: React.FC = () => {
  const navigate = useNavigate();
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  
  // Form state
  const [formData, setFormData] = useState<Partial<Prompt>>({
    prompt_key: '',
    name: '',
    content: '',
    category: 'general',
    description: '',
    variables: [],
    language: 'en',
    model_preferences: {},
    is_active: true,
    is_default: true,
    admin_notes: ''
  });
  
  // Filter state
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [activeFilter, setActiveFilter] = useState<string>('');
  const [languageFilter, setLanguageFilter] = useState<string>('');
  
  // Stats
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchPrompts();
    fetchStats();
  }, [categoryFilter, activeFilter, languageFilter]);

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (categoryFilter) params.append('category', categoryFilter);
      if (activeFilter !== '') params.append('is_active', activeFilter);
      if (languageFilter) params.append('language', languageFilter);
      
      const response = await api.get(`/api/admin/prompts?${params.toString()}`);
      setPrompts(response.data.prompts || []);
    } catch (err: any) {
      console.error('Error fetching prompts:', err);
      setError(err.response?.data?.detail || 'Failed to load prompts');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/admin/prompts/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchVersions = async (promptId: string) => {
    try {
      const response = await api.get(`/api/admin/prompts/${promptId}/versions`);
      setVersions(response.data.versions || []);
      setShowVersions(true);
    } catch (err) {
      console.error('Error fetching versions:', err);
      alert('Failed to load version history');
    }
  };

  const handleSelectPrompt = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setFormData({
      prompt_key: prompt.prompt_key,
      name: prompt.name,
      content: prompt.content,
      category: prompt.category,
      description: prompt.description || '',
      variables: prompt.variables,
      language: prompt.language,
      model_preferences: prompt.model_preferences,
      is_active: prompt.is_active,
      is_default: prompt.is_default,
      admin_notes: prompt.admin_notes || ''
    });
    setIsEditing(false);
    setShowVersions(false);
  };

  const handleCreate = () => {
    setIsCreating(true);
    setSelectedPrompt(null);
    setFormData({
      prompt_key: '',
      name: '',
      content: '',
      category: 'general',
      description: '',
      variables: [],
      language: 'en',
      model_preferences: {},
      is_active: true,
      is_default: true,
      admin_notes: ''
    });
  };

  const handleSaveCreate = async () => {
    try {
      await api.post('/api/admin/prompts/', formData);
      alert('Prompt created successfully!');
      setIsCreating(false);
      fetchPrompts();
      fetchStats();
    } catch (err: any) {
      console.error('Error creating prompt:', err);
      alert(err.response?.data?.detail || 'Failed to create prompt');
    }
  };

  const handleSaveEdit = async () => {
    if (!selectedPrompt) return;
    
    const changeDescription = prompt('Describe what changed in this version:');
    
    try {
      const updateData = {
        content: formData.content,
        name: formData.name,
        description: formData.description,
        variables: formData.variables,
        model_preferences: formData.model_preferences,
        is_active: formData.is_active,
        is_default: formData.is_default,
        admin_notes: formData.admin_notes,
        change_description: changeDescription || 'Updated prompt',
        create_new_version: true
      };
      
      await api.put(`/api/admin/prompts/${selectedPrompt.id}`, updateData);
      alert('Prompt updated successfully!');
      setIsEditing(false);
      fetchPrompts();
      fetchStats();
      
      // Refresh the selected prompt
      const response = await api.get(`/api/admin/prompts/${selectedPrompt.id}`);
      handleSelectPrompt(response.data);
    } catch (err: any) {
      console.error('Error updating prompt:', err);
      alert(err.response?.data?.detail || 'Failed to update prompt');
    }
  };

  const handleDelete = async (promptId: string) => {
    if (!window.confirm('Are you sure you want to deactivate this prompt?')) return;
    
    try {
      await api.delete(`/api/admin/prompts/${promptId}`);
      alert('Prompt deactivated successfully!');
      setSelectedPrompt(null);
      fetchPrompts();
      fetchStats();
    } catch (err: any) {
      console.error('Error deleting prompt:', err);
      alert(err.response?.data?.detail || 'Failed to delete prompt');
    }
  };

  const handleRollback = async (version: number) => {
    if (!selectedPrompt) return;
    
    if (!window.confirm(`Are you sure you want to rollback to version ${version}?`)) return;
    
    try {
      await api.post(`/api/admin/prompts/${selectedPrompt.id}/rollback/${version}`);
      alert(`Rolled back to version ${version} successfully!`);
      setShowVersions(false);
      
      // Refresh the prompt
      const response = await api.get(`/api/admin/prompts/${selectedPrompt.id}`);
      handleSelectPrompt(response.data);
      fetchPrompts();
    } catch (err: any) {
      console.error('Error rolling back:', err);
      alert(err.response?.data?.detail || 'Failed to rollback');
    }
  };

  const handleVariablesChange = (value: string) => {
    // Split by comma and trim
    const vars = value.split(',').map(v => v.trim()).filter(v => v);
    setFormData({ ...formData, variables: vars });
  };

  return (
    <div className="admin-prompts">
      <div className="admin-header">
        <h1>🤖 AI Prompts Management</h1>
        <button onClick={() => navigate('/admin')} className="btn-back">
          ← Back to Dashboard
        </button>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Prompts</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.active}</div>
            <div className="stat-label">Active</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.inactive}</div>
            <div className="stat-label">Inactive</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{Object.keys(stats.by_category || {}).length}</div>
            <div className="stat-label">Categories</div>
          </div>
        </div>
      )}

      <div className="prompts-container">
        {/* Left Panel - List */}
        <div className="prompts-list-panel">
          <div className="panel-header">
            <h2>Prompts</h2>
            <button onClick={handleCreate} className="btn-create">
              + New Prompt
            </button>
          </div>

          {/* Filters */}
          <div className="filters">
            <select 
              value={categoryFilter} 
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Categories</option>
              <option value="cv_extraction">CV Extraction</option>
              <option value="job_analysis">Job Analysis</option>
              <option value="candidate_evaluation">Candidate Evaluation</option>
              <option value="translation">Translation</option>
              <option value="reporting">Reporting</option>
              <option value="general">General</option>
            </select>

            <select 
              value={activeFilter} 
              onChange={(e) => setActiveFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Status</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>

            <select 
              value={languageFilter} 
              onChange={(e) => setLanguageFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All Languages</option>
              <option value="en">English</option>
              <option value="pt">Português</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
            </select>
          </div>

          {/* Prompts List */}
          {loading ? (
            <div className="loading">Loading prompts...</div>
          ) : error ? (
            <div className="error">{error}</div>
          ) : (
            <div className="prompts-list">
              {prompts.map((prompt) => (
                <div
                  key={prompt.id}
                  className={`prompt-item ${selectedPrompt?.id === prompt.id ? 'selected' : ''} ${!prompt.is_active ? 'inactive' : ''}`}
                  onClick={() => handleSelectPrompt(prompt)}
                >
                  <div className="prompt-item-header">
                    <strong>{prompt.name}</strong>
                    {!prompt.is_active && <span className="badge-inactive">Inactive</span>}
                  </div>
                  <div className="prompt-item-meta">
                    <span className="badge">{prompt.category}</span>
                    <span className="badge">{prompt.language}</span>
                    <span className="version">v{prompt.version}</span>
                  </div>
                  <div className="prompt-item-key">{prompt.prompt_key}</div>
                  <div className="prompt-item-stats">
                    Used {prompt.usage_count} times
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Panel - Detail/Edit */}
        <div className="prompts-detail-panel">
          {isCreating ? (
            <div className="prompt-editor">
              <div className="panel-header">
                <h2>Create New Prompt</h2>
                <div className="actions">
                  <button onClick={handleSaveCreate} className="btn-save">
                    Save
                  </button>
                  <button onClick={() => setIsCreating(false)} className="btn-cancel">
                    Cancel
                  </button>
                </div>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>Prompt Key *</label>
                  <input
                    type="text"
                    value={formData.prompt_key}
                    onChange={(e) => setFormData({ ...formData, prompt_key: e.target.value })}
                    placeholder="e.g., cv_extraction"
                  />
                  <small>Unique identifier used in code</small>
                </div>

                <div className="form-group">
                  <label>Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Human-readable name"
                  />
                </div>

                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    <option value="general">General</option>
                    <option value="cv_extraction">CV Extraction</option>
                    <option value="job_analysis">Job Analysis</option>
                    <option value="candidate_evaluation">Candidate Evaluation</option>
                    <option value="translation">Translation</option>
                    <option value="reporting">Reporting</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Language</label>
                  <select
                    value={formData.language}
                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                  >
                    <option value="en">English</option>
                    <option value="pt">Português</option>
                    <option value="fr">Français</option>
                    <option value="es">Español</option>
                  </select>
                </div>

                <div className="form-group full-width">
                  <label>Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="What does this prompt do?"
                    rows={2}
                  />
                </div>

                <div className="form-group full-width">
                  <label>Prompt Content *</label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    placeholder="The prompt template with {variable} placeholders"
                    rows={12}
                    className="code-textarea"
                  />
                  <small>Use {'{variable_name}'} for placeholders</small>
                </div>

                <div className="form-group full-width">
                  <label>Variables</label>
                  <input
                    type="text"
                    value={(formData.variables || []).join(', ')}
                    onChange={(e) => handleVariablesChange(e.target.value)}
                    placeholder="variable1, variable2, variable3"
                  />
                  <small>Comma-separated list of variables used in the prompt</small>
                </div>

                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    />
                    {' '}Active
                  </label>
                </div>

                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.is_default}
                      onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                    />
                    {' '}Default Version
                  </label>
                </div>

                <div className="form-group full-width">
                  <label>Admin Notes</label>
                  <textarea
                    value={formData.admin_notes}
                    onChange={(e) => setFormData({ ...formData, admin_notes: e.target.value })}
                    placeholder="Internal notes for admins"
                    rows={2}
                  />
                </div>
              </div>
            </div>
          ) : selectedPrompt ? (
            <div className="prompt-viewer">
              <div className="panel-header">
                <h2>{selectedPrompt.name}</h2>
                <div className="actions">
                  {!isEditing ? (
                    <>
                      <button onClick={() => setIsEditing(true)} className="btn-edit">
                        Edit
                      </button>
                      <button 
                        onClick={() => fetchVersions(selectedPrompt.id)} 
                        className="btn-secondary"
                      >
                        Version History
                      </button>
                      <button 
                        onClick={() => handleDelete(selectedPrompt.id)} 
                        className="btn-delete"
                      >
                        Deactivate
                      </button>
                    </>
                  ) : (
                    <>
                      <button onClick={handleSaveEdit} className="btn-save">
                        Save Changes
                      </button>
                      <button onClick={() => setIsEditing(false)} className="btn-cancel">
                        Cancel
                      </button>
                    </>
                  )}
                </div>
              </div>

              {showVersions ? (
                <div className="versions-panel">
                  <h3>Version History</h3>
                  <button onClick={() => setShowVersions(false)} className="btn-secondary">
                    ← Back to Prompt
                  </button>
                  
                  <div className="versions-list">
                    {versions.map((version) => (
                      <div key={version.id} className="version-item">
                        <div className="version-header">
                          <strong>Version {version.version}</strong>
                          <span className="version-date">
                            {new Date(version.created_at).toLocaleString()}
                          </span>
                        </div>
                        {version.change_description && (
                          <div className="version-description">
                            {version.change_description}
                          </div>
                        )}
                        {version.created_by && (
                          <div className="version-author">
                            by {version.created_by}
                          </div>
                        )}
                        <button
                          onClick={() => handleRollback(version.version)}
                          className="btn-rollback"
                          disabled={version.version === selectedPrompt.version}
                        >
                          {version.version === selectedPrompt.version ? 'Current' : 'Rollback to this'}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : isEditing ? (
                <div className="form-grid">
                  <div className="form-group">
                    <label>Name *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>

                  <div className="form-group">
                    <label>Category</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    >
                      <option value="general">General</option>
                      <option value="cv_extraction">CV Extraction</option>
                      <option value="job_analysis">Job Analysis</option>
                      <option value="candidate_evaluation">Candidate Evaluation</option>
                      <option value="translation">Translation</option>
                      <option value="reporting">Reporting</option>
                    </select>
                  </div>

                  <div className="form-group full-width">
                    <label>Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={2}
                    />
                  </div>

                  <div className="form-group full-width">
                    <label>Prompt Content *</label>
                    <textarea
                      value={formData.content}
                      onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                      rows={12}
                      className="code-textarea"
                    />
                  </div>

                  <div className="form-group full-width">
                    <label>Variables</label>
                    <input
                      type="text"
                      value={(formData.variables || []).join(', ')}
                      onChange={(e) => handleVariablesChange(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={formData.is_active}
                        onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      />
                      {' '}Active
                    </label>
                  </div>

                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={formData.is_default}
                        onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                      />
                      {' '}Default Version
                    </label>
                  </div>

                  <div className="form-group full-width">
                    <label>Admin Notes</label>
                    <textarea
                      value={formData.admin_notes}
                      onChange={(e) => setFormData({ ...formData, admin_notes: e.target.value })}
                      rows={2}
                    />
                  </div>
                </div>
              ) : (
                <div className="prompt-details">
                  <div className="detail-section">
                    <h3>Information</h3>
                    <div className="detail-grid">
                      <div className="detail-item">
                        <strong>Prompt Key:</strong>
                        <code>{selectedPrompt.prompt_key}</code>
                      </div>
                      <div className="detail-item">
                        <strong>Category:</strong>
                        <span className="badge">{selectedPrompt.category}</span>
                      </div>
                      <div className="detail-item">
                        <strong>Language:</strong>
                        <span className="badge">{selectedPrompt.language}</span>
                      </div>
                      <div className="detail-item">
                        <strong>Version:</strong>
                        <span>v{selectedPrompt.version}</span>
                      </div>
                      <div className="detail-item">
                        <strong>Status:</strong>
                        <span className={selectedPrompt.is_active ? 'status-active' : 'status-inactive'}>
                          {selectedPrompt.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="detail-item">
                        <strong>Usage:</strong>
                        <span>{selectedPrompt.usage_count} times</span>
                      </div>
                    </div>
                    {selectedPrompt.description && (
                      <div className="detail-item full-width">
                        <strong>Description:</strong>
                        <p>{selectedPrompt.description}</p>
                      </div>
                    )}
                  </div>

                  <div className="detail-section">
                    <h3>Prompt Content</h3>
                    <pre className="prompt-content">{selectedPrompt.content}</pre>
                  </div>

                  {selectedPrompt.variables && selectedPrompt.variables.length > 0 && (
                    <div className="detail-section">
                      <h3>Variables</h3>
                      <div className="variables-list">
                        {selectedPrompt.variables.map((variable: string) => (
                          <code key={variable} className="variable-badge">
                            {'{' + variable + '}'}
                          </code>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedPrompt.admin_notes && (
                    <div className="detail-section">
                      <h3>Admin Notes</h3>
                      <p className="admin-notes">{selectedPrompt.admin_notes}</p>
                    </div>
                  )}

                  <div className="detail-section">
                    <h3>Metadata</h3>
                    <div className="detail-grid">
                      <div className="detail-item">
                        <strong>Created:</strong>
                        <span>{new Date(selectedPrompt.created_at).toLocaleString()}</span>
                      </div>
                      {selectedPrompt.created_by && (
                        <div className="detail-item">
                          <strong>Created by:</strong>
                          <span>{selectedPrompt.created_by}</span>
                        </div>
                      )}
                      <div className="detail-item">
                        <strong>Updated:</strong>
                        <span>{new Date(selectedPrompt.updated_at).toLocaleString()}</span>
                      </div>
                      {selectedPrompt.updated_by && (
                        <div className="detail-item">
                          <strong>Updated by:</strong>
                          <span>{selectedPrompt.updated_by}</span>
                        </div>
                      )}
                      {selectedPrompt.last_used_at && (
                        <div className="detail-item">
                          <strong>Last used:</strong>
                          <span>{new Date(selectedPrompt.last_used_at).toLocaleString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">
              <h2>Select a prompt to view details</h2>
              <p>or</p>
              <button onClick={handleCreate} className="btn-create-large">
                + Create New Prompt
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPrompts;

