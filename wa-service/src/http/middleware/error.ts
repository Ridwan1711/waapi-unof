import type { NextFunction, Request, Response } from "express";
import { ZodError } from "zod";

import { AppError } from "../../utils/errors";
import { logger } from "../../utils/logger";

const log = logger.child({ module: "http" });

export function notFound(_req: Request, res: Response): void {
  res.status(404).json({ error: { code: "not_found", message: "Not found." } });
}

export function errorHandler(
  err: unknown,
  _req: Request,
  res: Response,
  _next: NextFunction,
): void {
  if (err instanceof ZodError) {
    res.status(400).json({
      error: { code: "validation_error", message: "Invalid request.", details: err.flatten() },
    });
    return;
  }
  if (err instanceof AppError) {
    res.status(err.statusCode).json({ error: { code: "error", message: err.message } });
    return;
  }
  log.error({ err }, "unhandled error");
  res.status(500).json({ error: { code: "internal_error", message: "Internal server error." } });
}
