import { SetMetadata } from '@nestjs/common';

export const PERMISSION_KEY = 'elm:requiredPermission';

/**
 * Declares the permission key a route requires (spec FR-010). `RbacGuard`
 * reads this metadata and denies the request if the caller's effective
 * permission set (role defaults + Supervisor overrides) does not include it.
 * A route with no `@RequirePermission` is intentionally left open only for
 * endpoints that are safe pre-permission (e.g. `/auth/login`) — every other
 * protected route MUST carry this decorator so RBAC coverage can be checked
 * mechanically during `/speckit-analyze`.
 */
export const RequirePermission = (permissionKey: string) => SetMetadata(PERMISSION_KEY, permissionKey);
