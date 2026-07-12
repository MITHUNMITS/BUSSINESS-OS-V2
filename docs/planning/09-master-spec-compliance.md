# Master Spec Compliance Snapshot

This is a current-state verification against `business_os_complete_master_codex_prompt_v3.md`.

## Product Direction

Status: **aligned, partial implementation**

- Business OS is treated as a modular all-in-one platform, not an ecommerce-only project.
- Ecommerce is the first production slice because it is the first business opportunity.
- The codebase already separates core, organizations, marketplace, subscriptions, entitlements, websites, catalogue, inventory, commerce, payments, and analytics.
- Appointments, CRM expansion, workforce, communications, marketing, automation, documents, assets, AI, and industry packs remain future modules.

## Domain And Routing Architecture

Status: **foundation implemented, production edge cases pending**

Implemented:

- `PLATFORM_ROOT_DOMAIN` is configurable.
- Generated site host resolution supports `{site_slug}.{PLATFORM_ROOT_DOMAIN}`.
- `WebsiteDomain` model tracks generated/custom/preview domains with the required lifecycle states.
- Root generated-site requests render the public website.
- Localhost root redirects to the seeded public website for developer ergonomics.
- Public website hosts block `/app/`, `/platform/`, `/api/`, and `/django-admin/`.
- Canonical business-admin host routes support `/o/<organization_slug>/...`.
- Canonical platform host routes support `/modules/`, `/organizations/`, and platform organization workspaces.
- API host permits `/api/v1/` and rejects business-admin routes.
- Platform portal views require explicit platform role assignments.
- Public generated-site page routes support `/p/<page_slug>/`.
- Host resolution records the request surface in `request.host_surface` and response header `X-BusinessOS-Surface`.
- Business Admin and Platform login routes stamp authenticated sessions with explicit portal scopes.
- Business Admin and Platform login includes password reset, POST-only logout, rate limiting, redirect safety, and auth audit events.
- Middleware rejects or clears authenticated sessions that appear on the wrong portal surface.
- Session and CSRF cookies are host-scoped by default.
- CSRF trusted origins are explicit for canonical app, platform, and API hosts.

Verified:

- `Host: nova-boutique.businessos.local` + `/` returns HTTP 200.
- `Host: nova-boutique.businessos.local` + `/app/o/nova-boutique/dashboard/` returns HTTP 404.
- `localhost:8000` redirects to `/sites/nova-boutique/`.

Pending:

- DNS ownership verification workflow.
- TLS provisioning and SSL status automation.
- CDN purge and domain failure diagnostics.
- Preview token subdomain rendering.
- Full customer actor model and customer account login.
- Full docs/status host content and production marketing host content.

## Business Admin And Platform Login

Status: **implemented for declared privileged-portal scope**

Implemented:

- `business_admin`, `platform_admin`, and reserved `customer` portal session scopes exist.
- Business Admin login requires an active organization membership.
- Platform login requires explicit platform portal permission.
- Successful login marks the browser session with the matching portal scope.
- Password reset is available on privileged app/platform hosts.
- Logout is POST-only and exposed in the Business Admin and Platform shells.
- Failed login attempts are rate-limited.
- Login success, login failure, login denied, login rate limit, logout, and rejected cross-portal sessions are audited.
- Middleware rejects Business Admin sessions on Platform hosts and Platform sessions on Business Admin hosts.
- Leaked privileged sessions on public website hosts are cleared and treated as anonymous.
- External `next` redirects are rejected.
- Session and CSRF cookie domains default to host-only.
- Docker Compose includes explicit canonical CSRF trusted origins for local platform/app/API testing.

Verified:

- Business login redirects to the member organization dashboard.
- Platform login redirects to `/organizations/`.
- Cross-portal session reuse fails.
- Privileged sessions leaked to public website hosts are cleared.
- Cookie domains and CSRF trusted origins match the intended policy.
- Failed login is audited and rate-limited.
- Logout is POST-only, audited, and clears the portal session.
- Password reset sends email without revealing account existence.
- Password reset is blocked on public website hosts.

Separate future features:

- Customer actor model and customer account login.
- Separate customer identity rules and customer portal permissions.
- Rate limiting for support and API endpoints.
- MFA and approval flows for sensitive platform/support operations.
- Production CSP/security-header hardening.

