import "dotenv/config";

import { z } from "zod";

/**
 * Validated, typed configuration. The service refuses to start with an invalid
 * environment (fail fast). Defaults make local development frictionless.
 */
const schema = z.object({
  NODE_ENV: z.string().default("development"),
  WA_SERVICE_PORT: z.coerce.number().int().positive().default(8090),
  WA_DEFAULT_PROVIDER: z.enum(["wwebjs", "baileys"]).default("wwebjs"),
  WA_SESSION_STORAGE: z.enum(["local", "remote"]).default("local"),
  WA_DATA_DIR: z.string().default("./.wwebjs_auth"),
  INTERNAL_API_SECRET: z.string().min(1).default("change-me-internal-hmac-secret"),
  DJANGO_INTERNAL_CALLBACK_URL: z.string().url().default("http://localhost:8000/internal"),
  REDIS_URL: z.string().optional(),
  LOG_LEVEL: z.string().default("info"),
  WA_SEND_MIN_DELAY_MS: z.coerce.number().int().nonnegative().default(1500),
  WA_SEND_MAX_DELAY_MS: z.coerce.number().int().nonnegative().default(4000),
  PUPPETEER_EXECUTABLE_PATH: z.string().optional(),
});

export type AppConfig = z.infer<typeof schema>;

export const config: AppConfig = schema.parse(process.env);

export const isProduction = config.NODE_ENV === "production";
