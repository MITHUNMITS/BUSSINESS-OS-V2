# Work Status

## Current Status

Implementation started on 2026-07-11.

Current focus:

- Master-spec alignment.
- Domain and host routing foundation.
- Core domain models.
- Ecommerce-first service contracts inside the modular Business OS platform.

## Completed

- Master specification reviewed.
- Production plan agreed.
- `docs/planning/` created.
- Project folder structure created.
- Django settings, URL routing, ASGI/WSGI, Celery entrypoint, Docker Compose, Dockerfile, and CI baseline added.
- Core tenancy, marketplace, subscription, entitlement, website, catalogue, inventory, commerce, payment, and analytics models/services started.
- Business Admin, Platform Superadmin, public website templates, API router, seed command, and first tests added.
- Compose configuration validated.
- Static bad-pattern scan passed for known runtime mistakes.
- Frontend dependencies installed, Tailwind/DaisyUI CSS generated, and npm audit passed with 0 vulnerabilities.
- Docker backend runtime verified with Postgres, Redis, Django web, and Celery worker running.
- Migrations generated and applied through Docker.
- Seed command completed idempotently with one organization, one website, and three products.
- Django checks, Ruff checks, pytest, health endpoint, database health endpoint, root URL, and seeded public website smoke checks passed.
- Root URL now resolves in the running container instead of returning the older empty-path 404.
- `WebsiteDomain` lifecycle model added for generated, custom, and preview domains.
- Generated-host resolution added for `{site_slug}.<PLATFORM_ROOT_DOMAIN>`.
- Public website hosts now block Business Admin, Platform Superadmin, API, and Django admin route prefixes.
- Canonical host guard foundation added for app, platform, API, generated-site, custom-site, preview, docs, status, marketing, and local surfaces.
- Canonical app-host admin routes added under `/o/<organization_slug>/...`.
- Canonical platform-host routes added for `/modules/` and `/organizations/`.
- Platform portal views now require platform staff.
- Public generated-site page routes now use `/p/<page_slug>/`.
- Master-spec compliance snapshot added in `09-master-spec-compliance.md`.
- Master-spec gap register added in `10-master-spec-gap-register.md`.
- Section-by-section build verification gates added in `11-section-verification-gates.md`.
- Next-day continuation prompt added in `12-next-day-prompt.md`.

## In Progress

- Product/admin/marketplace workflows need the next production implementation pass.
- Full DNS ownership verification, TLS provisioning, CDN purge, preview-token authorization, and production cookie/session policy need the next domain lifecycle pass.
- Actor/session separation, facility adaptation, billing edge cases, import/export, observability/DR, privacy/legal/audit, support mode, AI governance, and database governance are now tracked as explicit planning gaps.
- Business workflows need iterative completion module by module.
- UI screens need Playwright and accessibility verification.

## Blockers

- Local `python.exe` remains inaccessible on this machine, but Docker now provides a working Python/Django runtime.
- Docker Compose is now configured with container-safe `db` and `redis` hostnames plus a PostgreSQL health check and wait script.

See `08-verification-log.md` for exact command results.
