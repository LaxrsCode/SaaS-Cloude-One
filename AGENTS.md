# AGENTS.md — SaaS-Cloude-One

## Dev commands

| `make` command | Actual command | Notes |
|---|---|---|
| `make install` | `python3 -m venv venv && ./venv/bin/pip install -r requirements.txt` | Run once; venv/ already exists |
| `make run` | `python manage.py runserver` | Port 8000 |
| `make migrate` | `makemigrations && migrate` | Always do both |
| `make seed` | `python manage.py seed_data` | Creates admin user + Free/Pro/Enterprise plans |
| `make lint` | `ruff check .` | |
| `make format` | `ruff format .` | Single quotes enforced |
| `make test` | `python manage.py test` | 31 tests across all apps |

Run in order: `lint -> test` (no typecheck step exists).

## Projects & entrypoints

- **apps/accounts/** — CustomUser model (email-only, no username), allauth adapter, Celery email tasks
- **apps/dashboard/** — Dashboard views, UserSettings model, subscription management, API key hashing, seed_data management command
- **apps/subscriptions/** — StripeCustomer/Subscription models, Stripe webhooks, checkout views
- **apps/landing/** — Public pages (home, features, pricing, robots.txt)
- **apps/tenants/** — Multi-tenant: Business, BusinessSettings, BusinessMember models + CRUD views
- **apps/bookings/** — Booking system: Service, Staff, StaffService, AvailabilitySlot, BookingBlock, Booking models + CRUD views
- **apps/clients/** — CRM: Client, ClientNote models + CRUD views
- **apps/notifications/** — Notification, EmailReminder models + list/mark-read views
- **core/** — Django settings, root URL conf, Celery app, WSGI/ASGI
- **templates/** — All Django templates (landing, account/allauth, dashboard, subscriptions, plus tenants/bookings/clients/notifications)

## Key quirks

- **Uses Celery** (`@shared_task`), **not** Django 6.0 native `@task` despite what README says. Redis via docker-compose.
- **LANGUAGE_CODE = 'es'** (Spanish default) with `es`/`en` both configured.
- **Ruff config**: `line-length = 120`, `quote-style = 'single'`, `select = [E, W, F, I, B, DJ]`.
- **Makefile uses `python3`** (not `python`). `make install` targets non-Windows paths (`./venv/bin/pip`). On Windows: activate `venv/Scripts/activate` instead.
- **`.env` contains live test credentials** (Stripe test keys, Gmail app password). Do not commit.
- **`.gitignore` excludes** `opencode.json`, `MODEL.md`, `.env`, `db.sqlite3`, `staticfiles/`.
- **CSP nonces** required for inline `<script>` tags: use `{{ csp_nonce }}`.

## Architecture notes

- `UserSettings` (OneToOneField to user) holds subscription state and notification prefs; created on first settings page access via `get_or_create`.
- `SubscriptionPlan` (dashboard) defines plans; `StripeCustomer` + `Subscription` (subscriptions) handle Stripe integration — two separate subscription systems exist: a local UserSettings-based one and a Stripe one.
- `CustomUser` uses `email` as `USERNAME_FIELD`, no username, `REQUIRED_FIELDS = []`.
- allauth email verification is **mandatory** (`ACCOUNT_EMAIL_VERIFICATION = 'mandatory'`). Emails go through Celery via `CustomAccountAdapter`.
- API keys in `UserSettings` are stored as `sha256` hashes; plaintext shown once via session.


## vexp <!-- vexp v2.1.4 -->

**MANDATORY: use `run_pipeline` - do NOT grep or glob the codebase.**
vexp returns pre-indexed, graph-ranked context in a single call.

### Workflow
1. `run_pipeline` with your task description - ALWAYS FIRST (replaces all other tools)
2. Make targeted changes based on the context returned
3. `run_pipeline` again only if you need more context

### Available MCP tools
- `run_pipeline` - **PRIMARY TOOL**. Runs capsule + impact + memory in 1 call.
  Auto-detects intent. Includes file content. Example: `run_pipeline({ "task": "fix auth bug" })`
- `get_skeleton` - compact file structure
- `index_status` - indexing status
- `expand_vexp_ref` - expand V-REF placeholders in v2 output

### Agentic search
- Do NOT use built-in file search, grep, or codebase indexing - always call `run_pipeline` first
- If you spawn sub-agents or background tasks, pass them the context from `run_pipeline`
  rather than letting them search the codebase independently

### Smart Features
Intent auto-detection, hybrid ranking, session memory, auto-expanding budget.

### Multi-Repo
`run_pipeline` auto-queries all indexed repos. Use `repos: ["alias"]` to scope. Run `index_status` to see aliases.
<!-- /vexp -->