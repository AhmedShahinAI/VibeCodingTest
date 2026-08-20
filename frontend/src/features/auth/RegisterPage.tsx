import { FormEvent, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { authApi, ApiRequestError } from './authClient';
import { LanguageToggle } from '../../shared/layout/LanguageToggle';

/** Implements spec FR-001/FR-020 — email/password registration, fully localized, inline-validated. */
export function RegisterPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'learner' | 'course_provider'>('learner');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await authApi.register({
        email,
        password,
        role,
        locale: (i18n.language?.split('-')[0] as 'ar' | 'en') ?? 'en',
      });
      navigate('/mfa-setup', { state: { email, password } });
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(t(err.body.messageKey));
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
      <h1 className="text-xl font-semibold">{t('auth.register.title')}</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate>
        <label className="flex flex-col gap-1 text-start">
          <span>{t('auth.register.emailLabel')}</span>
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
          <span>{t('auth.register.passwordLabel')}</span>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded border px-3 py-2"
            autoComplete="new-password"
          />
        </label>
        <fieldset className="flex flex-col gap-1 text-start">
          <legend>{t('auth.register.roleLabel')}</legend>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="role"
              checked={role === 'learner'}
              onChange={() => setRole('learner')}
            />
            {t('auth.register.roleLearner')}
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="role"
              checked={role === 'course_provider'}
              onChange={() => setRole('course_provider')}
            />
            {t('auth.register.roleInstructor')}
          </label>
        </fieldset>
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
          {submitting ? t('common.loading') : t('auth.register.submit')}
        </button>
      </form>
    </main>
  );
}
