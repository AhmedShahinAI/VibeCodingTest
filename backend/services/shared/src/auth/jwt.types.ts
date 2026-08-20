/** Claims embedded in every Elm Platform access token (research.md: RS256, 15 min TTL). */
export interface AccessTokenClaims {
  sub: string; // userId
  tenantId: string;
  role: string;
  iat: number;
  exp: number;
}
