import Redis from "ioredis";

import { config } from "../config";
import type { WaEvent } from "../providers/types";
import { logger } from "../utils/logger";
import { signPayload } from "../utils/signing";

const log = logger.child({ module: "event-bridge" });

/**
 * Forwards WhatsApp events out of the service in two ways:
 *
 *  1. Redis pub/sub on `wa:events:<deviceId>` — consumed by Django to push
 *     real-time updates (QR, status) to the dashboard over SSE.
 *  2. A signed HTTP POST to Django's `/internal/events` — the durable path used
 *     to persist messages, update device status, and trigger webhooks.
 *
 * Both are best-effort here and failures are logged; delivery durability/retries
 * for webhooks live on the Django side.
 */
export class EventBridge {
  private readonly redis: Redis | null;
  private readonly callbackUrl: string;

  constructor() {
    this.redis = config.REDIS_URL
      ? new Redis(config.REDIS_URL, { maxRetriesPerRequest: null })
      : null;
    this.redis?.on("error", (err) => log.error({ err }, "redis connection error"));
    this.callbackUrl = `${config.DJANGO_INTERNAL_CALLBACK_URL.replace(/\/$/, "")}/events`;
  }

  publish(event: WaEvent): void {
    log.info({ deviceId: event.deviceId, type: event.type }, "wa event");
    const message = JSON.stringify(event);
    if (this.redis) {
      this.redis
        .publish(`wa:events:${event.deviceId}`, message)
        .catch((err: unknown) => log.error({ err }, "redis publish failed"));
    }
    void this.postToDjango(message);
  }

  private async postToDjango(message: string): Promise<void> {
    const timestamp = String(Date.now());
    const signature = signPayload(config.INTERNAL_API_SECRET, timestamp, message);
    try {
      const response = await fetch(this.callbackUrl, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-timestamp": timestamp,
          "x-signature": signature,
        },
        body: message,
      });
      if (!response.ok) {
        log.warn({ status: response.status }, "django event callback returned non-2xx");
      }
    } catch (err) {
      log.error({ err }, "django event callback failed");
    }
  }

  async close(): Promise<void> {
    if (this.redis) {
      await this.redis.quit();
    }
  }
}
