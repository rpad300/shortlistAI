/**
 * Main App component.
 * 
 * Sets up routing, theme management, and global layout structure.
 */

import { Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

// Pages (TODO: Create these components)
// import HomePage from '@pages/HomePage';
// import InterviewerFlow from '@pages/InterviewerFlow';
// import CandidateFlow from '@pages/CandidateFlow';
// import AdminLogin from '@pages/AdminLogin';
// import AdminDashboard from '@pages/AdminDashboard';

function App() {
  const { t } = useTranslation();

  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/interviewer/*" element={<div>{t('Interviewer Flow - Coming Soon')}</div>} />
        <Route path="/candidate/*" element={<div>{t('Candidate Flow - Coming Soon')}</div>} />
        <Route path="/admin/login" element={<div>{t('Admin Login - Coming Soon')}</div>} />
        <Route path="/admin/*" element={<div>{t('Admin Dashboard - Coming Soon')}</div>} />
      </Routes>
    </div>
  );
}

// Temporary HomePage component
function HomePage() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>{t('welcome')}</h1>
      <p>{t('description')}</p>
      
      <div style={{ marginTop: '2rem' }}>
        <button onClick={() => changeLanguage('en')}>English</button>
        <button onClick={() => changeLanguage('pt')}>Português</button>
        <button onClick={() => changeLanguage('fr')}>Français</button>
        <button onClick={() => changeLanguage('es')}>Español</button>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <a href="/interviewer" style={{ margin: '0 1rem' }}>{t('interviewer_flow')}</a>
        <a href="/candidate" style={{ margin: '0 1rem' }}>{t('candidate_flow')}</a>
        <a href="/admin/login" style={{ margin: '0 1rem' }}>{t('admin_login')}</a>
      </div>
    </div>
  );
}

export default App;

