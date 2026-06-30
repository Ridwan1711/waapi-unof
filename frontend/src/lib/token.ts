/**
 * JWT storage. Kept dependency-free (no imports) so both the API client and the
 * auth helpers can use it without a circular dependency.
 *
 * NOTE: localStorage is used for simplicity in this phase. Hardening (e.g.
 * httpOnly refresh cookies) is addressed in the Authentication phase.
 */
const ACCESS_TOKEN_KEY = "waapi_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
}
