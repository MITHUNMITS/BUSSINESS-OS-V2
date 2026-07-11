# Production Release Checklist

## Code

- [ ] All required apps have migrations.
- [x] No mandatory business behavior is represented by placeholder TODOs.
- [x] Services use transactions for critical writes in the first ecommerce slice.
- [x] Tenant-owned base models and query helpers are in place.
- [x] Entitlements are enforced outside the UI for website visibility and commerce actions.
- [x] Payment provider foundation avoids raw card storage.

## UI

- [ ] Business Admin and Platform Superadmin share Business OS components.
- [ ] Public website templates use theme tokens.
- [ ] Mobile table/card modes are implemented.
- [ ] RTL layout is tested.
- [ ] Empty, error, loading, success, and entitlement-required states are present.

## Testing

- [ ] Unit tests pass.
- [ ] Service tests pass.
- [ ] Tenant isolation tests pass.
- [ ] Checkout and stock reservation tests pass.
- [ ] Playwright ecommerce path passes.
- [ ] Axe accessibility checks pass.

## Operations

- [x] Production settings use secure cookies and HTTPS.
- [x] Secrets are loaded from environment or secret manager reference.
- [ ] Database backups and restore runbook exist.
- [x] Health endpoints are present.
- [ ] Error reporting and request IDs are configured.
