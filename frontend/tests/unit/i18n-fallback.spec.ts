import { describe, expect, it, vi } from 'vitest';
import i18next from 'i18next';

/**
 * Spec FR-023: a missing translation key falls back to English and logs the
 * gap, instead of rendering a raw key or crashing. Uses an isolated i18next
 * instance (not the app singleton in src/i18n/index.ts) with a key present
 * in English but deliberately absent from Arabic, mirroring the exact
 * production config (fallbackLng: 'en', missingKeyHandler for gap logging).
 */
describe('i18n missing-key fallback (spec FR-023)', () => {
  it('falls back to the English string when a key is missing for the active language', async () => {
    const instance = i18next.createInstance();
    await instance.init({
      lng: 'ar',
      fallbackLng: 'en',
      resources: {
        en: { translation: { 'auth.login.title': 'Sign in' } },
        ar: { translation: {} }, // key deliberately absent
      },
      returnEmptyString: false,
    });

    expect(instance.t('auth.login.title')).toBe('Sign in');
  });

  it('invokes the missing-key handler instead of throwing or returning undefined', async () => {
    const missingKeyHandler = vi.fn();
    const instance = i18next.createInstance();
    await instance.init({
      lng: 'ar',
      fallbackLng: 'en',
      saveMissing: true,
      missingKeyHandler,
      resources: {
        en: { translation: {} },
        ar: { translation: {} },
      },
    });

    const result = instance.t('does.not.exist');

    expect(missingKeyHandler).toHaveBeenCalled();
    expect(result).toBeDefined();
  });
});
