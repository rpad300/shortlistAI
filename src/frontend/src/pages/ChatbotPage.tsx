/**
 * Chatbot CV Preparation Page
 * 
 * Main page for conversational chatbot flow that guides candidates
 * through CV preparation for specific job opportunities.
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Layout from '@components/Layout';
import ChatInterface from '@components/ChatInterface';
import Checkbox from '@components/Checkbox';
import Button from '@components/Button';
import { chatbotAPI, profilesAPI } from '@services/api';
import './ChatbotPage.css';

// Simple logger for development
const logger = {
  info: (message: string) => console.log(`[ChatbotPage] ${message}`),
  error: (message: string) => console.error(`[ChatbotPage] ${message}`),
  warn: (message: string) => console.warn(`[ChatbotPage] ${message}`)
};

interface Message {
  id: string;
  role: 'user' | 'bot' | 'system';
  content: string;
  message_type?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

const ChatbotPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [riskPanelOpen, setRiskPanelOpen] = useState(false);
  const [companyRisk, setCompanyRisk] = useState<any | null>(null);
  const [candidateRisk, setCandidateRisk] = useState<any | null>(null);
  const [riskLoading, setRiskLoading] = useState(false);
  const [_companyProfileId, setCompanyProfileId] = useState<string | null>(null);
  const [companyPositions, setCompanyPositions] = useState<any[]>([]);
  const [selectedCompanyRedFlags, setSelectedCompanyRedFlags] = useState<Record<number, boolean>>({});
  const [selectedCandidateRedFlags, setSelectedCandidateRedFlags] = useState<Record<number, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [consentStep, setConsentStep] = useState(true);
  const [recoveryStep, setRecoveryStep] = useState(false);
  const [recoverySessionId, setRecoverySessionId] = useState('');
  
  // Consent state
  const [consents, setConsents] = useState({
    consent_read_cv: false,
    consent_read_job_opportunity: false,
    consent_analyze_links: false,
    consent_store_data: false
  });

  // Don't auto-load session - user must explicitly start a new session
  // This ensures each user starts fresh and sessions are properly isolated

  const handleRecoverSession = async () => {
    if (!recoverySessionId.trim()) {
      setError(t('chatbot.session_id_required', 'Please enter a session ID to recover.'));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await chatbotAPI.recoverSession(recoverySessionId.trim());
      
      const { session: sessionData, messages: sessionMessages } = response.data;
      
      if (!sessionData) {
        throw new Error('Session not found');
      }

      // Check if session is active (not completed or abandoned)
      if (sessionData.status === 'completed' || sessionData.status === 'abandoned') {
        setError(t('chatbot.session_inactive', 'This session has been completed or abandoned. Please start a new session.'));
        return;
      }

      // Store session ID
      localStorage.setItem('chatbot_session_id', sessionData.id);
      
      // Set session state
      setSessionId(sessionData.id);
      setConsentStep(false);
      setRecoveryStep(false);
      
      // Load messages from recovered session
      const uniqueMessages = (sessionMessages || []).filter((msg: Message, index: number, self: Message[]) =>
        index === self.findIndex((m: Message) => m.id === msg.id)
      );
      
      setMessages(uniqueMessages);

      logger.info(`Recovered chatbot session: ${sessionData.id}`);

    } catch (err: any) {
      console.error('Error recovering session:', err);
      setError(
        err.response?.data?.detail ||
        t('chatbot.recovery_error', 'Failed to recover session. Please check the session ID and try again.')
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStartNewSession = async () => {
    // Validate all consents are given
    if (!Object.values(consents).every(Boolean)) {
      setError(t('chatbot.all_consents_required', 'All consents must be given to proceed.'));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // IMPORTANT: Clear any existing session before starting a new one
      // This ensures each new session is isolated and starts fresh
      const oldSessionId = localStorage.getItem('chatbot_session_id');
      if (oldSessionId) {
        localStorage.removeItem('chatbot_session_id');
        logger.info(`Cleared previous session: ${oldSessionId}`);
      }

      // Clear messages to start fresh
      setMessages([]);
      setSessionId(null);

      // Create new session
      const language = i18n.language || localStorage.getItem('language') || 'en';
      const response = await chatbotAPI.welcome({
        language,
        ...consents
      });

      const { session_id } = response.data;
      
      // Store NEW session ID
      localStorage.setItem('chatbot_session_id', session_id);
      
      // Set session state
      setSessionId(session_id);
      setConsentStep(false);
      
      // Load messages from the new session (including welcome message)
      const messagesResponse = await chatbotAPI.getMessages(session_id);
      const sessionMessages = messagesResponse.data.messages || [];
      
      // Filter out duplicates and set messages
      const uniqueMessages = sessionMessages.filter((msg: Message, index: number, self: Message[]) =>
        index === self.findIndex((m: Message) => m.id === msg.id)
      );
      
      setMessages(uniqueMessages);

      logger.info(`Started new chatbot session: ${session_id}`);

    } catch (err: any) {
      console.error('Error starting new session:', err);
      setError(
        err.response?.data?.detail ||
        t('chatbot.start_error', 'Failed to start chatbot session. Please try again.')
      );
      // Clear session ID on error
      setSessionId(null);
      localStorage.removeItem('chatbot_session_id');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!sessionId || !message.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Add user message immediately for better UX
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: message,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Show "thinking" indicator
      const thinkingMessage: Message = {
        id: `thinking-${Date.now()}`,
        role: 'bot',
        content: t('chatbot.thinking', '🤔 Thinking... This may take a moment while I process your request.'),
        message_type: 'system',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, thinkingMessage]);

      await chatbotAPI.sendMessage(sessionId, message);
      
      // Reload all messages to avoid duplicates and get proper IDs
      const messagesResponse = await chatbotAPI.getMessages(sessionId);
      const updatedMessages = messagesResponse.data.messages || [];
      
      // Filter out duplicates and temporary messages
      const uniqueMessages = updatedMessages.filter((msg: Message, index: number, self: Message[]) =>
        index === self.findIndex((m: Message) => m.id === msg.id)
      ).filter((msg: Message) => !msg.id.startsWith('temp-') && !msg.id.startsWith('thinking-'));
      
      setMessages(uniqueMessages);
    } catch (err: any) {
      // Remove temporary messages on error
      setMessages(prev => prev.filter(msg => 
        !msg.id.startsWith('temp-') && !msg.id.startsWith('thinking-')
      ));
      
      setError(
        err.response?.data?.detail ||
        t('chatbot.message_error', 'Failed to send message. Please try again.')
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);

    try {
      // Add user message for file upload
      const userMessage: Message = {
        id: `temp-upload-${Date.now()}`,
        role: 'user',
        content: `📎 Uploaded file: ${file.name}`,
        message_type: 'file_upload',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Show processing indicator
      const processingMessage: Message = {
        id: `processing-${Date.now()}`,
        role: 'bot',
        content: t('chatbot.processing_cv', '📄 Processing your CV... This may take 1-2 minutes while I extract and analyze the content.'),
        message_type: 'system',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, processingMessage]);

      await chatbotAPI.uploadCV(sessionId, file);
      
      // Reload messages to get bot response
      const messagesResponse = await chatbotAPI.getMessages(sessionId);
      const updatedMessages = messagesResponse.data.messages || [];
      
      // Filter out duplicates and temporary messages
      const uniqueMessages = updatedMessages.filter((msg: Message, index: number, self: Message[]) =>
        index === self.findIndex((m: Message) => m.id === msg.id)
      ).filter((msg: Message) => !msg.id.startsWith('temp-') && !msg.id.startsWith('processing-'));
      
      setMessages(uniqueMessages);
    } catch (err: any) {
      // Remove temporary messages on error
      setMessages(prev => prev.filter(msg => 
        !msg.id.startsWith('temp-') && !msg.id.startsWith('processing-')
      ));
      
      setError(
        err.response?.data?.detail ||
        t('chatbot.upload_error', 'Failed to upload file. Please try again.')
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReviewRisk = async () => {
    try {
      setRiskLoading(true);
      setRiskPanelOpen(true);
      if (!sessionId) return;
      const sessRes = await chatbotAPI.getSession(sessionId);
      const session = sessRes.data?.session || {};
      const profileData = session.profile_data || {};
      const jobData = session.job_opportunity_data || {};
      const candidateName: string | undefined = profileData.name;
      const companyName: string | undefined = jobData.company || jobData.company_name;

      if (candidateName) {
        const candRes = await profilesAPI.listCandidates({
          candidate_name: candidateName,
          min_risk_level: 'low',
          limit: 1,
        });
        const candItem = candRes.data?.items?.[0];
        const candRisk = candItem?.social_media_risk_analysis || null;
        setCandidateRisk(candRisk);
        // Initialize selected red flags (all on)
        if (candRisk && Array.isArray(candRisk.red_flags)) {
          const rfState: Record<number, boolean> = {};
          candRisk.red_flags.forEach((_: any, idx: number) => (rfState[idx] = true));
          setSelectedCandidateRedFlags(rfState);
        } else {
          setSelectedCandidateRedFlags({});
        }
      } else {
        setCandidateRisk(null);
        setSelectedCandidateRedFlags({});
      }

      if (companyName) {
        const compRes = await profilesAPI.listCompanies({
          name: companyName,
          min_risk_level: 'low',
          limit: 1,
        });
        const compItem = compRes.data?.items?.[0];
        const risk = compItem?.reputation_risk_analysis || null;
        setCompanyRisk(risk);
        if (risk && Array.isArray(risk.red_flags)) {
          const rfState: Record<number, boolean> = {};
          risk.red_flags.forEach((_: any, idx: number) => (rfState[idx] = true));
          setSelectedCompanyRedFlags(rfState);
        } else {
          setSelectedCompanyRedFlags({});
        }
        if (compItem?.id) {
          setCompanyProfileId(compItem.id);
          // Load positions for this company profile
          try {
            const posRes = await profilesAPI.listCompanyPositions(compItem.id, 'active', 20);
            setCompanyPositions(Array.isArray(posRes.data?.items) ? posRes.data.items : []);
          } catch (e) {
            console.error('Failed to load company positions', e);
            setCompanyPositions([]);
          }
        } else {
          setCompanyProfileId(null);
          setCompanyPositions([]);
        }
      } else {
        setCompanyRisk(null);
        setSelectedCompanyRedFlags({});
        setCompanyProfileId(null);
        setCompanyPositions([]);
      }
    } catch (e) {
      console.error('Risk review error', e);
    } finally {
      setRiskLoading(false);
    }
  };

  const handleAdjustCVConsideringRisk = async () => {
    // Build instruction based on language, company, positions and selected red flags
    const lang = i18n.language || 'en';
    const selectedCompanyRF =
      companyRisk && Array.isArray(companyRisk.red_flags)
        ? companyRisk.red_flags.filter((_: any, idx: number) => selectedCompanyRedFlags[idx])
        : [];
    const selectedCandidateRF =
      candidateRisk && Array.isArray(candidateRisk.red_flags)
        ? candidateRisk.red_flags.filter((_: any, idx: number) => selectedCandidateRedFlags[idx])
        : [];

    const companyRFText =
      selectedCompanyRF.length > 0
        ? selectedCompanyRF.map((rf: any) => `- ${rf?.description || JSON.stringify(rf)}`).join('\n')
        : t('chatbot.no_company_red_flags_selected', 'No company red flags selected.');

    const candidateRFText =
      selectedCandidateRF.length > 0
        ? selectedCandidateRF.map((rf: any) => `- ${rf?.description || JSON.stringify(rf)}`).join('\n')
        : t('chatbot.no_candidate_red_flags_selected', 'No candidate red flags selected.');

    const positionsSummary =
      companyPositions && companyPositions.length > 0
        ? companyPositions.slice(0, 3).map((p: any) => `- ${p?.job_title || t('chatbot.unknown_position', 'Unknown Position')}`).join('\n')
        : t('chatbot.no_positions_listed', 'No active positions listed.');

    const header = t('chatbot.adjust_cv_header', 'Adjust CV considering risk (language: {{lang}})', { lng: lang, lang });
    const guideline = t(
      'chatbot.adjust_cv_guideline',
      'Optimize my CV considering the selected risk factors, reinforcing professionalism and alignment with company culture. Provide a diff of changes and a short rationale per section.'
    );

    const instruction = `${header}

Company risk factors (selected):
${companyRFText}

Candidate risk factors (selected):
${candidateRFText}

Relevant company positions:
${positionsSummary}

${guideline}`;

    await handleSendMessage(instruction);
  };

  const handleGenerateTailoredComms = async () => {
    const lang = i18n.language || 'en';
    
    // Build company selected red flags text from state
    const companySelectedText = Array.isArray(companyRisk?.red_flags)
      ? companyRisk.red_flags
          .map((rf: any, idx: number) => ({ rf, idx }))
          .filter(({ idx }: any) => selectedCompanyRedFlags[idx] === true)
          .map(({ rf }: any) => `- ${rf?.description || JSON.stringify(rf)}`)
          .join('\n')
      : t('chatbot.no_company_red_flags_selected', 'No company red flags selected.');

    // Build candidate selected red flags text from state
    const candidateSelectedText = Array.isArray(candidateRisk?.red_flags)
      ? candidateRisk.red_flags
          .map((rf: any, idx: number) => ({ rf, idx }))
          .filter(({ idx }: any) => selectedCandidateRedFlags[idx] === true)
          .map(({ rf }: any) => `- ${rf?.description || JSON.stringify(rf)}`)
          .join('\n')
      : t('chatbot.no_candidate_red_flags_selected', 'No candidate red flags selected.');

    // Build positions text
    const positionsText = companyPositions.length > 0
      ? companyPositions.slice(0, 5).map((p: any) => `- ${p?.job_title || t('chatbot.unknown_position', 'Unknown Position')}`).join('\n')
      : t('chatbot.no_positions_listed', 'No active positions listed.');

    const header = t('chatbot.generate_comms_header', 'Generate tailored messages (language: {{lang}})', { lang });
    const channels = t('chatbot.generate_comms_channels', 'Generate risk-aware messages for: email, LinkedIn, and application portal notes.');
    const guideline = t('chatbot.generate_comms_guideline', 'Use the selected risk factors to tailor the tone and content, ensuring professionalism while addressing any concerns proactively.');

    const instruction = `${header}
${channels}

${t('chatbot.company_risk', 'Company risk factors (selected)')}:
${companySelectedText}

${t('chatbot.candidate_risk', 'Candidate risk factors (selected)')}:
${candidateSelectedText}

${t('chatbot.company_positions', 'Relevant company positions')}:
${positionsText}

${guideline}`;

    await handleSendMessage(instruction);
  };

  if (consentStep) {
    return (
      <Layout>
        <div className="chatbot-consent-container">
          <div className="chatbot-consent-content">
            <h1>{t('chatbot.title', 'CV Preparation Chatbot')}</h1>
            <p className="chatbot-consent-description">
              {t('chatbot.description', 
                'I\'m your AI assistant for CV preparation. I\'ll guide you through optimizing your CV for a specific job opportunity. To get started, I need your consent to:')}
            </p>

            <div className="chatbot-consent-list">
              <Checkbox
                label={t('chatbot.consent_read_cv', 'Read and analyze your CV')}
                checked={consents.consent_read_cv}
                onChange={(checked) => setConsents(prev => ({ ...prev, consent_read_cv: checked }))}
              />
              
              <Checkbox
                label={t('chatbot.consent_read_job', 'Read and analyze the job opportunity')}
                checked={consents.consent_read_job_opportunity}
                onChange={(checked) => setConsents(prev => ({ ...prev, consent_read_job_opportunity: checked }))}
              />
              
              <Checkbox
                label={t('chatbot.consent_analyze_links', 'Analyze public links (LinkedIn, GitHub, portfolio)')}
                checked={consents.consent_analyze_links}
                onChange={(checked) => setConsents(prev => ({ ...prev, consent_analyze_links: checked }))}
              />
              
              <Checkbox
                label={t('chatbot.consent_store_data', 'Store your data for this session')}
                checked={consents.consent_store_data}
                onChange={(checked) => setConsents(prev => ({ ...prev, consent_store_data: checked }))}
              />
            </div>

            {error && (
              <div className="chatbot-error">
                {error}
              </div>
            )}

            <Button
              onClick={handleStartNewSession}
              disabled={loading || !Object.values(consents).every(Boolean)}
              className="chatbot-start-button"
            >
              {loading ? t('chatbot.starting', 'Starting...') : t('chatbot.start', 'Start New Chat Session')}
            </Button>

            <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid #ddd', textAlign: 'center' }}>
              <button
                onClick={() => setRecoveryStep(true)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#007bff',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  fontSize: '0.9rem'
                }}
              >
                {t('chatbot.recover_session', 'Recover existing session')}
              </button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (recoveryStep) {
    return (
      <Layout>
        <div className="chatbot-consent-container">
          <div className="chatbot-consent-content">
            <h1>{t('chatbot.recover_session_title', 'Recover Session')}</h1>
            <p className="chatbot-consent-description">
              {t('chatbot.recover_session_description', 
                'Enter your session ID to recover and continue your previous session. You can find your session ID in the chat history.')}
            </p>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                {t('chatbot.session_id', 'Session ID')}
              </label>
              <input
                type="text"
                value={recoverySessionId}
                onChange={(e) => setRecoverySessionId(e.target.value)}
                placeholder={t('chatbot.session_id_placeholder', 'Enter your session ID here...')}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '1rem'
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && recoverySessionId.trim()) {
                    handleRecoverSession();
                  }
                }}
              />
            </div>

            {error && (
              <div className="chatbot-error">
                {error}
              </div>
            )}

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <Button
                onClick={handleRecoverSession}
                disabled={loading || !recoverySessionId.trim()}
                className="chatbot-start-button"
              >
                {loading ? t('chatbot.recovering', 'Recovering...') : t('chatbot.recover', 'Recover Session')}
              </Button>
              <Button
                onClick={() => {
                  setRecoveryStep(false);
                  setRecoverySessionId('');
                  setError(null);
                }}
                disabled={loading}
                style={{
                  background: '#6c757d',
                  border: 'none',
                  color: 'white',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '1rem'
                }}
              >
                {t('chatbot.cancel', 'Cancel')}
              </Button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const handleStartNewSessionFromChat = async () => {
    // Clear current session and return to consent step
    setSessionId(null);
    setMessages([]);
    setConsentStep(true);
    setError(null);
    localStorage.removeItem('chatbot_session_id');
    logger.info('Cleared session and returned to consent step');
  };

  return (
    <Layout>
      <div className="chatbot-page">
        <div className="chatbot-header">
          <div className="chatbot-header-content">
            <div>
              <h1>{t('chatbot.title', 'CV Preparation Chatbot')}</h1>
              <p className="chatbot-subtitle">
                {t('chatbot.subtitle', 'I\'ll help you optimize your CV for this job opportunity.')}
              </p>
            </div>
            <button 
              onClick={handleStartNewSessionFromChat}
              className="chatbot-new-session-button"
              title={t('chatbot.start_new_session', 'Start New Session')}
            >
              {t('chatbot.new_session', 'New Session')}
            </button>
          </div>
        </div>

        {error && (
          <div className="chatbot-error-banner">
            {error}
            <button onClick={() => setError(null)} className="chatbot-error-close">×</button>
          </div>
        )}

        <div className="chatbot-content">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div />
            {sessionId && (
              <button
                onClick={handleReviewRisk}
                className="chatbot-new-session-button"
                title={t('chatbot.review_risk', 'Review Risk (Company & Candidate)')}
                disabled={riskLoading}
              >
                {riskLoading ? t('chatbot.reviewing_risk', 'Reviewing Risk...') : t('chatbot.review_risk', 'Review Risk')}
              </button>
            )}
          </div>

          <ChatInterface
            sessionId={sessionId}
            messages={messages}
            onSendMessage={handleSendMessage}
            onFileUpload={handleFileUpload}
            loading={loading}
            disabled={!sessionId}
          />

          {riskPanelOpen && (
            <div className="risk-panel" style={{ marginTop: '1rem', border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem' }}>
              <h3 style={{ marginTop: 0 }}>{t('chatbot.risk_review', 'Risk Review')}</h3>

              <div className="risk-section" style={{ marginBottom: '1rem' }}>
                <h4 style={{ margin: '0 0 0.5rem' }}>{t('chatbot.company_risk', 'Company Risk')}</h4>
                {!companyRisk && <p style={{ margin: 0 }}>{t('chatbot.no_company_risk_data', 'No company risk data available yet.')}</p>}
                {companyRisk && (
                  <div className="risk-card" style={{ background: '#fafafa', border: '1px solid #eee', borderRadius: 6, padding: '0.75rem' }}>
                    <p style={{ marginTop: 0 }}>
                      <strong>{t('chatbot.risk_level', 'Risk Level')}:</strong> {companyRisk.risk_level || 'n/a'} |{' '}
                      <strong>{t('chatbot.score', 'Score')}:</strong> {companyRisk.overall_risk_score ?? 'n/a'}
                    </p>
                    {Array.isArray(companyRisk.red_flags) && companyRisk.red_flags.length > 0 && (
                      <>
                        <strong>{t('chatbot.red_flags', 'Red Flags')}:</strong>
                        <ul style={{ marginTop: '0.5rem' }}>
                          {companyRisk.red_flags.map((rf: any, idx: number) => (
                            <li key={`crf-${idx}`}>
                              <label style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                                <input
                                  type="checkbox"
                                  checked={!!selectedCompanyRedFlags[idx]}
                                  onChange={(e) => {
                                    setSelectedCompanyRedFlags((prev) => ({
                                      ...prev,
                                      [idx]: e.target.checked,
                                    }));
                                  }}
                                />
                                <span>{rf?.description || JSON.stringify(rf)}</span>
                              </label>
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                    {companyPositions.length > 0 && (
                      <>
                        <strong style={{ display: 'block', marginTop: '0.5rem' }}>
                          {t('chatbot.company_positions', 'Active Positions')}
                        </strong>
                        <ul style={{ marginTop: '0.5rem' }}>
                          {companyPositions.slice(0, 8).map((p: any, idx: number) => (
                            <li key={`pos-${idx}`}>
                              {p?.job_title || t('chatbot.unknown_position', 'Unknown Position')}
                              {p?.job_details?.location?.city ? ` · ${p.job_details.location.city}` : ''}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                )}
              </div>

              <div className="risk-section">
                <h4 style={{ margin: '0 0 0.5rem' }}>{t('chatbot.candidate_risk', 'Candidate Risk')}</h4>
                {!candidateRisk && <p style={{ margin: 0 }}>{t('chatbot.no_candidate_risk_data', 'No candidate risk data available yet.')}</p>}
                {candidateRisk && (
                  <div className="risk-card" style={{ background: '#fafafa', border: '1px solid #eee', borderRadius: 6, padding: '0.75rem' }}>
                    <p style={{ marginTop: 0 }}>
                      <strong>{t('chatbot.risk_level', 'Risk Level')}:</strong> {candidateRisk.risk_level || 'n/a'} |{' '}
                      <strong>{t('chatbot.score', 'Score')}:</strong> {candidateRisk.overall_risk_score ?? 'n/a'}
                    </p>
                    {Array.isArray(candidateRisk.red_flags) && candidateRisk.red_flags.length > 0 && (
                      <>
                        <strong>{t('chatbot.red_flags', 'Red Flags')}:</strong>
                        <ul style={{ marginTop: '0.5rem' }}>
                          {candidateRisk.red_flags.map((rf: any, idx: number) => (
                            <li key={`prf-${idx}`}>
                              <label style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                                <input
                                  type="checkbox"
                                  checked={!!selectedCandidateRedFlags[idx]}
                                  onChange={(e) => {
                                    setSelectedCandidateRedFlags((prev) => ({
                                      ...prev,
                                      [idx]: e.target.checked,
                                    }));
                                  }}
                                />
                                <span>{rf?.description || JSON.stringify(rf)}</span>
                              </label>
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                )}
              </div>

              <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                <button
                  onClick={handleGenerateTailoredComms}
                  className="chatbot-new-session-button"
                  title={t('chatbot.generate_comms', 'Generate tailored messages')}
                >
                  {t('chatbot.generate_comms', 'Generate tailored messages')}
                </button>
                <button
                  onClick={handleAdjustCVConsideringRisk}
                  className="chatbot-new-session-button"
                  title={t('chatbot.adjust_cv', 'Adjust CV considering risk')}
                >
                  {t('chatbot.adjust_cv', 'Adjust CV considering risk')}
                </button>
                <button
                  onClick={() => setRiskPanelOpen(false)}
                  className="chatbot-new-session-button"
                  title={t('chatbot.close', 'Close')}
                  style={{ backgroundColor: '#6b7280' }}
                >
                  {t('chatbot.close', 'Close')}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default ChatbotPage;

