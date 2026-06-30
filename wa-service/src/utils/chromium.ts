import { existsSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";

import { logger } from "./logger";

// Chromium runtime lock/coordination files (NOT WhatsApp session data).
const LOCK_FILES = new Set([
  "SingletonLock",
  "SingletonSocket",
  "SingletonCookie",
  "DevToolsActivePort",
]);

/**
 * Remove stale Chromium singleton lock files in a single browser profile dir.
 *
 * After a container restart or a crash, the previous Chromium leaves a
 * `SingletonLock` (tagged with the old hostname/pid) in the persisted profile,
 * which makes the next launch fail with "profile appears to be in use by
 * another Chromium process". These are runtime locks, not session/auth data, so
 * removing them is safe — and it only touches the given profile dir, so other
 * devices (and any other whatsapp-web.js service) are never affected.
 */
export function clearStaleChromiumLocks(profileDir: string): void {
  if (!existsSync(profileDir)) return;

  let removed = 0;
  try {
    for (const entry of readdirSync(profileDir, { withFileTypes: true })) {
      if (entry.isDirectory()) continue;
      if (LOCK_FILES.has(entry.name)) {
        rmSync(join(profileDir, entry.name), { force: true });
        removed += 1;
      }
    }
  } catch {
    // Profile dir unreadable or already gone — nothing to clean.
    return;
  }

  if (removed > 0) {
    logger.warn({ profileDir, removed }, "cleared stale Chromium lock files");
  }
}
