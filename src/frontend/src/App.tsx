/**
 * Main App component.
 * 
 * Sets up routing, theme management, and global layout structure.
 */

import { Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import InterviewerStep1 from '@pages/InterviewerStep1';
import InterviewerStep2 from '@pages/InterviewerStep2';
import InterviewerStep3 from '@pages/InterviewerStep3';
import InterviewerStep4 from '@pages/InterviewerStep4';
import InterviewerStep5 from '@pages/InterviewerStep5';
import CandidateStep1 from '@pages/CandidateStep1';
import LegalTerms from '@pages/LegalTerms';
import LegalPrivacy from '@pages/LegalPrivacy';
import './App.css';

function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/interviewer/step1" element={<InterviewerStep1 />} />
        <Route path="/interviewer/step2" element={<InterviewerStep2 />} />
        <Route path="/interviewer/step3" element={<InterviewerStep3 />} />
        <Route path="/interviewer/step4" element={<InterviewerStep4 />} />
        <Route path="/interviewer/step5" element={<InterviewerStep5 />} />
        <Route path="/interviewer/step6" element={<PlaceholderPage step="6 - Running AI Analysis..." flow="interviewer" />} />
        <Route path="/interviewer/step7" element={<PlaceholderPage step="7 - Results" flow="interviewer" />} />
        <Route path="/interviewer/step8" element={<PlaceholderPage step="8 - Email & Report" flow="interviewer" />} />
        <Route path="/candidate/step1" element={<CandidateStep1 />} />
        <Route path="/candidate/step2" element={<PlaceholderPage step="2" flow="candidate" />} />
        <Route path="/candidate/step3" element={<PlaceholderPage step="3" flow="candidate" />} />
        <Route path="/candidate/step4" element={<PlaceholderPage step="4" flow="candidate" />} />
        <Route path="/candidate/step5" element={<PlaceholderPage step="5" flow="candidate" />} />
        <Route path="/candidate/step6" element={<PlaceholderPage step="6" flow="candidate" />} />
        <Route path="/legal/terms" element={<LegalTerms />} />
        <Route path="/legal/privacy" element={<LegalPrivacy />} />
        <Route path="/admin/login" element={<PlaceholderPage step="Admin Login" flow="admin" />} />
      </Routes>
    </div>
  );
}

// HomePage component
function HomePage() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>{t('welcome')}</h1>
        <p className="home-description">{t('description')}</p>
      </header>
      
      <div className="language-selector">
        <button 
          onClick={() => changeLanguage('en')}
          className={i18n.language === 'en' ? 'active' : ''}
        >
          {t('languages.en')}
        </button>
        <button 
          onClick={() => changeLanguage('pt')}
          className={i18n.language === 'pt' ? 'active' : ''}
        >
          {t('languages.pt')}
        </button>
        <button 
          onClick={() => changeLanguage('fr')}
          className={i18n.language === 'fr' ? 'active' : ''}
        >
          {t('languages.fr')}
        </button>
        <button 
          onClick={() => changeLanguage('es')}
          className={i18n.language === 'es' ? 'active' : ''}
        >
          {t('languages.es')}
        </button>
      </div>

      <div className="flow-cards">
        <Link to="/interviewer/step1" className="flow-card">
          <h2>{t('interviewer_flow')}</h2>
          <p>{t('interviewer.subtitle')}</p>
        </Link>
        
        <Link to="/candidate/step1" className="flow-card">
          <h2>{t('candidate_flow')}</h2>
          <p>{t('candidate.subtitle')}</p>
        </Link>
      </div>
      
      <div className="admin-link">
        <Link to="/admin/login">{t('admin_login')}</Link>
      </div>
    </div>
  );
}

// Placeholder for steps not yet implemented
function PlaceholderPage({ step, flow }: { step: string; flow: string }) {
  const { t } = useTranslation();
  
  return (
    <div className="step-container">
      <div className="step-content">
        <h1>{flow === 'interviewer' ? t('interviewer.title') : t('candidate.title')} - Step {step}</h1>
        <p>This step is under development.</p>
        <p>Session ID: {sessionStorage.getItem(`${flow}_session_id`) || 'Not set'}</p>
        <Link to="/">← Back to Home</Link>
      </div>
    </div>
  );
}

export default App;

