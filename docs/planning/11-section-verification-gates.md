# Section Verification Gates

This document is the build-time checklist for `business_os_complete_master_codex_prompt_v3.md`.

For every implementation task:

1. List the affected master-spec sections.
2. Read those sections before coding.
3. Check this gate file for required proof.
4. Update implementation docs if scope changes.
5. Add or update tests for the relevant gate.
6. Run the smallest meaningful verification command.
7. Record evidence in `08-verification-log.md`.
8. Update `10-master-spec-gap-register.md` if a gap remains.

## Universal Completion Gate

A feature is production-ready for its declared scope only when all applicable items are true:

- Tenant scope is enforced in selectors, services, views, APIs, jobs, reports, exports, and files.
- Permission and entitlement checks are enforced outside the UI.
- Request context includes organization, facility where applicable, user, locale, currency, country, and host surface.
- Critical writes use transactions, constraints, and idempotency where duplicate actions are possible.
- State transitions are explicit and tested.
- Admin, superadmin, public website, and API surfaces are host-appropriate.
- UI includes loaded, empty, filtered-empty, loading, validation-error, permission-denied, entitlement-required, server-error, and success states where relevant.
- Tests cover happy path, denied path, cross-tenant path, and one important edge case.
- Docs and verification log are updated.

## Section Matrix

| Master section | Build-time verification gate |
|---|---|
| 0 Role and expectation | Confirm work is production-grade for declared scope and not a demo stub. |
| 1 Product principles | Verify modular all-in-one behavior, transparent pricing/cancellation, no dark patterns, and ecommerce-first wording only where appropriate. |
| 2 Recommended tech stack | Prefer Django built-ins, Django templates, HTMX, Alpine, Tailwind, DaisyUI, Lucide, PostgreSQL, Redis, Celery, pytest, Ruff, and planned observability/storage tools. Document justified deviations. |
| 3 High-level architecture | Confirm one codebase, one deployment, modular monolith boundaries, shared entitlement engine, no tenant-specific Django app installs. |
| 4 Generalized modules | Check whether touched work belongs to one of the 17 modules and whether future module extension points remain generic. |
| 5 Module registry | Register module metadata, capabilities, dependencies, navigation, website contributions, prices/limits references, and lifecycle hooks where applicable. |
| 6 Subscription/marketplace/entitlements | Verify purchase, customization, dependency resolution, bundle behavior, pricing snapshots, subscription statuses, activation, cancellation, and entitlement writes. |
| 7 Business Admin UI/UX | Verify layout, dynamic entitlement navigation, dashboard widgets, empty states, forms, responsive tables/cards, status badges, and accessible controls. |
| 8 Public website engine | Verify section composition, theme tokens, module-driven website behavior, editor/publish/preview/version flows, SEO, and domain rules. |
| 9 Superadmin UI | Verify platform-only access and controls for modules, prices, bundles, limits, subscriptions, invoices, payments, organizations, manual entitlements, support mode, and audit. |
| 10 Database design | Verify models, constraints, indexes, tenant keys, status fields, audit needs, migration safety, and clear deferral for future tables. |
| 11 Forms and controls | Verify form schema, validation, help text, errors, permissions, entitlement visibility, country/facility rules, and audit on sensitive changes. |
| 12 Availability/stock/reservation | Verify stock/capacity formula, holds, expiry, transaction locks, concurrent attempts, and no oversell/overbooking. |
| 13 Events/workflows | Verify domain event/outbox requirements, idempotent async work, retry behavior, notifications, and workflow audit. |
| 14 Search | Verify search scope, tenant/facility/entitlement filtering, indexes, ranking, empty states, and performance target. |
| 15 Files/media | Verify upload validation, storage visibility, private file access, derivatives, cleanup, CDN/cache behavior, and tenant-safe URLs. |
| 16 Security/multi-tenancy | Verify tenant isolation, object permissions, CSRF, session/cookie scope, rate limits, redirect allow-lists, file protection, and audit. |
| 17 API design | Verify `/api/v1` namespace, auth, permissions, pagination, errors, idempotency, typed contracts, and documentation. |
| 18 Testing | Verify unit, service, integration, browser, accessibility, security, and performance coverage for the changed area. |
| 19 Phased roadmap | Confirm the task belongs to the current phase or is intentionally preparing a future phase without overbuilding. |
| 20 Current dress customer config | Verify boutique seed/template data stays configuration, not hard-coded platform behavior. |
| 21 Project structure | Place code in the expected app/module boundary and avoid scattering business logic. |
| 22 Coding rules | Use services/selectors, explicit domain operations, constraints, transactions, and no silent invented business data. |
| 23 Acceptance criteria | Check route wiring, entitlement changes, admin/public behavior, checkout/payment/stock safety, and release proof. |
| 24 Final implementation instruction | Do not build every module at once; build foundation and current slice with extension points. |
| 25 Canonical domains | Verify host map, generated/custom/preview domains, admin/API/platform isolation, DNS/TLS lifecycle, canonical redirects, and cookie/session policy. |
| 26 Actor/portal/permission model | Verify anonymous/customer/business/platform/support actors, role separation, customer portal isolation, and audited support access. |
| 27 Facility model/adaptation | Verify facility type, terminology pack, default modules/forms/navigation/widgets/workflows/reports, and facility-aware schema resolution. |
| 28 Commercial hierarchy | Verify modules, submodules, capabilities, connectors, limits, usage meters, bundles, dependency types, and purchase rules. |
| 29 Module catalogue | Verify each touched module declares submodules, forms, UI, website contribution, purchase units, and dependencies. |
| 30 State machines | Verify product, booking, subscription, invoice, and website state transitions are explicit and invalid transitions are blocked. |
| 31 Billing edge cases | Verify trials, proration, coupons, taxes, usage, failed payments, retries, refunds, renewals, downgrade/cancel effects, and snapshots. |
| 32 Shipping/tax/fulfilment | Verify shipping zones/rules, tax labels/configuration, COD/manual/hosted payment compatibility, fulfilment statuses, and order tracking. |
| 33 Import/export/migration | Verify import preview, validation, mapping, rollback/audit, export permission, background processing, and data migration runbook. |
| 34 Observability/ops/backup/DR | Verify request IDs, logs, metrics, tracing, Sentry/App Insights plan, health checks, alerts, backups, restore tests, and runbooks. |
| 35 Privacy/security/legal/audit | Verify consent, terms, data export/delete, retention, audit events, support access policy, and sensitive-data handling. |
| 36 Support mode/superadmin workspace | Verify support-session reason, scope, expiry, approval where needed, audit, and no silent impersonation. |
| 37 Accessibility/localization/PWA/search | Verify WCAG 2.2 AA, keyboard, Axe, RTL, fonts, locale, currency/timezone, responsive behavior, PWA where included, and search UX. |
| 38 AI governance | Verify opt-in, data boundaries, explainability, human review for sensitive actions, audit, and no unsupported AI claims. |
| 39 Database governance | Verify migration safety, constraints, indexes, naming, data retention, backup impact, and no terminology-driven table names. |
| 40 Codex delivery protocol | Before final response, list affected modules, files changed, tests run, remaining gaps, and next safest task. |
| 41 Final product rule | Confirm Business OS remains one configurable platform controlled by entitlements. |
| 42 Final UI/UX technology decision | Verify DaisyUI primitive use, Business OS components, density modes, required UI states, marketplace UI rules, theme tokens, icons, fonts, and accessibility acceptance. |

