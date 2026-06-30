import { Router } from "express";
import { z } from "zod";

import type { ProviderManager } from "../../session/provider-manager";
import { AppError } from "../../utils/errors";
import { asyncHandler } from "../async-handler";
import { verifyInternalSignature } from "../middleware/hmac";

const initSchema = z.object({ deviceId: z.string().min(1) });

const sendSchema = z.object({
  type: z.enum(["text", "media"]).default("text"),
  to: z.string().min(1),
  body: z.string().optional(),
  media: z
    .object({
      mimeType: z.string().min(1),
      dataBase64: z.string().min(1),
      filename: z.string().optional(),
      caption: z.string().optional(),
    })
    .optional(),
});

/**
 * Internal API consumed by Django. All routes are HMAC-authenticated.
 */
export function internalRouter(manager: ProviderManager): Router {
  const router = Router();
  router.use(verifyInternalSignature);

  // Create + initialize a device session.
  router.post(
    "/sessions",
    asyncHandler(async (req, res) => {
      const { deviceId } = initSchema.parse(req.body);
      const status = manager.init(deviceId);
      res.status(202).json({ deviceId, status });
    }),
  );

  // Current status (+ last QR data URL, if awaiting scan).
  router.get("/devices/:id/status", (req, res) => {
    const provider = manager.get(req.params.id);
    if (!provider) throw new AppError(404, "Device session not found.");
    res.json({ deviceId: req.params.id, status: provider.getStatus(), qr: provider.getQR() });
  });

  // Send a text or media message.
  router.post(
    "/devices/:id/send",
    asyncHandler(async (req, res) => {
      const deviceId = req.params.id as string;
      const provider = manager.get(deviceId);
      if (!provider) throw new AppError(404, "Device session not found.");

      const input = sendSchema.parse(req.body);
      if (input.type === "media") {
        if (!input.media) throw new AppError(400, "media is required when type=media.");
        const result = await provider.sendMedia({ to: input.to, ...input.media });
        res.status(202).json(result);
        return;
      }
      if (!input.body) throw new AppError(400, "body is required when type=text.");
      const result = await provider.sendText({ to: input.to, body: input.body });
      res.status(202).json(result);
    }),
  );

  // Log out and tear down a session.
  router.post(
    "/devices/:id/logout",
    asyncHandler(async (req, res) => {
      const deviceId = req.params.id as string;
      await manager.remove(deviceId);
      res.status(202).json({ deviceId, status: "logged_out" });
    }),
  );

  return router;
}
