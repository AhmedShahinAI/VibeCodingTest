import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { authApi, ApiRequestError } from './authClient';
import { LanguageToggle } from '../../shared/layout/LanguageToggle';

interface LocationState {
  email: string;
  password: string;
}

/**
 * Implements the TOTP MFA setup step (research.md decision; spec FR-003).
 * Renders the `otpauth://` provisioning URL and raw secret for the user to
 * add to an authenticator app. A rendered QR image is a follow-up polish
 * item (no QR-rendering library is in the Phase 1 stack per plan.md).
 */
export function MfaSetupPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [otpauthUrl, setOtpauthUrl] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!state) return;
    authApi
      .mfaSetup({ email: state.email, password: state.password })
      .then((result) => {
        setOtpauthUrl(result.otpauthUrl);
        setSecret(result.secret);
      })
      .catch((err) => {
        setError(err instanceof ApiRequestError ? t(err.body.messageKey) : t('errors.generic'));
      });
  }, [state, t]);

  if (!state) {
    return <Navigate to="/register" replace />;
  }

  return (
    <main className="mx-auto flex max-w-sm flex-col gap-4 p-6">
      <div className="flex justify-end">
        <LanguageToggle />
      </div>
      <h1 className="text-xl font-semibold">{t('auth.mfaSetup.title')}</h1>
      <p>{t('auth.mfaSetup.instructions')}</p>
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      {secret && (
        <div className="rounded border p-3 text-start">
          <code className="break-all text-sm">{otpauthUrl}</code>
          <p className="mt-2 text-xs text-gray-600">{secret}</p>
        </div>
      )}
      <button
        type="button"
        onClick={() => navigate('/login', { state: { email: state.email } })}
        className="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
        disabled={!secret}
      >
        {t('auth.mfaSetup.continueToLogin')}
      </button>
    </main>
  );
}
