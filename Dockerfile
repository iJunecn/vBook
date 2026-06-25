# ---- build stage: install all deps + produce the SSR bundle ----
FROM oven/bun:1 AS build
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build          # Astro node standalone -> dist/server/entry.mjs + dist/client

# ---- runtime stage: Node server (the node adapter emits an .mjs that needs Node) ----
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=8080
# App server + its runtime deps. We copy the full node_modules from the build
# stage so the same image can also run the Drizzle migration Job (drizzle-kit is
# a devDependency); see k8s/migrate-job.yaml.
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./package.json
# Migration assets (used only by the pre-roll Job, which overrides the command).
COPY --from=build /app/drizzle ./drizzle
COPY --from=build /app/drizzle.config.ts ./drizzle.config.ts
COPY --from=build /app/src/lib/schema.ts ./src/lib/schema.ts
EXPOSE 8080
USER node
CMD ["node", "./dist/server/entry.mjs"]
