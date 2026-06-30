import type { EventBridge } from "../events/event-bridge";
import { createProvider } from "../providers/factory";
import type { WaStatus, WhatsAppProvider } from "../providers/types";
import { logger } from "../utils/logger";

const log = logger.child({ module: "provider-manager" });

/**
 * Owns the live WhatsApp sessions for this worker.
 *
 * The registry is in-memory here; the API Communication / Device Management
 * phases back it with Redis (device -> worker mapping + heartbeats) so sessions
 * can be routed and re-homed across a worker pool.
 */
export class ProviderManager {
  private readonly sessions = new Map<string, WhatsAppProvider>();

  constructor(private readonly bridge: EventBridge) {}

  has(deviceId: string): boolean {
    return this.sessions.has(deviceId);
  }

  get(deviceId: string): WhatsAppProvider | undefined {
    return this.sessions.get(deviceId);
  }

  list(): string[] {
    return [...this.sessions.keys()];
  }

  size(): number {
    return this.sessions.size;
  }

  /** Create (if needed) and initialize a session. Returns the current status. */
  init(deviceId: string): WaStatus {
    let provider = this.sessions.get(deviceId);
    if (!provider) {
      provider = createProvider(deviceId);
      provider.on((event) => this.bridge.publish(event));
      this.sessions.set(deviceId, provider);
    }
    // Initialization (launching the browser, handshaking) happens in the
    // background; progress is reported via emitted events.
    provider.init().catch((err: unknown) => {
      log.error({ err, deviceId }, "session init failed");
    });
    return provider.getStatus();
  }

  async remove(deviceId: string): Promise<void> {
    const provider = this.sessions.get(deviceId);
    if (!provider) return;
    await provider.destroy().catch((err: unknown) => {
      log.error({ err, deviceId }, "session destroy failed");
    });
    this.sessions.delete(deviceId);
  }

  async shutdown(): Promise<void> {
    await Promise.all(
      [...this.sessions.values()].map((provider) => provider.destroy().catch(() => undefined)),
    );
    this.sessions.clear();
  }
}
