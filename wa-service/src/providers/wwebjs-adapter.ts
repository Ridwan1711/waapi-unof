import { join } from "node:path";

import QRCode from "qrcode";
import { Client, MessageMedia } from "whatsapp-web.js";

import { createAuthStrategy } from "../auth-store";
import { config } from "../config";
import { clearStaleChromiumLocks } from "../utils/chromium";
import { logger } from "../utils/logger";
import { sleep } from "../utils/errors";
import type {
  SendMediaInput,
  SendResult,
  SendTextInput,
  WaEvent,
  WaEventListener,
  WaEventType,
  WaStatus,
  WhatsAppProvider,
} from "./types";

const log = logger.child({ module: "wwebjs" });

/** Pick a human-like delay (ms) before sending, to reduce ban risk. */
function randomSendDelay(): number {
  const { WA_SEND_MIN_DELAY_MS: min, WA_SEND_MAX_DELAY_MS: max } = config;
  const spread = Math.max(0, max - min);
  return min + Math.floor(Math.random() * (spread + 1));
}

/** Normalize a phone number or JID into a WhatsApp chat id. */
function toChatId(to: string): string {
  if (to.includes("@")) return to;
  const digits = to.replace(/[^\d]/g, "");
  return `${digits}@c.us`;
}

export class WwebjsAdapter implements WhatsAppProvider {
  private readonly client: Client;
  private status: WaStatus = "pending";
  private lastQr: string | null = null;
  private readonly listeners = new Set<WaEventListener>();

  constructor(public readonly deviceId: string) {
    this.client = new Client({
      authStrategy: createAuthStrategy(deviceId),
      puppeteer: {
        headless: true,
        executablePath: config.PUPPETEER_EXECUTABLE_PATH || undefined,
        args: [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-dev-shm-usage",
          "--disable-gpu",
        ],
        timeout: 60_000,
      },
    });
    this.registerHandlers();
  }

  private registerHandlers(): void {
    this.client.on("qr", (qr) => {
      QRCode.toDataURL(qr)
        .then((dataUrl) => {
          this.lastQr = dataUrl;
          this.status = "qr";
          this.emit("qr", { qr: dataUrl });
        })
        .catch((err: unknown) => log.error({ err, deviceId: this.deviceId }, "qr encode failed"));
    });

    this.client.on("ready", () => {
      this.status = "connected";
      this.lastQr = null;
      this.emit("ready", { phone: this.client.info?.wid?.user ?? "" });
    });

    this.client.on("auth_failure", (message) => {
      this.status = "failed";
      this.emit("state", { state: "auth_failure", message });
    });

    this.client.on("disconnected", (reason) => {
      this.status = "disconnected";
      this.emit("disconnected", { reason: String(reason) });
    });

    this.client.on("message", (msg) => {
      this.emit("message", {
        waMessageId: msg.id?._serialized ?? "",
        from: msg.from,
        to: msg.to,
        body: msg.body,
        messageType: msg.type,
        hasMedia: msg.hasMedia,
        timestamp: msg.timestamp,
      });
    });
  }

  async init(): Promise<void> {
    this.status = "initializing";
    // Clear any stale Chromium lock left by a previous container/crash for THIS
    // device's profile, so the browser can launch (fixes "profile in use").
    clearStaleChromiumLocks(join(config.WA_DATA_DIR, `session-${this.deviceId}`));
    log.info({ deviceId: this.deviceId }, "initializing session");
    try {
      await this.client.initialize();
    } catch (err) {
      // Surface the failure (e.g. Chromium OOM / launch error) instead of leaving
      // the device stuck on "initializing" forever.
      this.status = "failed";
      log.error({ err, deviceId: this.deviceId }, "session init failed");
      this.emit("state", {
        state: "failed",
        message: err instanceof Error ? err.message : String(err),
      });
      throw err;
    }
  }

  getStatus(): WaStatus {
    return this.status;
  }

  getQR(): string | null {
    return this.lastQr;
  }

  async sendText(input: SendTextInput): Promise<SendResult> {
    await sleep(randomSendDelay());
    const sent = await this.client.sendMessage(toChatId(input.to), input.body);
    return { waMessageId: sent.id?._serialized ?? "" };
  }

  async sendMedia(input: SendMediaInput): Promise<SendResult> {
    await sleep(randomSendDelay());
    const media = new MessageMedia(input.mimeType, input.dataBase64, input.filename);
    const sent = await this.client.sendMessage(toChatId(input.to), media, {
      caption: input.caption,
    });
    return { waMessageId: sent.id?._serialized ?? "" };
  }

  async logout(): Promise<void> {
    await this.client.logout();
    this.status = "logged_out";
  }

  async destroy(): Promise<void> {
    await this.client.destroy();
  }

  on(listener: WaEventListener): void {
    this.listeners.add(listener);
  }

  private emit(type: WaEventType, data: Record<string, unknown>): void {
    const event: WaEvent = {
      deviceId: this.deviceId,
      type,
      data,
      timestamp: new Date().toISOString(),
    };
    for (const listener of this.listeners) {
      listener(event);
    }
  }
}
