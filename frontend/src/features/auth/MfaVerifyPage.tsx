import { FormEvent, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { authApi, ApiRequestError, storeSession } from './authClient';
import { LanguageToggle } from '../../shared/layout/LanguageToggle';

interface LocationState {
  mfaChallengeToken: string;
}

/** Implements spec FR-003/FR-004/FR-007 — completes sign-in on a valid TOTP code. */
export function MfaVerifyPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [retryAllowed, setRetryAllowed] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  if (!state) {
    return <Navigate to="/login" replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const result = await authApi.mfaVerify({ mfaChallengeToken: state!.mfaChallengeToken, code });
      storeSession(result.accessToken, result.refreshToken);
      navigate('/dashboard');
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(t(err.body.messageKey));
        setRetryAllowed(err.body.retryAllowed ?? true);
      } else {
        setError(t('errors.generic'));
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex max-w-sm flex-col gap-4 p-6">
      <div className="flex justify-end">
        <LanguageToggle />
      </div>
      <h1 className="text-xl font-semibold">{t('auth.mfaVerify.title')}</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate>
        <label className="flex flex-col gap-1 text-start">
          <span>{t('auth.mfaVerify.codeLabel')}</span>
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]{6}"
            required
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="rounded border px-3 py-2 tracking-widest"
            autoComplete="one-time-code"
          />
        </label>
        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={submitting || !retryAllowed}
          className="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
        >
          {submitting ? t('common.loading') : t('auth.mfaVerify.submit')}
        </button>
      </form>
    </main>
  );
}
