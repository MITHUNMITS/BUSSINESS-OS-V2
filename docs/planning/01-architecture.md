# Business OS Ecommerce Architecture

## Goal

Business OS is a modular Django monolith. Every module remains deployed, and organization entitlements decide which admin routes, public website sections, APIs, background jobs, and reports are available.

The first production target is ecommerce for India and UAE businesses, with a boutique/fashion launch template that does not hard-code the domain to dresses.

## Architectural Rules

- Use one Django codebase and one deployment.
- Use PostgreSQL as the source of truth and Redis only for cache, locks, Celery, and short-lived holds.
- Resolve tenant context on every business-facing request.
- Enforce permissions and entitlements in services, selectors, views, APIs, jobs, and templates.
- Keep business logic out of templates, model methods, and view glue where practical.
- Use Django forms, auth, permissions, sessions, messages, migrations, i18n, transactions, constraints, and admin support.
- Keep module boundaries strong enough for future service extraction.

## First Release Slice

The first implementation slice includes:

- Core tenancy: organizations, facilities, memberships, roles, and audit events.
- Commercial control: marketplace modules, capabilities, prices, bundles, subscriptions, invoices, payments, and entitlements.
- Ecommerce foundation: catalogue, inventory-lite, cart, checkout, orders, shipping basics, and payment-provider abstraction.
- Website engine: entitlement-aware pages, sections, theme tokens, boutique/fashion template pack, catalogue pages, cart, checkout, and order tracking.
- Portals: custom Business Admin and Platform Superadmin, with Django admin available only for internal support.

## Country Defaults

Initial supported countries:

- UAE: AED, Asia/Dubai.
- India: INR, Asia/Kolkata.

The data model keeps currency, timezone, tax labels, and shipping zones configurable so additional countries can be added later.

