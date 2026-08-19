FROM cypress/included:13.15.0

WORKDIR /e2e

COPY package.json package-lock.json* ./
RUN npm install --omit=dev

COPY cypress.config.ts ./
COPY cypress ./cypress

ENTRYPOINT ["cypress", "run"]