## Actor, Portal, And Support Access

Status: **foundation implemented, full policy model pending**

Implemented:

- Platform roles and platform role assignments are separate from organization tenant roles.
- Platform permission service gates platform portal, organization view, and support-session access.
- Existing `is_platform_staff=True` users are backfilled into the system `platform-administrator` role.
- `is_platform_staff` alone is no longer enough to enter the platform portal.
- Business admin access is organization-membership-only.
- Support sessions track actor, target organization, reason, ticket reference, read-only scope, expiry, end metadata, and audit linkage.
- Support access uses the platform organization workspace and does not impersonate business users.
- Support-mode banner and exit control are visible in the platform organization workspace.
- Audit events can link to support sessions and record support mode, request ID, IP address, user agent, reason, actor, and organization.

Verified:

- Business member can access only their own organization admin.
- Platform staff with explicit role can access the platform portal.
- Non-platform users cannot access the platform portal.
- Platform staff without explicit role cannot access the platform portal.
- Scoped support session can access only the target organization workspace.
- Expired support session fails.
- Support access writes audit events.
- Support session does not grant business-admin access or create tenant membership.

Pending:

- Customer portal session isolation and full customer actor model.
- Facility-aware role dimensions.
- Platform role management UI.
- MFA and approval controls for sensitive support access.
- Controlled-write support workflow.
- Customer-facing support visibility rules beyond the current platform banner.
- Immutable audit retention, privacy export/delete, and legal hold workflows.

## Module And Entitlement Architecture

Status: **foundation implemented**

- Module registry exists and loads first-release module metadata.
- Organization entitlements exist and are enforced outside the UI for commerce actions and website page visibility.
- Marketplace, subscription, pricing, bundle, and capability models exist.
- Admin navigation is generated from registry/entitlement signals.

Pending:

- Self-serve marketplace checkout UI.
- Subscription payment/renewal/cancellation workflows.
- Full limit/quota enforcement across all modules.

## Facility-Aware Business OS Behavior

Status: **planned, model foundation present**

- Organization and facility models exist.
- Facility type exists for online, retail, warehouse, and office.
- Country/currency/timezone defaults support UAE and India.

Pending:

- Terminology packs by facility type.
- Facility-aware form schema resolver.
- Facility-specific default modules, dashboard widgets, workflows, reports, and website sections.

## Ecommerce First Slice

Status: **foundation implemented and verified**

- Catalogue, variants, inventory-lite, cart, checkout, order, payment intent, and stock reservation foundations exist.
- Stock reservation test passes.
- Seed creates one organization, one website, three products, inventory, COD payment provider, and entitlements.

Pending:

- Production-grade admin CRUD forms for products/categories/variants.
- Public cart and checkout pages.
- Shipping/tax rule UI and final checkout totals.
- Order management workflow UI.
- Real hosted payment gateway adapter.

## Verification Status

Passing:

- Docker Compose runtime with Postgres, Redis, web, and worker.
- Django system check.
- Migrations applied.
- `makemigrations --check --dry-run`.
- Ruff.
- Pytest: 39 tests.
- Health, database health, generated website, and host-isolation smoke checks.

Known dev-only warning:

- Celery runs as root inside the local container. This is acceptable for local development and must be fixed before production image hardening.

## Planning Gaps Added After Domain Review

Status: **gap register created**

The domain issue exposed that the plan needed a stricter master-spec review process. The following areas are now tracked in `10-master-spec-gap-register.md` and gated in `11-section-verification-gates.md`:

- Ethical marketplace UX and transparent billing.
- Canonical host, cookie, session, DNS, TLS, redirect, and preview-domain lifecycle.
- Actor, portal, tenant-role, platform-role, customer-portal, and support-mode separation.
- Facility-aware terminology, forms, navigation, workflows, reports, and website sections.
- Module, submodule, capability, connector, limit, usage-meter, and bundle hierarchy.
- State machines for product, booking, subscription, invoice, and website workflows.
- Billing edge cases, shipping/tax/fulfilment, import/export, search, files/media, events/outbox, observability, backup/DR, privacy/legal/audit, AI governance, database governance, localization, accessibility, and UI acceptance.

Rule going forward:

- Every build task must list affected master-spec sections, satisfy the relevant verification gates, and record proof in `08-verification-log.md`.
