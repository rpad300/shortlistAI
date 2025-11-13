/**
 * Interviewer Flow - Step 5: Upload CVs (Batch)
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import StepLayout from '@components/StepLayout';
import FileUpload from '@components/FileUpload';
import Button from '@components/Button';
import StepHelper from '@components/StepHelper';
import AILoadingOverlay from '@components/AILoadingOverlay';
import { interviewerAPI } from '@services/api';
import './InterviewerStep1.css';

const InterviewerStep5: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState('');
  
  // Handler to ADD files (not replace)
  const handleAddFiles = (newFiles: File[]) => {
    setFiles(prevFiles => {
      // Avoid duplicates by checking file name and size
      const existingKeys = new Set(prevFiles.map(f => `${f.name}-${f.size}`));
      const uniqueNewFiles = newFiles.filter(f => !existingKeys.has(`${f.name}-${f.size}`));
      return [...prevFiles, ...uniqueNewFiles];
    });
  };
  
  // Handler to REMOVE a specific file
  const handleRemoveFile = (index: number) => {
    setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const sessionId = sessionStorage.getItem('interviewer_session_id');
    if (!sessionId) {
      setError('Session not found.');
      return;
    }
    
    if (files.length === 0) {
      setError('Please upload at least one CV.');
      return;
    }
    
    setLoading(true);
    setError('');
    setUploadProgress(`Uploading ${files.length} CV(s)... This may take ${Math.ceil(files.length * 15 / 60)} minute(s)`);
    
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      files.forEach(file => {
        formData.append('files', file);
      });
      
      // Update progress message during upload
      setUploadProgress(`Processing ${files.length} CV(s)... Please wait (this may take a few minutes)`);
      
      const response = await interviewerAPI.step5(formData);
      
      const { files_processed, files_failed } = response.data;
      
      if (files_failed > 0) {
        setUploadProgress(`✅ Processed ${files_processed} CVs. ${files_failed} failed.`);
        // Still allow to proceed
        setTimeout(() => navigate('/interviewer/step6'), 2000);
      } else {
        navigate('/interviewer/step6');
      }
      
    } catch (error: any) {
      console.error('Error in step 5:', error);
      setError(error.response?.data?.detail || 'An error occurred uploading CVs.');
      setUploadProgress('');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <StepLayout>
      <div className="step-container">
        <div className="step-content">
        <h1>{t('interviewer.step5_title')}</h1>
        <p className="step-subtitle">Upload all CVs you want to analyze (multiple files supported)</p>
        
        <StepHelper
          title="📤 How to upload CVs?"
          type="tip"
          defaultOpen={true}
          content={
            <div>
              <p><strong>Goal:</strong> Upload all candidate CVs you want to analyze.</p>
              <p style={{ marginTop: '12px' }}><strong>✨ You can:</strong></p>
              <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
                <li>Select multiple files at once</li>
                <li>Add more files by selecting again (they will be ADDED, not replaced)</li>
                <li>Remove individual CVs by clicking the red ✕ button</li>
                <li>Upload when ready - all selected CVs will be processed together</li>
              </ul>
              <p style={{ marginTop: '12px' }}><strong>💡 Tip:</strong> Our AI will automatically extract candidate names and information from each CV.</p>
              <p><strong>⏱️ Processing:</strong> Instant upload + ~10-20 seconds AI summary per CV</p>
            </div>
          }
        />
        
        <AILoadingOverlay 
          isVisible={loading}
          message={`Uploading and processing ${files.length} CV(s)`}
          estimatedSeconds={files.length * 15}
        />
        
        <form onSubmit={handleSubmit} className="step-form">
          <div className="form-section">
            <FileUpload
              onFileSelect={handleAddFiles}
              multiple={true}
              accept=".pdf,.docx,.doc"
              maxSizeMB={10}
              label="Add CVs (PDF, DOCX) - You can add multiple times"
              hideFileList={true}
            />
            
            {files.length > 0 && (
              <div style={{ marginTop: 'var(--spacing-md)' }}>
                <div style={{ 
                  padding: 'var(--spacing-md)', 
                  backgroundColor: 'var(--color-accent-light)', 
                  borderRadius: 'var(--radius-md)',
                  marginBottom: 'var(--spacing-md)'
                }}>
                  <strong>{files.length} CV(s) ready to upload</strong>
                </div>
                
                {/* List of selected files with remove button */}
                <div style={{ 
                  maxHeight: '300px', 
                  overflowY: 'auto',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--spacing-sm)'
                }}>
                  {files.map((file, index) => (
                    <div 
                      key={`${file.name}-${index}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: 'var(--spacing-sm)',
                        marginBottom: 'var(--spacing-xs)',
                        backgroundColor: 'var(--color-bg-secondary)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)'
                      }}
                    >
                      <div style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        📄 {file.name}
                        <span style={{ 
                          marginLeft: 'var(--spacing-sm)', 
                          fontSize: 'var(--font-size-xs)', 
                          color: 'var(--color-text-secondary)' 
                        }}>
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveFile(index)}
                        style={{
                          background: 'var(--color-error)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '50%',
                          width: '24px',
                          height: '24px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          marginLeft: 'var(--spacing-sm)'
                        }}
                        title="Remove CV"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {uploadProgress && (
            <div style={{ padding: 'var(--spacing-md)', backgroundColor: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--spacing-md)' }}>
              {uploadProgress}
            </div>
          )}
          
          {error && <div className="error-banner">{error}</div>}
          
          <div className="form-actions">
            <Button type="button" variant="outline" onClick={() => navigate('/interviewer/step4')}>
              {t('common.previous')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={loading || files.length === 0}
            >
              {loading ? 'Uploading...' : `Upload ${files.length} CV(s)`}
            </Button>
          </div>
        </form>
      </div>
    </div>
    </StepLayout>
  );
};

export default InterviewerStep5;

