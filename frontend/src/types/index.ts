/** Shared types used across the frontend. */

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

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

export type DeviceStatus =
  | "pending"
  | "initializing"
  | "qr"
  | "connected"
  | "disconnected"
  | "failed"
  | "logged_out";

export interface Device {
  id: string;
  name: string;
  phone_number: string;
  status: DeviceStatus;
  provider: string;
  last_seen_at: string | null;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_staff: boolean;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface MeResponse {
  user: User;
  workspaces: Workspace[];
}

export interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  scopes: string[];
  rate_limit_per_min: number;
  is_active: boolean;
  last_used_at: string | null;
  revoked_at: string | null;
  created_at: string;
}

export interface ApiKeyCreated extends ApiKey {
  key: string;
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  secret: string;
  description: string;
  is_active: boolean;
  created_at: string;
}

export interface WebhookDelivery {
  id: string;
  event_type: string;
  status: string;
  attempts: number;
  response_status: number | null;
  next_retry_at: string | null;
  delivered_at: string | null;
  created_at: string;
}

export type MessageDirection = "in" | "out";

export interface Message {
  id: string;
  device: string;
  direction: MessageDirection;
  message_type: string;
  address: string;
  body: string;
  status: string;
  wa_message_id: string;
  error: string;
  created_at: string;
}

export interface ScheduledMessage {
  id: string;
  device: string;
  run_at: string;
  status: string;
  payload: Record<string, unknown>;
  celery_task_id: string;
  last_run_at: string | null;
  created_at: string;
}

export interface AutoReplyRule {
  id: string;
  device: string | null;
  name: string;
  match_type: "exact" | "contains" | "starts_with" | "regex";
  pattern: string;
  case_sensitive: boolean;
  response_body: string;
  is_active: boolean;
  priority: number;
  created_at: string;
}
