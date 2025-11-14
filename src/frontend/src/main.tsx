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

// In development, unregister any existing service workers to avoid conflicts
if (import.meta.env.DEV && 'serviceWorker' in navigator) {
  // Force unregister all service workers immediately
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    registrations.forEach((registration) => {
      registration.unregister().then((success) => {
        if (success) {
          console.log('[Dev] Unregistered service worker:', registration.scope);
        } else {
          console.warn('[Dev] Failed to unregister service worker:', registration.scope);
        }
      }).catch((error) => {
        console.error('[Dev] Error unregistering service worker:', error);
      });
    });
  }).catch((error) => {
    console.error('[Dev] Error getting service worker registrations:', error);
  });
  
  // Also try to unregister by scope
  if (navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
  }
}

// Note: Service worker is automatically registered by VitePWA plugin in production only
// In development, VitePWA is disabled to avoid conflicts with Vite dev server

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </HelmetProvider>
  </React.StrictMode>
);

