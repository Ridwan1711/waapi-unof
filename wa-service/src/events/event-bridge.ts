import { logger } from "../utils/logger";
import type { WaEvent } from "../providers/types";

const log = logger.child({ module: "event-bridge" });

/**
 * Forwards WhatsApp events out of the service.
 *
 * In this phase events are logged. The API Communication phase extends
 * `publish` to fan out over Redis pub/sub and POST an HMAC-signed event to the
 * Django callback (DJANGO_INTERNAL_CALLBACK_URL). Keeping that here means the
 * provider/session code never changes when transport is added.
 */
export class EventBridge {
  publish(event: WaEvent): void {
    log.info({ deviceId: event.deviceId, type: event.type }, "wa event");
  }
}