## Minimum Verification Evidence By Work Type

| Work type | Required evidence |
|---|---|
| Model or migration | `makemigrations --check --dry-run`, `migrate --check`, model/service tests, migration review. |
| Service or selector | Unit/service tests for success, denied, cross-tenant, and edge case. |
| Route/view/API | Host/surface check, permission check, entitlement check, CSRF/auth behavior where relevant, integration test. |
| Admin UI | Screenshot/browser check, keyboard path, responsive check, empty/error/loading/success states. |
| Public website | Entitlement on/off checks, generated/custom host behavior, SEO/basic accessibility check, mobile check. |
| Checkout/payment/billing | Idempotency test, transaction test, duplicate submission test, payment-provider abstraction proof, no raw card storage. |
| Stock/availability | Concurrent reservation/booking test, expiry/release test, no oversell/overbooking test. |
| Import/export | Permission check, tenant scope check, malformed file test, preview/rollback/audit proof. |
| Operations/security | Health/logging/metrics evidence, security regression test, runbook update. |

## Current Known High-Priority Gates

1. Finish canonical host enforcement for `app`, `platform`, `api`, docs/status, custom domains, and previews.
2. Add platform-role versus tenant-role separation and audited support mode.
3. Add facility profile schema and terminology pack resolver before broadening beyond ecommerce.
4. Expand marketplace/subscription purchase flow with pricing snapshots and billing edge cases.
5. Add domain events/outbox before notifications, analytics, integrations, or workflow automation grow.
6. Add import/export, observability, privacy/legal, and database governance runbooks before production launch.
