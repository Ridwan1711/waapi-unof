import crypto from "node:crypto";

import type { NextFunction, Request, Response } from "express";

import { config } from "../../config";
import { signPayload } from "../../utils/signing";

const MAX_SKEW_MS = 5 * 60 * 1000;

function unauthorized(res: Response, message: string): void {
  res.status(401).json({ error: { code: "unauthorized", message } });
}

/**
 * Verify the HMAC signature on internal requests from Django.
 *
 * Signature = HMAC_SHA256(INTERNAL_API_SECRET, `${timestamp}.` + rawBody),
 * sent as the `x-signature` header with `x-timestamp` (epoch ms). Requests
 * older than 5 minutes are rejected to mitigate replay.
 */
export function verifyInternalSignature(req: Request, res: Response, next: NextFunction): void {
  const signature = req.header("x-signature");
  const timestamp = req.header("x-timestamp");

  if (!signature || !timestamp) {
    unauthorized(res, "Missing signature headers.");
    return;
  }

  const age = Math.abs(Date.now() - Number(timestamp));
  if (!Number.isFinite(age) || age > MAX_SKEW_MS) {
    unauthorized(res, "Stale or invalid timestamp.");
    return;
  }

  const body = req.rawBody ?? Buffer.from("");
  const expected = signPayload(config.INTERNAL_API_SECRET, timestamp, body);

  const provided = Buffer.from(signature);
  const expectedBuffer = Buffer.from(expected);
  if (
    provided.length !== expectedBuffer.length ||
    !crypto.timingSafeEqual(provided, expectedBuffer)
  ) {
    unauthorized(res, "Invalid signature.");
    return;
  }

  next();
}
