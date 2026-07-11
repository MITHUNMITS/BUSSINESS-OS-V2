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
- Platform portal views require `is_platform_staff`.
- Public generated sites use canonical page paths like `/p/contact/`.

## Start Commands

```powershell
git pull
docker compose ps
docker compose run --rm web sh docker/entrypoint.sh python manage.py check
docker compose run --rm web sh docker/entrypoint.sh pytest
docker compose run --rm web sh docker/entrypoint.sh ruff check .
```

## Next Recommended Implementation

Implement the **Actor, Portal, And Support Access Foundation** before building more ecommerce screens.

Affected master-spec sections:

- Section 16: Security and multi-tenancy
- Section 25: Canonical domain and routing architecture
- Section 26: Actor, portal, and permission model
- Section 35: Privacy, security, legal, and audit
- Section 36: Support mode and superadmin organization workspace
- Section 40: Codex delivery protocol

Required work:

1. Add explicit platform role model or platform permission service separate from organization tenant roles.
2. Add support-session model with reason, scope, expiry, actor, target organization, and audit fields.
3. Add service methods to start/end support sessions.
4. Ensure support access does not silently impersonate business users.
5. Add tests for:
   - business member can access only own org admin.
   - platform staff can access platform portal.
   - non-platform user cannot access platform portal.
   - support session grants scoped organization access.
   - expired support session fails.
   - audit event is written for support access.
6. Update `08-verification-log.md`, `09-master-spec-compliance.md`, and `10-master-spec-gap-register.md`.

Do not build appointments, CRM, marketing, or advanced ecommerce UI yet. Keep the next slice small and production-grade.
