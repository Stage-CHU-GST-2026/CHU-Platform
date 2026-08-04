# syntax=docker/dockerfile:1
# CHU Platform web app (SvelteKit + adapter-node).
#
# Build context = apps/web (see docker-compose.yaml).

# ---- Build stage ----
FROM oven/bun:1-alpine AS build
WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .

# Build -> ./build (adapter-node output)
RUN bun run build

# ---- Runtime stage ----
FROM oven/bun:1-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000

COPY --from=build /app/build ./build
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
    CMD bun -e "fetch('http://127.0.0.1:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["bun", "./build/index.js"]
