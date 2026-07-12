# Next Day Prompt - 2026-07-13

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
- Facility terminology resolver is complete for the declared scope:
  - online, retail, warehouse, and office terminology profiles are implemented.
  - Business Admin navigation, dashboard labels, product/order page titles, and empty states use tenant/facility-scoped terminology.
  - unsupported facility types fall back safely.
- Catalogue Business Admin offering lifecycle is complete for the declared basic scope:
  - list, create, detail, edit, archive, and restore are implemented.
  - create/edit are facility-aware and tenant/facility-safe.
  - duplicate offering codes/default variant SKUs are rejected.
  - default variant creation/synchronization is implemented for simple offerings.
  - lifecycle audit events are written.
- Catalogue category lifecycle is complete for the declared basic scope:
  - list, create, detail, edit, archive, and restore are implemented.
  - parent hierarchy validation, tenant/facility scope checks, offering category assignment, and lifecycle audit events are implemented.
- Catalogue collection lifecycle is complete for the declared basic scope:
  - list, create, detail, edit, archive, and restore are implemented.
  - offering membership synchronization through `CollectionItem`, tenant/facility scope checks, navigation wiring, offering-detail membership display, and lifecycle audit events are implemented.
- Latest full verification passed:
  - `python manage.py check`
  - `python manage.py makemigrations --check --dry-run`
  - `python manage.py migrate --check`
  - `ruff check .`
  - `pytest` with 76 tests

## Start Commands

```powershell
git pull
docker compose ps
docker compose run --rm web sh docker/entrypoint.sh python manage.py check
docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run
docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check
docker compose run --rm web sh docker/entrypoint.sh pytest
docker compose run --rm web sh docker/entrypoint.sh ruff check .
```

## Next Recommended Implementation

Implement the **Catalogue Options And Variants Admin Lifecycle Completion** before public checkout expansion, public catalogue pages, media uploads, add-ons, price lists, imports/exports, appointments, CRM, marketing, or broad module UI.

The goal is to make configurable offerings production-manageable from Business Admin while preserving the simple-offering default variant behavior already used by checkout/cart foundations.

Affected master-spec sections:

- Section 7: Business Admin UI/UX
- Section 11: Forms and controls
- Section 12: Availability, stock, and reservation
- Section 16: Security and multi-tenancy
- Section 27: Facility model and facility-aware adaptation
- Section 29: Module catalogue and catalogue capabilities
- Section 30: State machines
- Section 39: Database governance
- Section 40: Codex delivery protocol

Required work:

1. Read the master-spec catalogue/form/module-capability sections around options, variants, SKUs, stock, and `catalogue.variants` before coding.
2. Define the declared completion scope clearly so this slice can be marked complete. Keep it to Business Admin options/variants management for existing offerings.
3. Add tenant/facility-safe Business Admin forms and services for:
   - `OptionDefinition`;
   - `OptionValue`;
   - `OfferingVariant`;
   - variant-to-option-value assignment.
4. Preserve the current simple offering behavior:
   - every offering still has a default variant;
   - changing an offering code/name keeps the default variant synchronized when the offering has no explicit configured variants;
   - adding explicit variants must not silently delete or corrupt the default variant.
5. Add canonical Business Admin routes/templates for option and variant workflows from the offering detail page.
6. Add service-level validation for:
   - same organization;
   - same facility scope where a facility exists;
   - duplicate option codes;
   - duplicate option values inside an option;
   - duplicate variant SKUs inside an organization;
   - variant option values belonging to the same organization/facility and not crossing unrelated options.
7. Add explicit audit events for option/variant create, update, archive/delete-safe transition where supported, and assignment changes.
8. Add tests proving:
   - business member can manage options/variants only for their own organization;
   - option/value create/edit rejects duplicates and cross-tenant data;
   - variant create/edit rejects duplicate SKUs and cross-tenant option values;
   - simple offering default variant behavior still works after offering edit;
   - explicit variants display on offering detail;
   - audit events are written.
9. Update `08-verification-log.md`, `09-master-spec-compliance.md`, `10-master-spec-gap-register.md`, and planning index/docs as needed.

Do not build media uploads, add-ons, price lists, imports/exports, public collection/category pages, cart/checkout UI, appointments, CRM, marketing, or broad module UI yet. Finish the declared options/variants admin lifecycle completely and production-grade.
