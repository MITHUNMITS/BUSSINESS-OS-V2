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
- Platform portal views now require explicit platform role assignments.
- Public generated-site page routes now use `/p/<page_slug>/`.
- Platform roles and platform role assignments added separately from organization membership roles.
- Read-only support-session foundation added with reason, ticket reference, scope, expiry, actor, target organization, start/end services, and audit links.
- Platform organization workspace added for scoped support access without impersonating business users or granting tenant membership.
- Support access audit events now capture support mode, support session, reason, IP address, user agent, request ID, actor, and organization.
- Business Admin and Platform login routes added with explicit portal-scoped sessions.
- Portal session boundary middleware added so business, platform, and future customer sessions cannot be reused across the wrong host surfaces.
- Host-only session/CSRF cookie defaults and explicit canonical CSRF trusted origins documented in settings and Docker Compose.
- Business Admin and Platform login completed for the declared scope with password reset, POST-only logout, login failure rate limiting, redirect safety, and auth audit events.
- Facility terminology resolver completed for existing facility types: online, retail, warehouse, and office.
- Business Admin navigation, dashboard labels, product/order page titles, and empty states now resolve through the facility terminology profile.
- Facility-aware Business Admin catalogue offering create flow completed for the declared scope.
- Catalogue offering creation now validates tenant/facility scope, duplicate codes/SKUs, draft/active status, public visibility, default variant creation, canonical route wiring, and create audit events.
- Basic catalogue offering lifecycle completed for detail, edit, archive, and restore.
- Offering edit now validates tenant/facility scope, duplicate codes/SKUs, synchronizes the default variant, and writes update audit events.
- Offering archive/restore now use POST-only status transitions, hide archived/restored offerings from public visibility, and write lifecycle audit events.
- Basic catalogue category lifecycle completed for list, create, detail, edit, archive, and restore.
- Category forms now resolve terminology by facility type, validate parent scope/hierarchy, generate unique slugs, and write lifecycle audit events.
- Offering create/edit now includes tenant/facility-safe category assignment.
- Master-spec compliance snapshot added in `09-master-spec-compliance.md`.
- Master-spec gap register added in `10-master-spec-gap-register.md`.
- Section-by-section build verification gates added in `11-section-verification-gates.md`.
- Next-day continuation prompt added in `12-next-day-prompt.md`.
- Actor/support foundation implementation note added in `13-actor-portal-support-foundation.md`.
- Business/Admin and Platform login completion note added in `14-business-platform-login-session-completion.md`.
- Facility terminology resolver completion note added in `15-facility-terminology-completion.md`.
- Catalogue offering admin create completion note added in `16-catalogue-offering-admin-create-completion.md`.
- Catalogue offering admin lifecycle completion note added in `17-catalogue-offering-admin-lifecycle-completion.md`.
- Catalogue category admin lifecycle completion note added in `18-catalogue-category-admin-lifecycle-completion.md`.

## In Progress

- Catalogue collection, image/media, option, variant, add-on, price-list, import/export, filtering, pagination, and bulk-management workflows need future production implementation passes.
- Marketplace/subscription workflows need the next production implementation pass.
- Full DNS ownership verification, TLS provisioning, CDN purge, preview-token authorization, and production cookie/session policy need the next domain lifecycle pass.
- Customer actor login, remaining facility-aware form/workflow/report defaults, billing edge cases, import/export, observability/DR, privacy/legal/audit, AI governance, and database governance are tracked as explicit planning gaps.
- Support mode still needs MFA/approval controls, controlled-write workflow policy, customer-facing visibility rules, and stronger immutable audit/retention work.
- Business workflows need iterative completion module by module.
- UI screens need Playwright and accessibility verification.

## Blockers

- Local `python.exe` remains inaccessible on this machine, but Docker now provides a working Python/Django runtime.
- Docker Compose is now configured with container-safe `db` and `redis` hostnames plus a PostgreSQL health check and wait script.

See `08-verification-log.md` for exact command results.
