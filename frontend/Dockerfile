# Frontend Next.js (dashboard web) — multi-stage para imagen final liviana.
# Consume la API FastAPI desde el navegador vía NEXT_PUBLIC_API_BASE_URL.

# 1) Build: instala dependencias y compila Next
FROM node:22-alpine AS build
WORKDIR /app
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# NEXT_PUBLIC_* se inyecta en build (es client-side). El navegador llega a la API
# por el puerto publicado en el host, por eso localhost:8000.
ENV NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# 2) Runner: solo lo necesario para servir en producción
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=build /app ./
EXPOSE 5173
# package.json: "start": "next start -p 5173"
CMD ["npm", "run", "start"]
