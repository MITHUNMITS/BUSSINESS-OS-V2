# Test Strategy

## Unit And Service Tests

- Tenant isolation for every tenant-owned selector and service.
- Entitlement checks for routes, actions, website sections, and APIs.
- Subscription activation, cancellation, renewal, and invoice snapshots.
- Product variants, categories, and visibility.
- Cart changes, stock reservation, checkout idempotency, and order creation.
- Payment intent creation, manual payment flow, and duplicate webhook protection.

## Integration Tests

- Business onboarding creates organization, facility, owner membership, website, and core entitlements.
- Marketplace activation provisions admin navigation and public website sections.
- Catalogue activation adds shop pages without commerce.
- Commerce activation adds cart, checkout, customer account, and order tracking.
- Module cancellation hides public features without deleting data.

## Browser Tests

- Platform Superadmin configures a module and price.
- Business owner activates ecommerce module.
- Public visitor browses products, adds item to cart, and checks out as guest.
- Customer signs in and views order status.
- Mobile admin tables render as cards.
- Keyboard-only navigation reaches all critical actions.

## Performance Targets

- Public product listing first response under 500 ms on warm cache for normal catalogue size.
- Checkout service avoids duplicate orders with idempotency keys.
- Product and order admin lists use pagination and indexed filters.

