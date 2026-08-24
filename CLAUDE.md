# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SillyTavern is an LLM frontend for power users: a Node.js Express server (`src/`) that serves a vanilla-JS single-page frontend (`public/`) and proxies requests to many LLM backends. AGPL-3.0 licensed. Requires Node >= 20; the whole codebase is ESM (`"type": "module"`).

## Commands

```bash
npm install               # install server deps (post-install also syncs default content)
npm run start             # start server (node server.js), serves http://127.0.0.1:8000
npm run debug             # start with --inspect
npm run start:no-csrf     # start with CSRF disabled (needed for some local testing)
npm run lint              # eslint over src/, public/, root *.js
npm run lint:fix
```

### Tests

Tests live in `tests/` with their own `package.json` — install and run from there:

```bash
cd tests
npm install
npm run test:unit         # Jest unit tests (*.test.js in tests/)
npm run test:e2e          # Playwright (*.e2e.js), expects a running server at http://127.0.0.1:8000
npm test                  # both
```

Run a single unit test file or case:

```bash
cd tests
node --experimental-vm-modules node_modules/jest/bin/jest.js --config jest.config.json util.test.js
node --experimental-vm-modules node_modules/jest/bin/jest.js --config jest.config.json -t "test name"
```

E2E tests (`tests/frontend/*.e2e.js`, mostly for the macro engine) require the server started first, e.g. with `npm run start:no-csrf` from the repo root.

## Architecture

### Server (`src/`)

- Boot chain: `server.js` → parses CLI args (`src/command-line.js`), sets `globalThis.DATA_ROOT` / `COMMAND_LINE_ARGS` → `src/server-main.js` (Express app, middleware, user storage init) → `src/server-startup.js` (route registration).
- **API endpoints**: each file in `src/endpoints/` exports a `router`, mounted in `src/server-startup.js` under `/api/<name>`. LLM backend proxies live in `src/endpoints/backends/` (`chat-completions.js` for OpenAI-compatible APIs, `kobold.js`, `text-completions.js`).
- **Multi-user system**: `src/users.js` — per-user data directories under `data/`, cookie sessions, optional login. Most endpoints operate on `request.user.directories` rather than global paths.
- **Config**: `config.yaml` at repo root (created on first run from `default/config.yaml`); parsing in `src/config-init.js`. User data root defaults to `data/` (overridable via `--dataRoot`).
- **Server plugins**: `plugins/` directory, loaded by `src/plugin-loader.js`; managed with `npm run plugins:install` / `plugins:update`.

### Frontend (`public/`)

- No build step for app code: `public/index.html` loads `public/script.js` (the huge main module) and modules in `public/scripts/` directly as ES modules. jQuery is used throughout.
- The only bundled artifact is `public/lib.js` (third-party libs), webpacked at runtime by a serve middleware (`src/middleware/webpack-serve.js`) — don't import npm packages directly in frontend code; go through `lib.js`.
- **Extensions**: built-in extensions live in `public/scripts/extensions/<name>/`; user-installed ones go to `public/scripts/extensions/third-party/` (gitignored). Extension docs: https://docs.sillytavern.app/for-contributors/writing-extensions/
- Frontend/backend API-specific settings pairs: e.g. `public/scripts/openai.js` (Chat Completion UIs), `nai-settings.js`, `kai-settings.js` correspond to their server-side endpoint counterparts.

### Data

- `data/` — runtime user data (characters, chats, settings); never commit.
- `default/` — templates for config and initial content, synced by `src/server-init.js` / content-manager.

## Contribution Rules (from CONTRIBUTING.md)

- **Target branch: `staging`** for 99% of PRs. `release` only for README updates, GitHub Actions, or critical hotfixes.
- Keep PRs small: soft limit ~200 changed lines; split larger work.
- English only for commit messages, PR descriptions, and code comments (localization files excepted).
- Run `npm run lint` before committing; follow existing naming conventions.
