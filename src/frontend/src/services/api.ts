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
  timeout: 30000, // Default timeout (can be overridden per endpoint)
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
    timeout: 30000 // 30s: just to start processing, actual processing is async
  }),
  step4SuggestionsProgress: (sessionId: string) => {
    return api.get(`/interviewer/step4/suggestions/progress/${sessionId}`, {
      timeout: 10000 // Polling endpoint - allow time for network delays
    });
  },
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
    timeout: 30000 // 30s: just to start processing, actual processing is async
  }),
  step2Progress: (sessionId: string) => {
    return api.get(`/candidate/step2/progress/${sessionId}`, {
      timeout: 10000 // Polling endpoint - allow time for network delays
    });
  },
  step3: (data: FormData) => api.post('/candidate/step3', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000 // 60s: file upload only, no AI processing
  }),
  step4: (sessionId: string) => api.post(`/candidate/step4?session_id=${sessionId}`, null, {
    timeout: 30000 // 30s: just to start processing, actual processing is async
  }),
  step4Progress: (sessionId: string) => {
    return api.get(`/candidate/step4/progress/${sessionId}`, {
      timeout: 10000 // Polling endpoint - allow time for network delays
    });
  },
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
 * API endpoints for Chatbot CV Preparation flow.
 * 
 * Timeouts are synchronized with backend processing times:
 * - Conversational messages: 180s (AI responses can take 60-120s, +50% margin)
 * - File uploads: 180s (CV upload + PDF.co processing + AI extraction can take 60-120s)
 * - Profile updates: 30s (just DB operations, no AI)
 * - Session/messages retrieval: 30s (just DB queries)
 */
export const chatbotAPI = {
  welcome: (data: {
    language: string;
    consent_read_cv: boolean;
    consent_read_job_opportunity: boolean;
    consent_analyze_links: boolean;
    consent_store_data: boolean;
  }) => api.post('/chatbot/welcome', data, {
    timeout: 30000 // Just DB operations, no AI
  }),
  sendMessage: (sessionId: string, message: string, messageType: string = 'text') =>
    api.post('/chatbot/message', {
      session_id: sessionId,
      message,
      message_type: messageType
    }, {
      timeout: 180000 // 180s: AI responses can take 60-120s, allow extra margin
    }),
  updateProfile: (sessionId: string, data: {
    name: string;
    email: string;
    phone?: string;
    location?: string;
    links?: Record<string, string>;
  }) => api.post('/chatbot/profile', {
    session_id: sessionId,
    ...data
  }, {
    timeout: 30000 // Just DB operations, no AI
  }),
  uploadCV: (sessionId: string, file: File) => {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', file);
    return api.post('/chatbot/cv/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000 // 180s: File upload + PDF.co processing + AI extraction can take 60-120s
    });
  },
  getSession: (sessionId: string) =>
    api.get(`/chatbot/session/${sessionId}`, {
      timeout: 30000 // Just DB query
    }),
  getMessages: (sessionId: string, limit?: number) => {
    const params = limit ? `?limit=${limit}` : '';
    return api.get(`/chatbot/session/${sessionId}/messages${params}`, {
      timeout: 30000 // Just DB query
    });
  },
  recoverSession: (sessionId: string) =>
    api.get(`/chatbot/session/${sessionId}`, {
      timeout: 30000 // Just DB query
    }),
};

/**
 * API endpoints for Profiles (company & candidate) with risk filters.
 */
export const profilesAPI = {
  listCompanies: (params: {
    name?: string;
    industry?: string;
    min_risk_level?: "low" | "medium" | "high" | "critical";
    limit?: number;
  }) =>
    api.get(`/profiles/company`, {
      params,
      timeout: 20000,
    }),
  getCompany: (profileId: string) =>
    api.get(`/profiles/company/${profileId}`, { timeout: 20000 }),
  listCompanyPositions: (profileId: string, status?: string, limit: number = 50) =>
    api.get(`/profiles/company/${profileId}/positions`, {
      params: { status, limit },
      timeout: 20000,
    }),
  listCandidates: (params: {
    candidate_name?: string;
    min_risk_level?: "low" | "medium" | "high" | "critical";
    limit?: number;
  }) =>
    api.get(`/profiles/candidate`, {
      params,
      timeout: 20000,
    }),
  getCandidate: (profileId: string) =>
    api.get(`/profiles/candidate/${profileId}`, { timeout: 20000 }),
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

