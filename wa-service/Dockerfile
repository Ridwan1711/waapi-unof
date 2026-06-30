# syntax=docker/dockerfile:1
# =============================================================================
# WhatsApp service image (Node + Express + whatsapp-web.js).
# Build context = repository root.
#
# whatsapp-web.js drives a real Chromium via Puppeteer, so we install the
# system Chromium + its shared-library dependencies and point Puppeteer at it
# (PUPPETEER_SKIP_DOWNLOAD avoids downloading a second copy).
# =============================================================================

FROM node:22-bookworm-slim AS base
# NODE_ENV is intentionally NOT "production" here: the deps/builder stages need
# devDependencies (typescript, @types/*) to compile. It is set to production
# only in the final runtime stage below.
ENV PUPPETEER_SKIP_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        ca-certificates fonts-liberation curl \
        libnss3 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
        libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# ---- deps -------------------------------------------------------------------
FROM base AS deps
COPY wa-service/package.json wa-service/package-lock.json ./
# --include=dev guarantees devDependencies are installed for the TypeScript build.
RUN npm ci --include=dev

# ---- builder (TypeScript -> dist) ------------------------------------------
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY wa-service/ ./
RUN npm run build && npm prune --omit=dev

# ---- final ------------------------------------------------------------------
FROM base AS runner
ENV NODE_ENV=production
RUN groupadd --system waapp \
    && useradd --system --gid waapp --home-dir /app --shell /usr/sbin/nologin waapp \
    && mkdir -p /data/sessions \
    && chown -R waapp:waapp /app /data
COPY --from=builder --chown=waapp:waapp /app/node_modules ./node_modules
COPY --from=builder --chown=waapp:waapp /app/dist ./dist
COPY --from=builder --chown=waapp:waapp /app/package.json ./package.json
USER waapp
EXPOSE 8090
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD node -e "fetch('http://localhost:'+(process.env.WA_SERVICE_PORT||8090)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "dist/index.js"]
