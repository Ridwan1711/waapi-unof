import pino from "pino";

import { config, isProduction } from "../config";

export const logger = pino({
  level: config.LOG_LEVEL,
  // Pretty-print in development; structured JSON in production.
  ...(isProduction ? {} : { transport: { target: "pino-pretty", options: { colorize: true } } }),
});
