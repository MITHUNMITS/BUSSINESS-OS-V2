# Test Strategy

Every test plan must reference the affected master-spec sections and the gate rows in `11-section-verification-gates.md`.

## Unit And Service Tests

- Tenant isolation for every tenant-owned selector and service.
- Entitlement checks for routes, actions, website sections, and APIs.
- Subscription activation, cancellation, renewal, and invoice snapshots.
- Billing edge cases: trials, prorations, coupons, taxes, renewals, failed payments, downgrades, cancellations, refunds, and usage snapshots.
- Product variants, categories, and visibility.
- Cart changes, stock reservation, checkout idempotency, and order creation.
- Payment intent creation, manual payment flow, and duplicate webhook protection.
- Facility-aware schema resolution, terminology packs, default modules, and permission visibility.
- Domain events/outbox creation and idempotent consumer behavior.
- Explicit state-machine transition tests for product, booking, subscription, invoice, website, order, payment, and fulfilment states where implemented.

## Integration Tests

- Business onboarding creates organization, facility, owner membership, website, and core entitlements.
- Marketplace activation provisions admin navigation and public website sections.
- Catalogue activation adds shop pages without commerce.
- Commerce activation adds cart, checkout, customer account, and order tracking.
- Module cancellation hides public features without deleting data.
- Canonical host routing separates marketing, business admin, platform superadmin, API, generated sites, custom domains, and previews.
- Customer portal sessions remain isolated from business-admin and platform sessions.
- Support-mode access is scoped, time-limited, and audited.
- Import/export respects tenant scope, permissions, entitlements, validation, and audit.

## Browser Tests

- Platform Superadmin configures a module and price.
- Business owner activates ecommerce module.
- Public visitor browses products, adds item to cart, and checks out as guest.
- Customer signs in and views order status.
- Mobile admin tables render as cards.
- Keyboard-only navigation reaches all critical actions.
- Marketplace UI shows exact price, included capabilities, dependencies, renewal date, cancellation effect, usage charges, and no preselected paid add-ons.
- Public website changes sections when catalogue, commerce, appointment, or reservation entitlements are toggled.
- RTL and mobile layouts pass for critical admin and public website paths.

## Security And Privacy Tests

- Cross-tenant object access is denied for every new selector, view, API, job, export, and file route.
- Public website hosts cannot reach Business Admin, Platform Superadmin, API, or Django admin routes.
- CSRF-sensitive flows reject invalid origins and tokens.
- Redirect targets are allow-listed.
- Uploaded files are validated and private media is access controlled.
- Consent, data export, deletion request, support access, and audit events are covered when implemented.

## Performance Targets

- Public product listing first response under 500 ms on warm cache for normal catalogue size.
- Checkout service avoids duplicate orders with idempotency keys.
- Product and order admin lists use pagination and indexed filters.
- Search, imports, exports, admin tables, public website rendering, and checkout have target query counts or response-time checks before production launch.
