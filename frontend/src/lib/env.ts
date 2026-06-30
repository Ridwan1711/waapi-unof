/**
 * Typed access to public environment variables.
 *
 * NEXT_PUBLIC_* values are inlined at build time, so they must be present when
 * the frontend image is built (see frontend/Dockerfile build args).
 */
export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "waapi-unof",
} as const;
