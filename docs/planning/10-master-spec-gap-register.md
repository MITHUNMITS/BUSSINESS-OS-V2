# Master Spec Gap Register

This register exists because the domain requirements were under-planned at first. Every future build task must check this file and `11-section-verification-gates.md` before implementation is marked complete.

Status meanings:

- Planned: requirement is documented but not built.
- Foundation: model/service boundary exists but production workflow is incomplete.
- Implemented: built, tested, and documented for the declared scope.

## Critical Planning Gaps Found

| Area | Missed or under-specified detail | Production risk | Required fix before marking related work complete | Status |
|---|---|---|---|---|
| Product identity | Docs could read as ecommerce-only instead of all-in-one Business OS. | Wrong architecture decisions, hard-coded shop assumptions. | Keep Business OS as the platform identity; ecommerce is only first slice. | Foundation |
| Ethical UX | Pricing, cancellation, trial, usage, renewal, and downgrade transparency were not explicit enough in workflow docs. | Dark-pattern risk and customer trust damage. | Every marketplace/subscription UI must show active items, exact price, renewal date, cancellation effect, included capabilities, and usage charges. | Planned |
| Canonical domains | Initial plan missed full host map and host isolation. | Admin/API leakage on public domains. | Enforce `app`, `platform`, `api`, docs/status, generated-site, custom-domain, and preview host behavior. | Foundation |
| Cookie/session isolation | Customer portal, business admin, and platform sessions were not planned separately. | Privileged session leakage across wildcard/custom domains. | Business/Admin and Platform login/session scope is implemented; finish customer actor login and production custom-domain policy. | Foundation |
| Domain lifecycle | DNS verification, TLS, canonical redirects, CDN purge, and failure diagnostics were missing. | Custom domains cannot be production-safe. | Build domain verification service, DNS instruction records, TLS status automation, redirect rules, and audit trail. | Foundation |
| Actor model | Platform roles, tenant roles, customer actors, support agents, and facility roles were not deeply modeled in planning. | Permission shortcuts and cross-role confusion. | Platform roles and read-only support sessions now exist; finish customer actors, facility roles, and the full permission matrix. | Foundation |
| Facility adaptation | Facility type was modeled, but terminology packs, default modules, forms, workflows, reports, and website sections were not planned enough. | Business OS becomes ecommerce-biased instead of facility-aware. | Add facility profile schema and resolver for labels, forms, navigation, dashboard widgets, reports, workflows, and defaults. | Foundation |
| Module hierarchy | Submodules, connectors, limits, usage meters, dependencies, conflicts, and bundle behavior were not explicit enough. | Entitlement engine becomes too small for real subscriptions. | Registry metadata must include modules, submodules, capabilities, connectors, dependency types, limits, usage meters, and website/admin contributions. | Foundation |
| Marketplace checkout | Customize, dependency resolution, bundle discount, coupon, tax, renewal, payment, and activation steps were not fully gated. | Incomplete subscription purchase flow. | Implement marketplace checkout as a service workflow with snapshots and idempotency. | Planned |
| Superadmin | Superadmin configuration was mentioned but not detailed enough for all platform controls. | Platform team cannot safely operate customers/modules/billing. | Expand custom superadmin for modules, prices, bundles, limits, entitlements, subscriptions, invoices, organization activation, support mode, and audit. | Foundation |
| Business Admin UI | Dynamic navigation, status system, forms, mobile tables, empty states, and dashboards need stronger acceptance gates. | Admin screens feel demo-like or inconsistent. | All admin pages must use Business OS components and required UI states. | Planned |
| Website engine | Editor, publishing, revisions, previews, section contracts, theme tokens, SEO, and module website contributions need deeper gating. | Websites cannot be safely customized or published. | Add publish state machine, preview route, version snapshots, section schema, and entitlement-driven website contributions. | Foundation |
| Database design | Many future table families were not tracked as intentional deferred modules. | Accidental schema drift or missing extension points. | Track all 17 module table families in roadmap; build only current-scope tables with clear future boundaries. | Planned |
| Forms and controls | Master spec lists many production forms, but planning only covered broad form behavior. | Missing admin workflows during build. | Each form must have schema, permissions, entitlement visibility, validation, audit, and tests. | Planned |
| Availability/holds | Appointment, multi-resource, reservation, and stock hold lifecycle were not fully planned. | Overselling/overbooking and race conditions. | Use transaction boundaries, row locks, expiry, idempotency, capacity formulas, and tests for concurrent attempts. | Foundation |
| Events/outbox | Internal domain events and transactional outbox were missing from planning. | Integrations, notifications, analytics, and async workflows become unreliable. | Add domain-event model/outbox, idempotent consumers, retry/dead-letter policy. | Planned |
| Search | Cross-module, entitlement-aware, facility-aware search was too light. | Poor admin/public discovery and data leakage risk. | Define search scopes, indexes, visibility checks, and performance targets. | Planned |
| Files/media | Storage validation, derivatives, private files, access control, and CDN behavior were under-planned. | Security and performance issues. | Add media policy for upload validation, virus-scan hook, private/public storage, derivatives, and tenant-safe access. | Planned |
| Security/multi-tenancy | Need stronger gate for every selector/view/API/job/export. | Tenant data leak. | Require tenant scope tests and object permission tests for each business feature. | Foundation |
| API design | API namespaces were planned, but versioning, auth, pagination, idempotency, errors, and docs need explicit gates. | API inconsistency and insecure external integrations. | Use Django Ninja contracts, versioned namespaces, typed errors, object permissions, rate limits, and idempotency where needed. | Planned |
| Test strategy | Tests existed but not every master-spec section had a verification requirement. | Features marked done without proof. | Use `11-section-verification-gates.md` for each build task. | Foundation |
| Seed/current customer | Boutique/dress seed can accidentally become product identity. | Platform hard-codes one business type. | Keep seed data as template/customer configuration only; generic domain names in models/services. | Foundation |
| State machines | Product, booking, subscription, invoice, and website states were not in planning docs deeply enough. | Invalid transitions and hard-to-debug workflows. | Implement explicit transition services and tests before workflow UI is complete. | Planned |
| Billing edge cases | Trials, proration, coupons, failed payments, taxes, refunds, downgrades, and cancellations were missing. | Incorrect invoices and support burden. | Add billing calculation snapshots and edge-case tests before paid launch. | Planned |
| Shipping/tax/fulfilment | Country rules, tax labels, shipping zones, fulfilment statuses, and COD/manual rules need detail. | Checkout totals wrong or operations incomplete. | Build configurable shipping/tax services and order fulfilment state transitions. | Planned |
| Import/export/migration | CSV import/export, mapping, validation, background jobs, and exports were under-planned. | Launch data migration becomes manual and risky. | Add import/export framework with preview, validation, rollback, audit, and entitlement checks. | Planned |
| Observability/DR | Backups, restore tests, Sentry, OpenTelemetry, App Insights, alerts, runbooks, and audit visibility were too light. | Production failures are hard to diagnose or recover. | Add operations runbooks, backup/restore verification, metrics, tracing, error reporting, and alert checks. | Planned |
| Privacy/legal/audit | Consent, data export/delete, retention, terms, support access, and audit trails were not fully planned. | Compliance and trust risk. | Support audit foundation exists; add privacy workflows, immutable audit retention, export/delete, and legal hold rules. | Foundation |
| Support mode | Audited platform support access to org workspace was missing. | Unsafe support impersonation. | Read-only support sessions now exist; add approval, MFA, controlled-write policy, customer visibility, and full audit lifecycle. | Foundation |
| Accessibility/localization/PWA | WCAG, RTL, fonts, language, currency/timezone, and PWA behavior need explicit verification. | Poor international launch quality. | Add Axe, keyboard, RTL, responsive, language, and font checks to release gates. | Planned |
| AI governance | AI features were listed but not controlled. | Unsafe automation and privacy risk later. | AI must require explicit customer opt-in, explainability, audit, human review for sensitive actions, and data-boundary controls. | Planned |
| Database governance | Migration safety, indexes, constraints, naming, soft deletion, and data retention were not explicit enough. | Schema instability and production migration risk. | Add migration checklist, constraint/index policy, and data-retention policy. | Planned |
| UI technology decision | DaisyUI role, component library, density modes, UI states, specialized libraries, icons, fonts, and visual direction need stronger gates. | Inconsistent or demo-looking UI. | All UI work must pass component-library, state, accessibility, responsiveness, and visual-density checks. | Planned |

