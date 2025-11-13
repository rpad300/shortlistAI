/**
 * Interviewer Flow - Step 5: Upload CVs (Batch)
 */

import React, { useState, useEffect } from 'react';
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
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [processingProgress, setProcessingProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  
  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if ((window as any).__step5PollInterval) {
        clearInterval((window as any).__step5PollInterval);
        delete (window as any).__step5PollInterval;
      }
    };
  }, []);
  
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
    setIsProcessing(true);
    setUploadProgress(`Starting upload of ${files.length} CV(s)...`);
    setProcessingStatus('Starting upload...');
    setProcessingProgress(0);
    setTotalFiles(files.length);
    
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      files.forEach(file => {
        formData.append('files', file);
      });
      
      console.log(`[Step5] Starting upload of ${files.length} CV(s)`);
      
      // Start upload (returns immediately, processing happens in background)
      const response = await interviewerAPI.step5(formData);
      
      if (response.data.status === 'already_running') {
        setProcessingStatus('Upload already in progress...');
      } else {
        setProcessingStatus('Upload started! Processing CVs...');
        setTotalFiles(response.data.total_files || files.length);
      }
      
      // Start polling for progress
      const pollInterval = setInterval(async () => {
        try {
          const progressResponse = await interviewerAPI.step5Progress(sessionId);
          const progressData = progressResponse.data;
          
          const progressInfo = progressData.progress || {};
          const current = progressInfo.current || 0;
          const total = progressInfo.total || totalFiles || 1;
          const statusText = progressInfo.status || 'Processing...';
          const currentFilename = progressInfo.current_filename || '';
          
          setCurrentFile(current);
          setTotalFiles(total);
          setProcessingStatus(currentFilename ? `${statusText}` : statusText);
          
          // Calculate progress percentage
          const progressPercent = total > 0 ? Math.min(95, (current / total) * 100) : 20;
          setProcessingProgress(progressPercent);
          
          // Check if complete
          if (progressData.complete) {
            clearInterval(pollInterval);
            
            setProcessingProgress(100);
            
            // Show detailed summary
            const summary = progressData.summary || {};
            const processed = progressData.cv_count || summary.processed || current;
            const total: number = summary.total_files || totalFiles;
            const failed = summary.failed || (progressData.errors?.length || 0);
            
            if (failed > 0) {
              setProcessingStatus(`⚠️ Completed: ${processed}/${total} CV(s) processed. ${failed} failed.`);
              setError(`Some CVs failed: ${progressData.errors?.join(', ') || 'Unknown error'}`);
            } else {
              setProcessingStatus(`✅ Completed: ${processed} CV(s) processed successfully`);
            }
            
            // Navigate to step 6 after short delay (only if at least one CV was processed)
            if (processed > 0) {
              setTimeout(() => {
                navigate('/interviewer/step6');
              }, 3000); // Give user time to see the summary
            } else {
              // No CVs processed - don't navigate, let user see the error
              setProcessingStatus(`❌ Upload failed: No CVs could be processed`);
              setIsProcessing(false);
              setLoading(false);
            }
          } else if (progressData.status === 'failed') {
            clearInterval(pollInterval);
            
            setProcessingStatus(`❌ Upload failed: ${progressInfo.status || 'Unknown error'}`);
            setProcessingProgress(0);
            setError(progressData.errors?.join(', ') || 'Upload failed');
            setIsProcessing(false);
            setLoading(false);
          }
        } catch (pollError: any) {
          // Don't log timeout errors as they're expected during long operations
          const isTimeout = pollError.code === 'ECONNABORTED' || pollError.message?.includes('timeout');
          if (!isTimeout) {
            console.error('Error polling upload progress:', pollError);
          }
          
          // Continue polling unless it's a 404 (session expired)
          if (pollError.response?.status === 404) {
            clearInterval(pollInterval);
            
            sessionStorage.removeItem('interviewer_session_id');
            setError('Session expired. Please restart from step 1.');
            setIsProcessing(false);
            setLoading(false);
          }
        }
      }, 3000); // Poll every 3 seconds
      
      // Store interval ID for cleanup on unmount
      (window as any).__step5PollInterval = pollInterval;
      
    } catch (error: any) {
      console.error('Error in step 5:', error);
      setError(error.response?.data?.detail || 'An error occurred starting CV upload.');
      setUploadProgress('');
      setIsProcessing(false);
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
        
        {isProcessing ? (
          <AILoadingOverlay 
            isVisible={isProcessing}
            message={`${processingStatus} (${currentFile}/${totalFiles})`}
            estimatedSeconds={totalFiles * 15}
          />
        ) : (
          <AILoadingOverlay 
            isVisible={loading}
            message={uploadProgress || `Preparing to upload ${files.length} CV(s)...`}
            estimatedSeconds={files.length * 15}
          />
        )}
        
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

