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

// Service Worker cleanup utility - can be called manually via window.cleanupServiceWorkers()
const cleanupServiceWorkers = async () => {
    try {
      // Get all registrations
      const registrations = await navigator.serviceWorker.getRegistrations();
      
      if (registrations.length === 0) {
        return; // No service workers to clean up
      }
      
      console.log(`[SW Cleanup] Found ${registrations.length} service worker(s) to clean up`);
      
      // Unregister all service workers
      const unregisterPromises = registrations.map(async (registration) => {
        try {
          // Send message to unregister
          const activeWorker = registration.active;
          if (activeWorker) {
            try {
              activeWorker.postMessage({ type: 'SKIP_WAITING' });
            } catch (e) {
              // Worker might not be ready, ignore
            }
          }
          
          // Unregister
          const success = await registration.unregister();
          if (success) {
            console.log('[SW Cleanup] Unregistered service worker:', registration.scope);
          } else {
            console.warn('[SW Cleanup] Failed to unregister service worker:', registration.scope);
          }
        } catch (error) {
          console.error('[SW Cleanup] Error unregistering service worker:', error);
        }
      });
      
      await Promise.all(unregisterPromises);
      
      // Clear all caches
      try {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map((cacheName) => {
            console.log('[SW Cleanup] Deleting cache:', cacheName);
            return caches.delete(cacheName);
          })
        );
        console.log('[SW Cleanup] All caches cleared');
      } catch (error) {
        console.warn('[SW Cleanup] Error clearing caches:', error);
      }
      
      // Force reload if we were in development or if service workers were found
      if (import.meta.env.DEV && registrations.length > 0) {
        console.log('[SW Cleanup] Service workers cleaned up. Reloading page...');
        // Small delay to ensure cleanup is complete
        setTimeout(() => {
          window.location.reload();
        }, 500);
      }
    } catch (error) {
      console.error('[SW Cleanup] Error during service worker cleanup:', error);
    }
  };
  
// Make cleanup function available globally for manual cleanup if needed
if (typeof window !== 'undefined') {
  (window as any).cleanupServiceWorkers = cleanupServiceWorkers;
}

// In development and production, clean up old service workers to avoid conflicts
if ('serviceWorker' in navigator) {
  // In development, always clean up service workers
  if (import.meta.env.DEV) {
    // Run cleanup immediately
    cleanupServiceWorkers();
    
    // Also listen for service worker updates and unregister them
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      console.log('[SW Cleanup] Service worker controller changed, cleaning up...');
      cleanupServiceWorkers();
    });
    
    // Listen for messages from service workers
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'SKIP_WAITING') {
        console.log('[SW Cleanup] Received SKIP_WAITING message, cleaning up...');
        cleanupServiceWorkers();
      }
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

