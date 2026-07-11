# Implementation Steps

## Step 0: Master Spec Gate

Before implementing any feature:

1. Identify affected sections in `business_os_complete_master_codex_prompt_v3.md`.
2. Check `10-master-spec-gap-register.md` for known gaps in those areas.
3. Apply the relevant gates in `11-section-verification-gates.md`.
4. Write or update the smallest meaningful tests before marking the task complete.
5. Record verification evidence in `08-verification-log.md`.

## Step 1: Foundation

1. Create Django project settings, Docker services, static pipeline, and health endpoints.
2. Create custom user model before first migrations.
3. Create organization, facility, membership, role, permission, audit, and media foundations.
4. Add tenant-scoped managers and service-level permission boundaries.
5. Add tests proving tenant isolation and object-level access.
6. Add request-context verification for organization, facility, locale, currency, and host surface.
7. Add platform-role versus tenant-role separation before privileged superadmin workflows.

## Step 2: Marketplace And Entitlements

1. Create module, capability, dependency, price, bundle, and limit models.
2. Create subscription, subscription item, invoice, invoice line, and payment models.
3. Implement activation services that generate entitlements and initialize limits.
4. Build Platform Superadmin screens for module and organization configuration.
5. Build Business Admin marketplace screens for selecting modules, customizing add-ons, and renewing subscriptions.
6. Add pricing snapshots, dependency resolution, bundle discount, coupon, tax, renewal, cancellation, downgrade, and failed-payment behavior before paid launch.

## Step 3: Website And UI System

1. Create the Business OS component library using DaisyUI primitives.
2. Create website, page, section, theme, domain, preview, and publish models.
3. Render public websites from business data, theme tokens, template pack, and entitlements.
4. Add boutique/fashion template pack with catalogue and commerce capability slots.
5. Add accessibility, RTL, mobile, empty, loading, error, and entitlement-required states.
6. Complete canonical host routing, DNS verification, TLS status, redirects, previews, publish versions, and custom-domain audit before production custom domains.

## Step 4: Catalogue And Inventory-Lite

1. Create products, categories, collections, options, variants, images, prices, and SEO metadata.
2. Add admin CRUD forms and responsive tables/cards.
3. Add tenant-scoped public product listing and detail pages.
4. Create inventory item, level, movement, and reservation records.
5. Prevent overselling with database transactions and row locks.
6. Keep boutique content as template data only; generic catalogue/offering models must support future services, appointments, rentals, and reservations.

## Step 5: Commerce

1. Create cart, cart item, checkout, order, order item, and order status workflows.
2. Support guest checkout and optional customer account linkage.
3. Support shipping zones/rules for India and UAE.
4. Support COD/manual payment and provider-ready hosted payment intents.
5. Add idempotency keys for checkout and payment callbacks.
6. Add explicit order, invoice, payment, fulfilment, return/refund, and cancellation state-machine tests.

## Step 6: Hardening

1. Add search, analytics, import/export, observability, backup documentation, and release runbooks.
2. Add pytest, Playwright, accessibility, security, and performance checks.
3. Validate production settings, environment variables, secrets, and deployment checklist.
4. Run acceptance scenarios end to end.
5. Add privacy/legal workflows, audit review, support-mode controls, AI governance placeholders, database governance checklist, and disaster recovery verification.
