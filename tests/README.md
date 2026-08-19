# End-to-End Tests (Cypress)

Cypress end-to-end tests that run against the full application stack — front-end, back-end API, and MongoDB databases — all orchestrated through Docker Compose.

## Directory Structure

```
tests/
├── cypress.config.ts          # Cypress configuration (base URL, timeouts, file paths)
├── Dockerfile                  # Builds the Cypress runner image (based on cypress/included)
├── package.json               # Cypress dependency and npm scripts
└── cypress/
    ├── e2e/
    │   ├── editor.cy.ts        # Editor loading, typing, and JSON output tests
    │   └── comments.cy.ts      # Comment panel toggle, input, and button state tests
    ├── fixtures/
    │   └── sample-document.json  # Sample Tiptap document JSON for test data
    └── support/
        ├── e2e.ts              # Cypress support entry point
        └── commands.ts         # Custom commands (clearEditor, typeIntoEditor)
```

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed
- The env files in `env/` must be configured. Copy the example files and adjust as needed:
  ```bash
  cp env/client.env.example env/client.env
  cp env/server.env.example env/server.env
  cp env/mongo.env.example env/mongo.env
  cp env/test.env.example env/test.env
  ```

The test compose file mounts `mongo-init/test-mongo-init.js` into both MongoDB containers at `/docker-entrypoint-initdb.d/`. This script runs automatically on first initialization (when the data volumes are empty) and seeds:

- **`tiptap_editor.documents`** — 3 sample documents (including one with an inline comment mark)
- **`tiptap_editor.comments`** — 2 sample comments (one open, one closed)
- **`tiptap_rag.embeddings`** — 3 sample embedding records

> The seed script only runs on first initialization. If the data volumes already exist from a prior run, remove them to re-seed:
> ```bash
> docker compose -f docker-compose.test.yml down -v
> ```

The same seed data is replicated in `server/tests/conftest.py` for the pytest suite, so both test layers work against an identical dataset.

## Running the Tests

### Full Stack via Docker Compose (Recommended)

The test compose file spins up the entire application (client, server, both MongoDB instances) and a Cypress runner container, then executes the tests headlessly:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from e2e
```

This command:
- Builds all service images (client, server, e2e)
- Starts MongoDB, the API server, and the front-end
- Waits for the client and server to be ready
- Runs Cypress in headless mode against `http://client:5173`
- Exits with a non-zero code if any test fails

To view test artifacts (screenshots and videos) after a run, the `cypress-results` volume stores output. Mount it or copy it out:

```bash
docker compose -f docker-compose.test.yml run --rm e2e cat /e2e/cypress/results/report.html
```

### Local Cypress (Without Docker)

If you have Node.js installed and want to run Cypress locally against a running dev server:

```bash
cd tests
npm install
npm run open      # Opens the Cypress interactive test runner
npm run run       # Runs all tests headlessly
npm run e2e       # Runs tests headlessly with Electron browser
```

When running locally, set the `CYPRESS_BASE_URL` environment variable to point at your dev server:

```bash
CYPRESS_BASE_URL=http://localhost:5173 npm run run
```

## Configuration

The Cypress configuration lives in `cypress.config.ts`. Key settings:

| Setting | Default | Description |
| ------- | ------- | ----------- |
| `baseUrl` | `http://localhost:5173` (local) / `http://client:5173` (Docker) | URL Cypress visits to reach the app |
| `viewportWidth` | 1280 | Browser viewport width in pixels |
| `viewportHeight` | 720 | Browser viewport height in pixels |
| `defaultCommandTimeout` | 10000 | Max wait time for element commands (ms) |
| `specPattern` | `cypress/e2e/**/*.cy.ts` | Glob pattern for test files |

The `CYPRESS_BASE_URL` environment variable (set in `env/test.env`) overrides the default baseUrl when running in Docker.

## Writing New Tests

Create a new `.cy.ts` file in `cypress/e2e/`. Tests use the standard Cypress API:

```typescript
describe('My Feature', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('does something', () => {
    cy.get('.some-element').should('be.visible')
  })
})
```

Custom commands defined in `cypress/support/commands.ts`:

- `cy.clearEditor()` — Clears all text from the editor
- `cy.typeIntoEditor(text)` — Clicks into the editor and types the given text

## Test Files

| File | What it covers |
| ---- | -------------- |
| `editor.cy.ts` | Page loads, title visible, document UUID bar, editor renders, typing works, JSON output, save button |
| `comments.cy.ts` | Comment panel renders, input field, Add Comment button states, panel toggle, empty state |
