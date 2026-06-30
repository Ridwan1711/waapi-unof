import express, { type Request } from "express";
import helmet from "helmet";
import pinoHttp from "pino-http";

import { EventBridge } from "../events/event-bridge";
import { ProviderManager } from "../session/provider-manager";
import { logger } from "../utils/logger";
import { errorHandler, notFound } from "./middleware/error";
import { healthRouter } from "./routes/health";
import { internalRouter } from "./routes/internal";

export interface CreatedApp {
  app: express.Express;
  manager: ProviderManager;
  bridge: EventBridge;
}

export function createApp(): CreatedApp {
  const bridge = new EventBridge();
  const manager = new ProviderManager(bridge);

  const app = express();
  app.disable("x-powered-by");
  app.use(helmet());
  app.use(pinoHttp({ logger }));
  app.use(
    express.json({
      limit: "25mb",
      // Capture the raw body so the HMAC middleware can verify the signature.
      verify: (req, _res, buf) => {
        (req as Request).rawBody = buf;
      },
    }),
  );

  app.use(healthRouter(manager));
  app.use("/internal", internalRouter(manager));

  app.use(notFound);
  app.use(errorHandler);

  return { app, manager, bridge };
}
