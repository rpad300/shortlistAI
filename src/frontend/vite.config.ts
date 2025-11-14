import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      // Disable PWA completely in development to avoid service worker conflicts
      devOptions: {
        enabled: false,
        type: 'module'
      },
      // Only register service worker in production builds
      // Use 'null' to prevent any registration script injection in dev
      injectRegister: process.env.NODE_ENV === 'production' ? 'script' : null,
      manifest: {
        name: 'CV Analysis Platform',
        short_name: 'CV Analysis',
        description: 'AI-powered CV analysis for interviewers and candidates',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any maskable'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        // Workbox configuration for service worker caching strategies
        // Skip waiting - immediately activate new service worker
        skipWaiting: true,
        clientsClaim: true,
        
        // Exclude index.html from precaching - we'll handle it with NetworkFirst
        // This ensures the latest version is always fetched
        globIgnores: ['**/index.html'],
        
        // Disable default navigation fallback since we're handling it with runtime caching
        // This prevents the error about trying to create handler for non-precached index.html
        navigateFallback: null,
        navigateFallbackDenylist: [/^\/_/, /\/[^/?]+\.[^/]+$/],
        
        runtimeCaching: [
          {
            // Root path and SPA routes - NetworkFirst to always get latest index.html
            // This must be FIRST to catch navigation requests before other patterns
            urlPattern: ({ request }) => request.mode === 'navigate',
            handler: 'NetworkFirst',
            options: {
              cacheName: 'navigation-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 0 // No cache expiration - always check network
              },
              networkTimeoutSeconds: 3 // Quick timeout to fallback to cache if offline
            }
          },
          {
            // HTML pages - always check network first, fallback to cache only if offline
            urlPattern: /^https?:\/\/.*\/.*\.html$/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'html-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 0 // No cache expiration - always check network
              },
              networkTimeoutSeconds: 3 // Quick timeout to fallback to cache if offline
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              }
            }
          },
          {
            urlPattern: /^https:\/\/.*\.supabase\.co\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'supabase-api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 5 // 5 minutes
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@services': path.resolve(__dirname, './src/services'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
      '@assets': path.resolve(__dirname, './src/assets')
    }
  },
  server: {
    port: 3000,
    hmr: {
      // Reduce WebSocket connection issues
      clientPort: 3000,
      protocol: 'ws',
      host: 'localhost'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Ensure consistent asset hashing for cache busting
    rollupOptions: {
      output: {
        // Use content hash for better cache busting
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `assets/[name]-[hash][extname]`;
          }
          if (/css/i.test(ext)) {
            return `assets/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'i18n-vendor': ['i18next', 'react-i18next'],
          'supabase-vendor': ['@supabase/supabase-js']
        }
      }
    },
    // Ensure CSS is properly extracted and hashed
    cssCodeSplit: true
  }
});

