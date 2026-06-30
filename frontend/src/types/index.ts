/** Shared types used across the frontend. */

/** Standard API error envelope (see docs/api.md). */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/** Generic paginated list response. */
export interface Paginated<T> {
  results: T[];
  pagination: {
    count: number;
    page: number;
    pages: number;
    page_size: number;
    next: string | null;
    previous: string | null;
  };
}
