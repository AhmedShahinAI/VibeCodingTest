import { useTranslation } from 'react-i18next';
import { SUPPORTED_LANGUAGES, SupportedLanguage } from '../../i18n';

/**
 * Minimal language toggle available on every screen (register/login/MFA are
 * pre-auth, so they cannot depend on the authenticated dashboard's
 * LanguageSwitcher, which additionally persists the choice to the backend —
 * see features/dashboard/LanguageSwitcher.tsx for that authenticated path).
 */
export function LanguageToggle() {
  const { t, i18n } = useTranslation();
  const current = (i18n.language?.split('-')[0] ?? 'en') as SupportedLanguage;

  return (
    <div role="group" aria-label={t('common.languageSwitcherLabel')} className="flex gap-2 text-sm">
      {SUPPORTED_LANGUAGES.map((lang) => (
        <button
          key={lang}
          type="button"
          aria-pressed={current === lang}
          onClick={() => i18n.changeLanguage(lang)}
          className={`rounded px-2 py-1 ${current === lang ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-700'}`}
        >
          {lang === 'ar' ? 'العربية' : 'English'}
        </button>
      ))}
    </div>
  );
}
