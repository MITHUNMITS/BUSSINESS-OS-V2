# Next Day Prompt - 2026-07-12

Use this prompt tomorrow if the current context is gone.

## Prompt

Continue the Business OS V2 project from the latest pushed `main` branch.

First read these files:

1. `business_os_complete_master_codex_prompt_v3.md`
2. `docs/planning/10-master-spec-gap-register.md`
3. `docs/planning/11-section-verification-gates.md`
4. `docs/planning/06-work-status.md`
5. `docs/planning/08-verification-log.md`

Do not treat this as an ecommerce-only project. Business OS is a modular all-in-one Django monolith; ecommerce is only the first production slice.

## Current Verified State

- Docker Compose runs PostgreSQL, Redis, Django web, and Celery worker.
- Root localhost route works and redirects to the seeded public website.
- Generated host routing works for `nova-boutique.businessos.local`.
- `WebsiteDomain` exists for generated, custom, and preview domain lifecycle foundation.
- Canonical host guard foundation is implemented:
  - local host keeps developer routes.
  - localhost subdomains map to the same canonical surfaces for local browser testing.
  - `app.localhost:8000`, `platform.localhost:8000`, `api.localhost:8000`, and `<site_slug>.localhost:8000` are supported.
  - `app.<PLATFORM_ROOT_DOMAIN>` uses canonical business admin routes like `/o/<org>/dashboard/`.
  - `platform.<PLATFORM_ROOT_DOMAIN>` uses canonical platform routes like `/organizations/`.
  - `api.<PLATFORM_ROOT_DOMAIN>` allows `/api/v1/`.
  - generated/custom public website hosts only expose public website/customer routes.
  - wrong-host admin/API/platform/public routes return 404.
- Platform portal views require explicit platform role assignments.
- Public generated sites use canonical page paths like `/p/contact/`.
- Explicit platform roles and platform role assignments exist separately from organization tenant roles.
- Read-only support-session foundation exists with reason, ticket reference, scope, expiry, actor, target organization, start/end services, visible support banner/exit, and audit events.
- Business Admin and Platform Admin login/session scope is complete:
  - Business Admin login requires active organization membership.
  - Platform login requires explicit platform portal permission.
  - sessions are stamped with portal scope.
  - cross-portal session reuse is rejected.
  - leaked privileged sessions on public hosts are cleared.
  - safe redirects, POST-only logout, password reset, login rate limiting, and auth audit events are implemented.
- Latest verification passed:
  - `python manage.py check`
  - `python manage.py makemigrations --check --dry-run`
  - `python manage.py migrate --check`
  - `pytest` with 39 tests
  - `ruff check .`

## Start Commands

```powershell
git pull
docker compose ps
docker compose run --rm web sh docker/entrypoint.sh python manage.py check
docker compose run --rm web sh docker/entrypoint.sh pytest
docker compose run --rm web sh docker/entrypoint.sh ruff check .
```

## Next Recommended Implementation

Implement the **Facility Profile And Terminology Resolver Completion** before building broad forms, module UI, appointments, CRM, or advanced ecommerce UI.

The goal is to make Business OS adapt labels, form hints, default dashboards, and navigation language by business/facility type so future forms do not hard-code ecommerce wording.

Affected master-spec sections:

- Section 7: Business Admin UI/UX
- Section 11: Forms and controls
- Section 16: Security and multi-tenancy
- Section 27: Facility model and facility-aware adaptation
- Section 29: Module catalogue
- Section 40: Codex delivery protocol

Required work:

1. Read master-spec Section 27 fully before coding.
2. Define the declared completion scope clearly so this slice can be marked complete, not just "foundation".
3. Add a facility profile/terminology resolver service that supports existing facility types without ecommerce-only assumptions.
4. Wire the resolver into Business Admin navigation/page labels where safe and scoped.
5. Add tests proving:
   - online store terminology remains correct for current ecommerce slice.
   - retail/warehouse/office terminology resolves differently where expected.
   - unknown or unsupported facility type falls back safely.
   - resolver is organization/facility scoped and does not leak tenant data.
6. Update `08-verification-log.md`, `09-master-spec-compliance.md`, `10-master-spec-gap-register.md`, and planning index/docs as needed.

Do not build appointments, CRM, marketing, broad module UI, or advanced ecommerce UI yet. Finish the declared facility terminology slice completely and production-grade.
