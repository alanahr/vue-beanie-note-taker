# Multi-stage build: build the Vue app, then serve with Vite preview

FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS serve

WORKDIR /app

COPY --from=build /app/package.json /app/package-lock.json ./
COPY --from=build /app/dist ./dist
COPY --from=build /app/vite.config.ts ./
COPY --from=build /app/tsconfig.json ./
COPY --from=build /app/tsconfig.app.json ./
COPY --from=build /app/tsconfig.node.json ./

RUN npm install --omit=dev vite

EXPOSE ${CLIENT_PORT}

CMD ["npx", "vite", "preview", "--host", "0.0.0.0", "--port", "5173"]
