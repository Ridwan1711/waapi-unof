/** Engine-agnostic WhatsApp provider contract.
 *
 * Every engine (whatsapp-web.js today, Baileys later) implements this so the
 * rest of the service — and the whole platform — never depends on a specific
 * library. New engines are added as adapters without touching callers.
 */

export type WaStatus =
  "pending" | "initializing" | "qr" | "connected" | "disconnected" | "failed" | "logged_out";

export type WaEventType = "qr" | "ready" | "disconnected" | "message" | "state";

export interface WaEvent {
  deviceId: string;
  type: WaEventType;
  data: Record<string, unknown>;
  timestamp: string;
}

export type WaEventListener = (event: WaEvent) => void;

export interface SendTextInput {
  to: string;
  body: string;
}

export interface SendMediaInput {
  to: string;
  mimeType: string;
  dataBase64: string;
  filename?: string;
  caption?: string;
}

export interface SendResult {
  waMessageId: string;
}

export interface WhatsAppProvider {
  readonly deviceId: string;
  init(): Promise<void>;
  getStatus(): WaStatus;
  getQR(): string | null;
  sendText(input: SendTextInput): Promise<SendResult>;
  sendMedia(input: SendMediaInput): Promise<SendResult>;
  logout(): Promise<void>;
  destroy(): Promise<void>;
  on(listener: WaEventListener): void;
}
