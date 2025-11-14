/**
 * API client for backend communication.
 * 
 * Provides centralized HTTP client with error handling and auth.
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Main API client instance.
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for AI operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth
api.interceptors.request.use(
  (config) => {
    // Ensure Authorization header is set from localStorage if available
    const token = localStorage.getItem('admin_token');
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Don't log timeout errors for polling endpoints (they're expected)
    const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout');
    const isPollingEndpoint = error.config?.url?.includes('/progress/');
    
    if (isTimeout && isPollingEndpoint) {
      // Silently handle timeout for polling - it's expected and will retry
      return Promise.reject(error);
    }
    
    if (error.response) {
      console.error('[API] Response error:', error.response.status, error.response.data);
    } else if (error.request && !isTimeout) {
      // Only log "No response received" if it's not a timeout
      console.error('[API] No response received:', error.request);
    } else if (!isTimeout) {
      console.error('[API] Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;

/**
 * API endpoints for Interviewer flow.
 * 
 * Timeouts are synchronized with backend processing times:
 * - Backend AI operations: 60-90s → Frontend: 120-150s (50% margin)
 * - Backend file processing: variable → Frontend: 120s (safe margin)
 * - Background operations: return immediately → Frontend: 30s (just to start)
 * - Polling endpoints: quick checks → Frontend: 8-10s (network delays)
 */
export const interviewerAPI = {
  step1: (data: any) => api.post('/interviewer/step1', data, {
    timeout: 30000 // No AI, just DB operations
  }),
  step2: (data: FormData) => api.post('/interviewer/step2', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000 // 30s: just to start processing, actual processing is async
  }),
  step2Progress: (sessionId: string) => {
    return api.get(`/interviewer/step2/progress/${sessionId}`, {
      timeout: 10000 // Polling endpoint - allow time for network delays
    });
  },
  step3Suggestions: (sessionId: string) => api.get(`/interviewer/step3/suggestions/${sessionId}`, {
    timeout: 30000 // No AI, just returns cached data from session
  }),
  step3: (data: any) => api.post('/interviewer/step3', data, {
    timeout: 30000 // No AI, just stores data
  }),
  step4Suggestions: (sessionId: string) => api.get(`/interviewer/step4/suggestions/${sessionId}`, {
    timeout: 90000 // 90s: backend AI timeout=60s, +50% margin for network/processing
  }),
  step4: (data: any) => api.post('/interviewer/step4', data, {
    timeout: 30000 // No AI, just stores data
  }),
  step5: (data: FormData) => {
    // Upload starts immediately, processing happens in background
    return api.post('/interviewer/step5', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000 // 60s: file upload can be large, but processing is async
    });
  },
  step5Progress: (sessionId: string) => {
    return api.get(`/interviewer/step5/progress/${sessionId}`, {
      timeout: 10000 // Polling endpoint - allow time for network delays
    });
  },
  step6: (sessionId: string) => api.post(`/interviewer/step6?session_id=${sessionId}`, null, {
    timeout: 30000 // Quick response - analysis runs in background (backend timeout=300s per CV)
  }),
  step6Progress: (sessionId: string) => api.get(`/interviewer/step6/progress/${sessionId}`, {
    timeout: 10000 // Polling endpoint - allow time for network delays
  }),
  step7: (sessionId: string, reportCode?: string) => {
    const url = reportCode 
      ? `/interviewer/step7/${sessionId}?report_code=${reportCode}`
      : `/interviewer/step7/${sessionId}`;
    return api.get(url, {
      timeout: 30000 // Just retrieves report data
    });
  },
  sendEmail: (sessionId: string, email: string) => 
    api.post('/interviewer/step8/email', { session_id: sessionId, recipient_email: email }, {
      timeout: 30000
    }),
  downloadReport: (sessionId: string) => api.get(`/interviewer/step8/report/${sessionId}`, {
    responseType: 'blob',
    timeout: 60000 // File download can take time
  }),
};

/**
 * API endpoints for Candidate flow.
 * 
 * Timeouts are synchronized with backend processing times:
 * - Backend AI operations: 60-90s → Frontend: 120-150s (50% margin)
 * - Backend file processing: variable → Frontend: 120s (safe margin)
 */
export const candidateAPI = {
  step1: (data: any) => api.post('/candidate/step1', data, {
    timeout: 30000 // No AI, just DB operations
  }),
  step2: (data: FormData) => api.post('/candidate/step2', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 150000 // 150s: file upload + AI normalization (backend can take 60-90s, +50% margin)
  }),
  step3: (data: FormData) => api.post('/candidate/step3', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000 // 60s: file upload only, no AI processing
  }),
  step4: (sessionId: string) => api.post(`/candidate/step4?session_id=${sessionId}`, null, {
    timeout: 120000 // 120s: backend AI timeout=90s, +33% margin for network/processing
  }),
  step5: (sessionId: string) => api.get(`/candidate/step5/${sessionId}`, {
    timeout: 30000 // Just retrieves analysis results
  }),
  sendEmail: (sessionId: string, email: string) => 
    api.post('/candidate/step6/email', { session_id: sessionId, recipient_email: email }, {
      timeout: 30000
    }),
  downloadReport: (sessionId: string) => api.get(`/candidate/step6/report/${sessionId}`, {
    responseType: 'blob',
    timeout: 60000 // File download can take time
  }),
};

/**
 * API endpoints for Admin.
 */
export const adminAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/admin/login', credentials),
  getMe: () => api.get('/admin/me'),
  getDashboardStats: () => api.get('/admin/dashboard/detailed-stats'),
  listCandidates: (limit = 50, offset = 0) =>
    api.get(`/admin/candidates?limit=${limit}&offset=${offset}`),
  getCandidateDetails: (candidateId: string) =>
    api.get(`/admin/candidates/${candidateId}`),
  downloadCV: (cvId: string) =>
    api.get(`/admin/cvs/${cvId}/download`),
};

