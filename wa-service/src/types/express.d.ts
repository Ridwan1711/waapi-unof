export {};

declare global {
  // Augment Express's Request with the raw body captured for HMAC verification.
  namespace Express {
    interface Request {
      rawBody?: Buffer;
    }
  }
}
