import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './en.json';
import ar from './ar.json';

/**
 * Implements spec FR-019/FR-023: persists the user's language choice,
 * falls back to English on any missing key, and logs the gap instead of
 * rendering a raw key or crashing the screen (constitution Principle III).
 */
export const SUPPORTED_LANGUAGES = ['en', 'ar'] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

const STORAGE_KEY = 'elm.locale';

export function getStoredLocale(): SupportedLanguage {
  const stored = typeof window !== 'undefined' ? window.localStorage.getItem(STORAGE_KEY) : null;
  return stored === 'ar' ? 'ar' : 'en';
}

export function storeLocale(locale: SupportedLanguage): void {
  window.localStorage.setItem(STORAGE_KEY, locale);
}

export function directionFor(locale: SupportedLanguage): 'rtl' | 'ltr' {
  return locale === 'ar' ? 'rtl' : 'ltr';
}

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, ar: { translation: ar } },
  lng: getStoredLocale(),
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
  returnEmptyString: false,
  saveMissing: true,
  missingKeyHandler: (languages, _namespace, key) => {
    // eslint-disable-next-line no-console
    console.warn(
      JSON.stringify({
        level: 'warn',
        message: 'i18n missing translation key',
        key,
        languages,
      }),
    );
  },
});

export default i18n;
