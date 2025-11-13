/**
 * Admin AI Settings Page
 * 
 * Allows admins to configure the AI provider fallback chain with specific models.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminAuth } from '@hooks/AdminAuthContext';
import api from '@services/api';
import './AdminDashboard.css';

interface Provider {
  name: string;
  display_name: string;
}

interface Model {
  id: string;
  name: string;
  display_name: string;
  max_output_tokens?: number;
  context_window?: number;
}

interface FallbackItem {
  provider: string;
  model: string | null;
  order: number;
}

const AdminAISettings: React.FC = () => {
  const { user } = useAdminAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [fallbackChain, setFallbackChain] = useState<FallbackItem[]>([]);
  const [availableProviders, setAvailableProviders] = useState<Provider[]>([]);
  const [modelsCache, setModelsCache] = useState<Record<string, Model[]>>({});

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError(null);

      const [chainResponse, providersResponse] = await Promise.all([
        api.get('/admin/settings/default-ai-provider'),
        api.get('/admin/settings/available-providers')
      ]);

      setFallbackChain(chainResponse.data.fallback_chain || []);
      setAvailableProviders(providersResponse.data.providers || []);
    } catch (err: any) {
      console.error('Error loading AI settings:', err);
      setError(err.response?.data?.detail || 'Failed to load AI settings');
    } finally {
      setLoading(false);
    }
  };

  const loadModelsForProvider = async (providerName: string): Promise<Model[]> => {
    if (modelsCache[providerName]) {
      return modelsCache[providerName];
    }

    try {
      const response = await api.get(`/admin/settings/providers/${providerName}/models`);
      const models = response.data.models || [];
      setModelsCache(prev => ({ ...prev, [providerName]: models }));
      return models;
    } catch (err: any) {
      console.error(`Error loading models for ${providerName}:`, err);
      return [];
    }
  };

  const handleAddItem = () => {
    const newOrder = fallbackChain.length > 0 
      ? Math.max(...fallbackChain.map(item => item.order)) + 1 
      : 1;
    
    setFallbackChain([...fallbackChain, {
      provider: availableProviders[0]?.name || '',
      model: null,
      order: newOrder
    }]);
  };

  const handleRemoveItem = (index: number) => {
    setFallbackChain(fallbackChain.filter((_, i) => i !== index).map((item, i) => ({
      ...item,
      order: i + 1
    })));
  };

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const newChain = [...fallbackChain];
    [newChain[index - 1], newChain[index]] = [newChain[index], newChain[index - 1]];
    newChain.forEach((item, i) => { item.order = i + 1; });
    setFallbackChain(newChain);
  };

  const handleMoveDown = (index: number) => {
    if (index === fallbackChain.length - 1) return;
    const newChain = [...fallbackChain];
    [newChain[index], newChain[index + 1]] = [newChain[index + 1], newChain[index]];
    newChain.forEach((item, i) => { item.order = i + 1; });
    setFallbackChain(newChain);
  };

  const handleProviderChange = async (index: number, providerName: string) => {
    const newChain = [...fallbackChain];
    newChain[index].provider = providerName;
    newChain[index].model = null; // Reset model when provider changes
    
    // Load models for the new provider
    const models = await loadModelsForProvider(providerName);
    if (models.length > 0) {
      newChain[index].model = models[0].id;
    }
    
    setFallbackChain(newChain);
  };

  const handleModelChange = (index: number, modelId: string) => {
    const newChain = [...fallbackChain];
    // Store the full model ID (important for Gemini which needs "models/" prefix)
    newChain[index].model = modelId || null;
    setFallbackChain(newChain);
  };

  const handleSave = async () => {
    if (fallbackChain.length === 0) {
      setError('Please add at least one provider to the fallback chain');
      return;
    }

    // Validate all items have providers
    for (const item of fallbackChain) {
      if (!item.provider) {
        setError('All items must have a provider selected');
        return;
      }
    }

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      await api.put('/admin/settings/default-ai-provider', fallbackChain);

      setSuccess(`Fallback chain updated with ${fallbackChain.length} provider(s)`);
      
      setTimeout(() => {
        loadSettings();
      }, 1500);
    } catch (err: any) {
      console.error('Error saving AI settings:', err);
      setError(err.response?.data?.detail || 'Failed to save AI settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="admin-loading">
          <div className="loading-spinner"></div>
          <p>Loading AI settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div className="admin-header-content">
          <h1>AI Provider Fallback Chain</h1>
          <div className="admin-user-info">
            <span>{user?.email}</span>
            <button className="logout-btn" onClick={() => navigate('/admin/dashboard')}>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="admin-content">
        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        {success && (
          <div style={{
            background: '#4caf50',
            color: 'white',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1.5rem',
            textAlign: 'center'
          }}>
            {success}
          </div>
        )}

        <div style={{
          background: 'var(--surface)',
          padding: '2rem',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          maxWidth: '1000px',
          margin: '0 auto'
        }}>
          <h2 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Fallback Chain Configuration</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Configure the order of AI providers and models to use. If one provider/model fails, 
            the system will automatically try the next one in the chain.
          </p>

          {availableProviders.length === 0 && (
            <div style={{
              padding: '1rem',
              background: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '8px',
              marginBottom: '1.5rem',
              color: '#856404'
            }}>
              <strong>No providers available.</strong> Please configure at least one AI provider API key in your environment variables.
            </div>
          )}

          <div style={{ marginBottom: '2rem' }}>
            {fallbackChain.map((item, index) => (
              <div
                key={index}
                style={{
                  padding: '1.5rem',
                  border: '2px solid var(--border)',
                  borderRadius: '8px',
                  marginBottom: '1rem',
                  background: 'var(--bg)',
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start'
                }}
              >
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  alignItems: 'center',
                  minWidth: '60px'
                }}>
                  <div style={{
                    background: 'var(--color-ai-blue)',
                    color: 'white',
                    borderRadius: '50%',
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 600,
                    fontSize: '0.875rem'
                  }}>
                    {item.order}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <button
                      onClick={() => handleMoveUp(index)}
                      disabled={index === 0}
                      style={{
                        padding: '0.25rem 0.5rem',
                        border: '1px solid var(--border)',
                        borderRadius: '4px',
                        background: index === 0 ? '#ccc' : 'var(--surface)',
                        cursor: index === 0 ? 'not-allowed' : 'pointer',
                        fontSize: '0.75rem'
                      }}
                      title="Move up"
                    >
                      ↑
                    </button>
                    <button
                      onClick={() => handleMoveDown(index)}
                      disabled={index === fallbackChain.length - 1}
                      style={{
                        padding: '0.25rem 0.5rem',
                        border: '1px solid var(--border)',
                        borderRadius: '4px',
                        background: index === fallbackChain.length - 1 ? '#ccc' : 'var(--surface)',
                        cursor: index === fallbackChain.length - 1 ? 'not-allowed' : 'pointer',
                        fontSize: '0.75rem'
                      }}
                      title="Move down"
                    >
                      ↓
                    </button>
                  </div>
                </div>

                <div style={{ flex: 1, display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <label style={{
                      display: 'block',
                      marginBottom: '0.5rem',
                      fontWeight: 600,
                      fontSize: '0.875rem'
                    }}>
                      Provider:
                    </label>
                    <select
                      value={item.provider}
                      onChange={(e) => handleProviderChange(index, e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        fontSize: '1rem',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        background: 'var(--bg)',
                        color: 'var(--text-primary)',
                        cursor: 'pointer'
                      }}
                    >
                      <option value="">-- Select Provider --</option>
                      {availableProviders.map((provider) => (
                        <option key={provider.name} value={provider.name}>
                          {provider.display_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div style={{ flex: 1 }}>
                    <label style={{
                      display: 'block',
                      marginBottom: '0.5rem',
                      fontWeight: 600,
                      fontSize: '0.875rem'
                    }}>
                      Model:
                    </label>
                    <ModelSelector
                      providerName={item.provider}
                      selectedModel={item.model}
                      onModelChange={(modelId) => handleModelChange(index, modelId)}
                      loadModels={loadModelsForProvider}
                    />
                  </div>

                  <button
                    onClick={() => handleRemoveItem(index)}
                    style={{
                      padding: '0.75rem 1rem',
                      border: '1px solid #dc3545',
                      borderRadius: '8px',
                      background: '#dc3545',
                      color: 'white',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      alignSelf: 'flex-end'
                    }}
                    title="Remove"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}

            {fallbackChain.length === 0 && (
              <div style={{
                padding: '2rem',
                textAlign: 'center',
                border: '2px dashed var(--border)',
                borderRadius: '8px',
                color: 'var(--text-secondary)'
              }}>
                No providers in fallback chain. Click "Add Provider" to get started.
              </div>
            )}
          </div>

          <div style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <button
              onClick={handleAddItem}
              disabled={availableProviders.length === 0}
              style={{
                padding: '0.75rem 1.5rem',
                border: '1px solid var(--color-ai-blue)',
                borderRadius: '8px',
                background: availableProviders.length === 0 ? '#ccc' : 'var(--color-ai-blue)',
                color: 'white',
                cursor: availableProviders.length === 0 ? 'not-allowed' : 'pointer',
                fontSize: '1rem',
                fontWeight: 600
              }}
            >
              + Add Provider
            </button>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                onClick={() => navigate('/admin/dashboard')}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  background: 'var(--surface)',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  fontSize: '1rem'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving || fallbackChain.length === 0 || availableProviders.length === 0}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: 'none',
                  borderRadius: '8px',
                  background: saving ? '#ccc' : 'var(--color-ai-blue)',
                  color: 'white',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  fontWeight: 600
                }}
              >
                {saving ? 'Saving...' : 'Save Fallback Chain'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Component to handle model selection with lazy loading
const ModelSelector: React.FC<{
  providerName: string;
  selectedModel: string | null;
  onModelChange: (modelId: string) => void;
  loadModels: (providerName: string) => Promise<Model[]>;
}> = ({ providerName, selectedModel, onModelChange, loadModels }) => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (providerName) {
      setLoading(true);
      loadModels(providerName).then(loadedModels => {
        setModels(loadedModels);
        setLoading(false);
        // Auto-select first model if none selected
        if (!selectedModel && loadedModels.length > 0) {
          onModelChange(loadedModels[0].id);
        }
      });
    } else {
      setModels([]);
    }
  }, [providerName]);

  if (!providerName) {
    return (
      <select disabled style={{
        width: '100%',
        padding: '0.75rem',
        fontSize: '1rem',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        background: '#f5f5f5',
        color: '#999'
      }}>
        <option>Select provider first</option>
      </select>
    );
  }

  if (loading) {
    return (
      <select disabled style={{
        width: '100%',
        padding: '0.75rem',
        fontSize: '1rem',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        background: '#f5f5f5',
        color: '#999'
      }}>
        <option>Loading models...</option>
      </select>
    );
  }

  return (
    <select
      value={selectedModel || ''}
      onChange={(e) => onModelChange(e.target.value)}
      style={{
        width: '100%',
        padding: '0.75rem',
        fontSize: '1rem',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        background: 'var(--bg)',
        color: 'var(--text-primary)',
        cursor: 'pointer'
      }}
    >
      <option value="">-- Use Default Model --</option>
      {models.map((model) => {
        const tokenInfo = model.max_output_tokens 
          ? ` | Max: ${model.max_output_tokens.toLocaleString()} tokens`
          : '';
        const contextInfo = model.context_window
          ? ` | Context: ${(model.context_window / 1000).toFixed(0)}K`
          : '';
        return (
          <option key={model.id} value={model.id}>
            {model.display_name}{tokenInfo}{contextInfo}
          </option>
        );
      })}
    </select>
  );
};

export default AdminAISettings;
