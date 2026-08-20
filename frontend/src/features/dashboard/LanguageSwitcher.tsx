import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES, SupportedLanguage } from '../../i18n';
import { authApi } from '../auth/authClient';

/**
 * Authenticated language switcher (spec FR-019): unlike the pre-auth
 * `LanguageToggle` (shared/layout), this one persists the choice to
 * `User.locale` via `PUT /me/locale` so it survives across devices/sessions,
 * not just this browser's localStorage.
 */
export function LanguageSwitcher() {
  const { t, i18n } = useTranslation();
  const current = (i18n.language?.split('-')[0] ?? 'en') as SupportedLanguage;

  async function select(lang: SupportedLanguage) {
    await i18n.changeLanguage(lang);
    try {
      await authApi.updateLocale(lang);
    } catch {
      // Persisting the preference failed (e.g. session expired); the local
      // UI has already switched, so this is a non-blocking best-effort sync.
    }
  }

  return (
    <div role="group" aria-label={t('common.languageSwitcherLabel')} className="flex gap-2 text-sm">
      {SUPPORTED_LANGUAGES.map((lang) => (
        <button
          key={lang}
          type="button"
          aria-pressed={current === lang}
          onClick={() => select(lang)}
          className={`rounded px-2 py-1 ${current === lang ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          {lang === 'ar' ? 'العربية' : 'English'}
        </button>
      ))}
    </div>
  );
}