## Gap Progress Notes

- 2026-07-11: Canonical host guard foundation implemented for business admin, platform admin, API, generated public sites, custom public sites, preview, docs, status, marketing, and local surfaces. Domain lifecycle remains foundation because DNS verification, TLS automation, CDN purge, preview authorization, and cookie/session policies are still pending.
- 2026-07-11: Platform portal views began requiring platform staff as an initial guardrail.
- 2026-07-12: Actor/support foundation implemented with explicit platform roles, platform permission checks, membership-only business admin access, read-only support sessions, support workspace banner/exit, and support audit events. Actor/support remains foundation because customer portal isolation, facility roles, MFA/approval, controlled-write support, and full privacy/audit lifecycle work are still pending.
- 2026-07-12: Business Admin and Platform login/session scope implemented with login/logout, password reset, explicit portal-scoped sessions, host-only cookie defaults, explicit canonical CSRF origins, cross-portal session rejection, public-host privileged-session clearing, login failure rate limiting, redirect safety, and auth audit events. Cookie/session isolation remains foundation only for separate future customer actor login and production custom-domain policy.

## Planning Fix Applied

- `01-architecture.md` now names Business OS as a modular all-in-one platform and ecommerce as the first slice.
- `09-master-spec-compliance.md` records current implementation status and pending domain work.
- `13-actor-portal-support-foundation.md` records the actor/support access decision and remaining scope.
- `14-business-platform-login-session-completion.md` records the completed Business Admin and Platform login/session scope.
- `11-section-verification-gates.md` now defines section-by-section build verification.
- `03-implementation-steps.md`, `05-test-strategy.md`, and `07-release-checklist.md` reference the gate process.

## Rule For Future Tasks

No task is complete until its affected master-spec sections are listed, the relevant gaps above are updated, and verification evidence is added to `08-verification-log.md`.
