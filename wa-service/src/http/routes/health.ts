import { Router } from "express";

import { config } from "../../config";
import type { ProviderManager } from "../../session/provider-manager";

/** Liveness endpoint used by the container HEALTHCHECK (unauthenticated). */
export function healthRouter(manager: ProviderManager): Router {
  const router = Router();
  router.get("/health", (_req, res) => {
    res.json({
      status: "ok",
      provider: config.WA_DEFAULT_PROVIDER,
      sessions: manager.size(),
    });
  });
  return router;
}
