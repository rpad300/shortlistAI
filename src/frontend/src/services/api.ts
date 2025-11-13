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
    if (error.response) {
      console.error('[API] Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('[API] No response received:', error.request);
    } else {
      console.error('[API] Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;

/**
 * API endpoints for Interviewer flow.
 */
export const interviewerAPI = {
  step1: (data: any) => api.post('/interviewer/step1', data),
  step2: (data: FormData) => api.post('/interviewer/step2', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  step3Suggestions: (sessionId: string) => api.get(`/interviewer/step3/suggestions/${sessionId}`, {
    timeout: 60000,
  }),
  step3: (data: any) => api.post('/interviewer/step3', data),
  step4Suggestions: (sessionId: string) => api.get(`/interviewer/step4/suggestions/${sessionId}`, {
    timeout: 60000,
  }),
  step4: (data: any) => api.post('/interviewer/step4', data),
  step5: (data: FormData) => api.post('/interviewer/step5', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  step6: (sessionId: string) => api.post(`/interviewer/step6?session_id=${sessionId}`, null, {
    timeout: 90000,
  }),
  step7: (sessionId: string, reportCode?: string) => {
    const url = reportCode 
      ? `/interviewer/step7/${sessionId}?report_code=${reportCode}`
      : `/interviewer/step7/${sessionId}`;
    return api.get(url);
  },
  sendEmail: (sessionId: string, email: string) => 
    api.post('/interviewer/step8/email', { session_id: sessionId, recipient_email: email }),
  downloadReport: (sessionId: string) => api.get(`/interviewer/step8/report/${sessionId}`, {
    responseType: 'blob'
  }),
};

/**
 * API endpoints for Candidate flow.
 */
export const candidateAPI = {
  step1: (data: any) => api.post('/candidate/step1', data),
  step2: (data: FormData) => api.post('/candidate/step2', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  step3: (data: FormData) => api.post('/candidate/step3', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  step4: (sessionId: string) => api.post(`/candidate/step4?session_id=${sessionId}`),
  step5: (sessionId: string) => api.get(`/candidate/step5/${sessionId}`),
  sendEmail: (sessionId: string, email: string) => 
    api.post('/candidate/step6/email', { session_id: sessionId, recipient_email: email }),
  downloadReport: (sessionId: string) => api.get(`/candidate/step6/report/${sessionId}`, {
    responseType: 'blob'
  }),
};

