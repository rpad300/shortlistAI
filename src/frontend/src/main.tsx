/**
 * Main entry point for the CV Analysis Platform frontend.
 * 
 * Initializes React app with:
 * - React Router for navigation
 * - i18n for multi-language support
 * - PWA service worker registration
 * - Global theme provider (light/dark mode)
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import App from './App';
import './i18n/config'; // Initialize i18n
import './index.css';

// Note: Service worker is automatically registered by VitePWA plugin
// No manual registration needed - VitePWA handles it automatically

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </HelmetProvider>
  </React.StrictMode>
);

