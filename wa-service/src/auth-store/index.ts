import { LocalAuth } from "whatsapp-web.js";

import { config } from "../config";

/**
 * Build the whatsapp-web.js auth strategy.
 *
 * LocalAuth persists each session on disk under WA_DATA_DIR (one folder per
 * device). For horizontal scaling, a RemoteAuth strategy (storing sessions in
 * Postgres/S3) can be swapped in here so sessions can move between workers —
 * the rest of the adapter is unaffected.
 */
export function createAuthStrategy(deviceId: string): LocalAuth {
  return new LocalAuth({ clientId: deviceId, dataPath: config.WA_DATA_DIR });
}
