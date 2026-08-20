import en from './en.json';
import ar from './ar.json';

type MessageKey = keyof typeof en;

const RESOURCES: Record<'en' | 'ar', Record<string, string>> = { en, ar };

/**
 * Server-side counterpart to the frontend's i18next config (spec FR-022:
 * notifications/messages are delivered in the user's selected language).
 * Falls back to English when a key is missing for the requested locale,
 * mirroring the frontend's fallback-and-log behavior (FR-023) rather than
 * throwing — a missing translation must never break message delivery.
 */
export function resolveMessage(locale: 'ar' | 'en', key: MessageKey, params?: Record<string, string>): string {
  const template = RESOURCES[locale]?.[key] ?? RESOURCES.en[key];
  if (!template) {
    // eslint-disable-next-line no-console
    console.warn(JSON.stringify({ level: 'warn', message: 'i18n missing message key', key, locale }));
    return key;
  }
  if (!params) return template;
  return Object.entries(params).reduce((text, [name, value]) => text.replaceAll(`{{${name}}}`, value), template);
}
