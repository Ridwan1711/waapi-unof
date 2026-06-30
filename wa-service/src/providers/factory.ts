import { config } from "../config";
import { AppError } from "../utils/errors";

import type { WhatsAppProvider } from "./types";
import { WwebjsAdapter } from "./wwebjs-adapter";

/** Construct a provider for the configured engine. */
export function createProvider(deviceId: string): WhatsAppProvider {
  switch (config.WA_DEFAULT_PROVIDER) {
    case "wwebjs":
      return new WwebjsAdapter(deviceId);
    case "baileys":
      // The Baileys adapter (lighter, no browser) is planned for scale. The
      // provider interface lets us add it without touching any caller.
      throw new AppError(501, "Baileys provider is not implemented yet.");
    default:
      throw new AppError(500, `Unknown WA provider: ${String(config.WA_DEFAULT_PROVIDER)}`);
  }
}
