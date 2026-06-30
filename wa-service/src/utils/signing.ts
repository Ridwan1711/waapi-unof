import crypto from "node:crypto";

/**
 * HMAC-SHA256 over `${timestamp}.` + body.
 *
 * Shared by inbound request verification (Django -> Node) and outbound event
 * signing (Node -> Django). Must stay byte-for-byte identical to the Django
 * implementation in `apps/core/signing.py`.
 */
export function signPayload(secret: string, timestamp: string, body: Buffer | string): string {
  return crypto.createHmac("sha256", secret).update(`${timestamp}.`).update(body).digest("hex");
}
