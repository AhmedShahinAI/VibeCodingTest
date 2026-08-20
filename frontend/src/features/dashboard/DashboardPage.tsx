import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { authApi } from '../auth/authClient';
import { LanguageSwitcher } from './LanguageSwitcher';
import { usePermissions } from '../../shared/rbac/usePermissions';

/**
 * Role-scoped dashboard shell (spec User Story 2 / FR-010): each section is
 * gated by a permission key from `usePermissions`, so a user only ever sees
 * the actions their role (and any Supervisor overrides) actually permit.
 * The server is still the real boundary (`RbacGuard` on every endpoint) —
 * this is UX-only defense-in-depth, per contracts/tenancy-api.md.
 */
const SECTIONS: { permission: string; labelKey: string }[] = [
  { permission: 'course.enroll', labelKey: 'dashboard.sections.browseCourses' },
  { permission: 'course.manage_own', labelKey: 'dashboard.sections.manageCourses' },
  { permission: 'course.grade_assigned', labelKey: 'dashboard.sections.gradeAssigned' },
  { permission: 'course.review_flagged', labelKey: 'dashboard.sections.reviewFlagged' },
  { permission: 'course.review_approve', labelKey: 'dashboard.sections.reviewApprove' },
  { permission: 'user.manage_all', labelKey: 'dashboard.sections.manageUsers' },
  { permission: 'tenant.manage_settings', labelKey: 'dashboard.sections.tenantSettings' },
  { permission: 'tenant.provision', labelKey: 'dashboard.sections.provisionTenants' },
];

export function DashboardPage() {
  const { t } = useTranslation();
  const [me, setMe] = useState<{ role: string } | null>(null);
  const { permissions, loading } = usePermissions();

  useEffect(() => {
    authApi.me().then(setMe).catch(() => setMe(null));
  }, []);

  const visibleSections = SECTIONS.filter((section) => permissions.has(section.permission));

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 p-6">
      <div className="flex justify-end">
        <LanguageSwitcher />
      </div>
      <h1 className="text-xl font-semibold">{t('dashboard.title')}</h1>
      {me && <p>{t('dashboard.welcome', { role: me.role })}</p>}
      {loading ? (
        <p>{t('common.loading')}</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {visibleSections.map((section) => (
            <li key={section.permission} className="rounded border p-3 text-start">
              {t(section.labelKey)}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
