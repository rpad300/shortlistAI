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
import App from './App';
import './i18n/config'; // Initialize i18n
import './index.css';

// PWA service worker registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then(
      (registration) => {
        console.log('ServiceWorker registration successful:', registration.scope);
      },
      (error) => {
        console.log('ServiceWorker registration failed:', error);
      }
    );
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

