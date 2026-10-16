# ==============================================================================
# CampusPulse Frontend Multi-Stage Dockerfile
# Stage 1: Build static assets with Node 22 Alpine
# Stage 2: Serve production bundle with Nginx 1.27 Alpine
# ==============================================================================
FROM node:22-alpine AS build

WORKDIR /app

# Install dependencies (leverage cache)
COPY package.json package-lock.json ./
RUN npm ci

# Copy sources and compile production bundle
COPY . .
RUN npm run build

# ── Stage 2: Production Nginx Server ──────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy built static bundle from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom reverse-proxy and SPA Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
