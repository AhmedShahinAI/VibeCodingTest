const ACCESS_TOKEN_KEY = 'elm.accessToken';
const REFRESH_TOKEN_KEY = 'elm.refreshToken';

export interface ApiError {
  error: string;
  reason?: string;
  messageKey: string;
  retryAllowed?: boolean;
}

export class ApiRequestError extends Error {
  constructor(readonly status: number, readonly body: ApiError) {
    super(body.messageKey);
  }
}

function getAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function storeSession(accessToken: string, refreshToken: string): void {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearSession(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function parseErrorBody(response: Response): Promise<ApiError> {
  try {
    return (await response.json()) as ApiError;
  } catch {
    return { error: 'unknown', messageKey: 'errors.generic' };
  }
}

/** Attempts a silent refresh using the stored refresh token; clears the session and returns false if it fails. */
async function trySilentRefresh(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refreshToken }),
  });
  if (!response.ok) {
    clearSession();
    return false;
  }
  const data = (await response.json()) as { accessToken: string; refreshToken: string };
  storeSession(data.accessToken, data.refreshToken);
  return true;
}

/**
 * Thin fetch wrapper: attaches the access token, and on a 401 that isn't
 * itself a login/refresh call, attempts exactly one silent refresh + retry
 * before surfacing the error (spec FR-004/FR-005).
 */
export async function apiRequest<T>(path: string, init: RequestInit = {}, _retry = true): Promise<T> {
  const accessToken = getAccessToken();
  const response = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init.headers,
    },
  });

  if (response.status === 401 && _retry && !path.includes('/auth/login') && !path.includes('/auth/refresh')) {
    const refreshed = await trySilentRefresh();
    if (refreshed) {
      return apiRequest<T>(path, init, false);
    }
  }

  if (!response.ok) {
    throw new ApiRequestError(response.status, await parseErrorBody(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export interface RegisterResponse {
  userId: string;
  status: string;
  mfaSetupRequired: true;
}

export const authApi = {
  register: (input: { email: string; password: string; role: 'learner' | 'course_provider'; locale: 'ar' | 'en' }) =>
    apiRequest<RegisterResponse>('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(input) }),

  mfaSetup: (input: { email: string; password: string }) =>
    apiRequest<{ otpauthUrl: string; secret: string }>('/api/v1/auth/mfa/setup', {
      method: 'POST',
      body: JSON.stringify(input),
    }),

  login: (input: { email: string; password: string }) =>
    apiRequest<{ mfaChallengeToken: string }>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(input) }),

  mfaVerify: (input: { mfaChallengeToken: string; code: string }) =>
    apiRequest<{ accessToken: string; refreshToken: string; expiresIn: number }>('/api/v1/auth/mfa/verify', {
      method: 'POST',
      body: JSON.stringify(input),
    }),

  logout: () => {
    const refreshToken = getRefreshToken();
    clearSession();
    if (!refreshToken) return Promise.resolve();
    return apiRequest<void>('/api/v1/auth/logout', { method: 'POST', body: JSON.stringify({ refreshToken }) });
  },

  me: () => apiRequest<{ userId: string; tenantId: string; role: string; locale: 'ar' | 'en' }>('/api/v1/me'),

  updateLocale: (locale: 'ar' | 'en') =>
    apiRequest<{ locale: 'ar' | 'en' }>('/api/v1/me/locale', { method: 'PUT', body: JSON.stringify({ locale }) }),
};
