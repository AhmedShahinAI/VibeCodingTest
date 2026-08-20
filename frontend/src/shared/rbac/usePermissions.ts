import { useEffect, useState } from 'react';
import { apiRequest } from '../../features/auth/authClient';

export interface PermissionsState {
  role: string | null;
  permissions: Set<string>;
  loading: boolean;
}

/**
 * Consumes `GET /rbac/permissions/me` (contracts/tenancy-api.md) so the UI
 * can render only permitted sections/actions. This is defense-in-depth for
 * UX only — the server enforces the real boundary via `RbacGuard` on every
 * request regardless of what the UI shows (spec FR-010/FR-011).
 */
export function usePermissions(): PermissionsState {
  const [state, setState] = useState<PermissionsState>({ role: null, permissions: new Set(), loading: true });

  useEffect(() => {
    let cancelled = false;
    apiRequest<{ role: string; permissions: string[] }>('/api/v1/rbac/permissions/me')
      .then((result) => {
        if (!cancelled) {
          setState({ role: result.role, permissions: new Set(result.permissions), loading: false });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setState({ role: null, permissions: new Set(), loading: false });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
