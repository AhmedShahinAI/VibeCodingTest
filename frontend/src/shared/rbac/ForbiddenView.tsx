import { useTranslation } from 'react-i18next';

/** Localized "You don't have access" view (PRD edge case; spec Requirements Cross-Cutting Contract). */
export function ForbiddenView() {
  const { t } = useTranslation();
  return (
    <div role="alert" className="rounded border border-red-200 bg-red-50 p-4 text-red-800">
      {t('errors.forbidden')}
    </div>
  );
}
