import { config } from "./config";
import { createApp } from "./http/app";
import { logger } from "./utils/logger";

const { app, manager, bridge } = createApp();

const server = app.listen(config.WA_SERVICE_PORT, () => {
  logger.info(
    { port: config.WA_SERVICE_PORT, provider: config.WA_DEFAULT_PROVIDER },
    "wa-service listening",
  );
});

async function shutdown(signal: string): Promise<void> {
  logger.info({ signal }, "shutting down");
  server.close();
  await manager.shutdown();
  await bridge.close();
  process.exit(0);
}

process.on("SIGTERM", () => void shutdown("SIGTERM"));
process.on("SIGINT", () => void shutdown("SIGINT"));
