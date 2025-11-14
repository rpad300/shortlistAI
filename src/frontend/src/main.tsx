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
  // More aggressive service worker cleanup for development
  const cleanupServiceWorkers = async () => {
    try {
      // Get all registrations
      const registrations = await navigator.serviceWorker.getRegistrations();
      
      // Unregister all service workers
      const unregisterPromises = registrations.map(async (registration) => {
        try {
          // Try to update first to get the latest version
          await registration.update();
          
          // Unregister
          const success = await registration.unregister();
          if (success) {
            console.log('[Dev] Unregistered service worker:', registration.scope);
          } else {
            console.warn('[Dev] Failed to unregister service worker:', registration.scope);
          }
        } catch (error) {
          console.error('[Dev] Error unregistering service worker:', error);
        }
      });
      
      await Promise.all(unregisterPromises);
      
      // If there's still a controller, try to unregister it
      if (navigator.serviceWorker.controller) {
        try {
          // Post message to skip waiting
          navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
          
          // Try to unregister by scope
          const controllerScope = navigator.serviceWorker.controller.scriptURL;
          const unregisterResult = await navigator.serviceWorker.unregister(controllerScope);
          if (unregisterResult) {
            console.log('[Dev] Unregistered controller service worker');
          }
        } catch (error) {
          console.warn('[Dev] Could not unregister controller:', error);
        }
      }
      
      // Force reload if service workers were found and unregistered
      if (registrations.length > 0) {
        console.log('[Dev] Service workers cleaned up. Reloading page...');
        // Small delay to ensure cleanup is complete
        setTimeout(() => {
          window.location.reload();
        }, 500);
      }
    } catch (error) {
      console.error('[Dev] Error during service worker cleanup:', error);
    }
  };
  
  // Run cleanup immediately
  cleanupServiceWorkers();
  
  // Also listen for service worker updates and unregister them
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      console.log('[Dev] Service worker controller changed, cleaning up...');
      cleanupServiceWorkers();
    });
  }
}

// In production, handle service worker updates to ensure users get latest version
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  // Listen for service worker updates
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    // When service worker changes, reload to get latest version
    console.log('[PWA] Service worker updated, reloading to get latest version...');
    window.location.reload();
  });
  
  // Check for updates periodically (every 5 minutes)
  setInterval(() => {
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      registrations.forEach((registration) => {
        registration.update().catch((error) => {
          console.warn('[PWA] Error checking for service worker updates:', error);
        });
      });
    });
  }, 5 * 60 * 1000); // 5 minutes
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

