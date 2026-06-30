import { describe, expect, it, vi } from "vitest";

import type { EventBridge } from "../events/event-bridge";
import type { WaEvent, WaEventListener, WhatsAppProvider } from "../providers/types";
import { ProviderManager } from "./provider-manager";

type FakeProvider = WhatsAppProvider & { fire: (event: WaEvent) => void };

function makeFakeProvider(deviceId: string): FakeProvider {
  let listener: WaEventListener | null = null;
  return {
    deviceId,
    init: vi.fn(async () => undefined),
    getStatus: () => "initializing",
    getQR: () => null,
    sendText: vi.fn(async () => ({ waMessageId: "x" })),
    sendMedia: vi.fn(async () => ({ waMessageId: "x" })),
    logout: vi.fn(async () => undefined),
    destroy: vi.fn(async () => undefined),
    on: (l: WaEventListener) => {
      listener = l;
    },
    fire: (event: WaEvent) => listener?.(event),
  };
}

function fakeBridge(): EventBridge {
  return { publish: vi.fn() } as unknown as EventBridge;
}

describe("ProviderManager", () => {
  it("creates and tracks a session", () => {
    const fake = makeFakeProvider("dev1");
    const manager = new ProviderManager(fakeBridge(), () => fake);

    const status = manager.init("dev1");

    expect(status).toBe("initializing");
    expect(manager.has("dev1")).toBe(true);
    expect(manager.size()).toBe(1);
  });

  it("forwards provider events to the bridge", () => {
    const bridge = fakeBridge();
    const fake = makeFakeProvider("dev1");
    const manager = new ProviderManager(bridge, () => fake);

    manager.init("dev1");
    fake.fire({ deviceId: "dev1", type: "ready", data: {}, timestamp: "t" });

    expect(bridge.publish).toHaveBeenCalledTimes(1);
  });

  it("removes a session", async () => {
    const fake = makeFakeProvider("dev1");
    const manager = new ProviderManager(fakeBridge(), () => fake);

    manager.init("dev1");
    await manager.remove("dev1");

    expect(fake.destroy).toHaveBeenCalled();
    expect(manager.has("dev1")).toBe(false);
  });
});
