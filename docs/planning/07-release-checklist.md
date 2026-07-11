# Production Release Checklist

## Code

- [ ] All required apps have migrations.
- [x] No mandatory business behavior is represented by placeholder TODOs.
- [x] Services use transactions for critical writes in the first ecommerce slice.
- [x] Tenant-owned base models and query helpers are in place.
- [x] Entitlements are enforced outside the UI for website visibility and commerce actions.
- [x] Payment provider foundation avoids raw card storage.
- [ ] Affected master-spec sections are listed for every completed task.
- [ ] `10-master-spec-gap-register.md` has no unresolved critical launch-scope gap.
- [ ] `11-section-verification-gates.md` is satisfied for each launch-scope section.
- [ ] Domain events/outbox exists before async notifications/integrations become critical.
- [ ] State machines block invalid transitions for product, subscription, invoice, website, order, payment, and fulfilment flows in launch scope.

## UI

- [ ] Business Admin and Platform Superadmin share Business OS components.
- [ ] Public website templates use theme tokens.
- [ ] Mobile table/card modes are implemented.
- [ ] RTL layout is tested.
- [ ] Empty, error, loading, success, and entitlement-required states are present.
- [ ] Marketplace/subscription screens show exact pricing, renewal, included capabilities, dependencies, cancellation effect, usage charges, and no dark patterns.
- [ ] Facility terminology and facility-aware form behavior are verified where facility-specific UI appears.
- [ ] Public website templates prove ecommerce is a template/module contribution, not the whole product identity.

## Testing

- [ ] Unit tests pass.
- [ ] Service tests pass.
- [ ] Tenant isolation tests pass.
- [ ] Checkout and stock reservation tests pass.
- [ ] Playwright ecommerce path passes.
- [ ] Axe accessibility checks pass.
- [ ] Domain/host isolation tests pass for local, generated, custom, app, platform, API, docs/status, and preview behavior in launch scope.
- [ ] Billing edge-case tests pass for paid launch scope.
- [ ] Import/export tests pass for launch-scope data.
- [ ] Security and privacy tests pass for support access, file access, consent/export/delete where implemented.

## Operations

- [x] Production settings use secure cookies and HTTPS.
- [x] Secrets are loaded from environment or secret manager reference.
- [ ] Database backups and restore runbook exist.
- [x] Health endpoints are present.
- [ ] Error reporting and request IDs are configured.
- [ ] Sentry/OpenTelemetry/Application Insights or equivalent production observability is configured.
- [ ] Backup restore has been tested, not just documented.
- [ ] Incident, deployment, rollback, DNS/domain, payment-webhook, and failed-job runbooks exist.
- [ ] Production cookie/session/CSRF domain policy is reviewed for generated and custom domains.
