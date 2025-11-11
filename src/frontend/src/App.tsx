/**
 * Main App component.
 * 
 * Sets up routing, theme management, and global layout structure.
 */

import { Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Home from '@pages/Home';
import Features from '@pages/Features';
import About from '@pages/About';
import Pricing from '@pages/Pricing';
import InterviewerStep1 from '@pages/InterviewerStep1';
import InterviewerStep2 from '@pages/InterviewerStep2';
import InterviewerStep3 from '@pages/InterviewerStep3';
import InterviewerStep4 from '@pages/InterviewerStep4';
import InterviewerStep5 from '@pages/InterviewerStep5';
import CandidateStep1 from '@pages/CandidateStep1';
import CandidateStep2 from '@pages/CandidateStep2';
import CandidateStep3 from '@pages/CandidateStep3';
import CandidateStep4 from '@pages/CandidateStep4';
import CandidateStep5 from '@pages/CandidateStep5';
import InterviewerStep6 from '@pages/InterviewerStep6';
import InterviewerStep7 from '@pages/InterviewerStep7';
import AdminLogin from '@pages/AdminLogin';
import LegalTerms from '@pages/LegalTerms';
import LegalPrivacy from '@pages/LegalPrivacy';
import './App.css';

function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/features" element={<Features />} />
        <Route path="/about" element={<About />} />
        <Route path="/how-it-works" element={<About />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/interviewer/step1" element={<InterviewerStep1 />} />
        <Route path="/interviewer/step2" element={<InterviewerStep2 />} />
        <Route path="/interviewer/step3" element={<InterviewerStep3 />} />
        <Route path="/interviewer/step4" element={<InterviewerStep4 />} />
        <Route path="/interviewer/step5" element={<InterviewerStep5 />} />
        <Route path="/interviewer/step6" element={<InterviewerStep6 />} />
        <Route path="/interviewer/step7" element={<InterviewerStep7 />} />
        <Route path="/interviewer/step8" element={<PlaceholderPage step="8 - Email & Report" flow="interviewer" />} />
        <Route path="/candidate/step1" element={<CandidateStep1 />} />
        <Route path="/candidate/step2" element={<CandidateStep2 />} />
        <Route path="/candidate/step3" element={<CandidateStep3 />} />
        <Route path="/candidate/step4" element={<CandidateStep4 />} />
        <Route path="/candidate/step5" element={<CandidateStep5 />} />
        <Route path="/candidate/step6" element={<PlaceholderPage step="6 - Email Sent!" flow="candidate" />} />
        <Route path="/legal/terms" element={<LegalTerms />} />
        <Route path="/legal/privacy" element={<LegalPrivacy />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/dashboard" element={<PlaceholderPage step="Dashboard" flow="admin" />} />
      </Routes>
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

