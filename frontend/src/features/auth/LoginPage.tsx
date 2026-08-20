import { FormEvent, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import { authApi, ApiRequestError } from './authClient';
import { LanguageToggle } from '../../shared/layout/LanguageToggle';

/** Implements spec FR-003/FR-006 — primary-credential step; issues no session token itself. */
export function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const prefillEmail = (location.state as { email?: string } | null)?.email ?? '';

  const [email, setEmail] = useState(prefillEmail);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const { mfaChallengeToken } = await authApi.login({ email, password });
      navigate('/mfa-verify', { state: { mfaChallengeToken } });
    } catch (err) {
      setError(err instanceof ApiRequestError ? t(err.body.messageKey) : t('errors.generic'));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex max-w-sm flex-col gap-4 p-6">
      <div className="flex justify-end">
        <LanguageToggle />
      </div>
      <h1 className="text-xl font-semibold">{t('auth.login.title')}</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate>
        <label className="flex flex-col gap-1 text-start">
          <span>{t('auth.login.emailLabel')}</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded border px-3 py-2"
            autoComplete="email"
          />
        </label>
        <label className="flex flex-col gap-1 text-start">
          <span>{t('auth.login.passwordLabel')}</span>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded border px-3 py-2"
            autoComplete="current-password"
          />
        </label>
        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
        >
          {submitting ? t('common.loading') : t('auth.login.submit')}
        </button>
      </form>
    </main>
  );
}
