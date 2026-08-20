import { PropsWithChildren, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { directionFor, storeLocale, SupportedLanguage } from '../../i18n';

/**
 * Binds `document.dir`/`document.lang` to the active i18next language on
 * every render (spec FR-021: RTL for Arabic, LTR for English, across every
 * Phase 1 screen) and persists the choice so it survives a reload.
 */
export function AppShell({ children }: PropsWithChildren) {
  const { i18n } = useTranslation();
  const language = (i18n.language?.split('-')[0] ?? 'en') as SupportedLanguage;

  useEffect(() => {
    const dir = directionFor(language);
    document.documentElement.dir = dir;
    document.documentElement.lang = language;
    storeLocale(language);
  }, [language]);

  return (
    <div className="min-h-screen bg-white text-gray-900 antialiased" data-testid="app-shell">
      {children}
    </div>
  );
}
