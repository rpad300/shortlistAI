/**
 * i18n configuration for multi-language support.
 * 
 * Supports: English (EN), Portuguese (PT), French (FR), Spanish (ES)
 * Base language: English
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import pt from './locales/pt.json';
import fr from './locales/fr.json';
import es from './locales/es.json';

// Detect browser language or use default
const getBrowserLanguage = (): string => {
  const browserLang = navigator.language.split('-')[0];
  const supportedLanguages = ['en', 'pt', 'fr', 'es'];
  return supportedLanguages.includes(browserLang) ? browserLang : 'en';
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      pt: { translation: pt },
      fr: { translation: fr },
      es: { translation: es }
    },
    lng: localStorage.getItem('language') || getBrowserLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // React already escapes
    },
    react: {
      useSuspense: false
    }
  });

// Save language preference when it changes
i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
  document.documentElement.lang = lng;
});

export default i18n;

