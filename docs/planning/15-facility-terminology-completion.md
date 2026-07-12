# Facility Terminology Resolver Completion

Date: 2026-07-12

## Scope

This note records the completed facility terminology resolver slice for master-spec sections 7, 11, 16, 27, 29, and 40.

This is complete for the declared scope: resolving and applying Business Admin terminology for the currently modeled facility types. The first facility-aware catalogue offering create form is recorded separately in `16-catalogue-offering-admin-create-completion.md`; remaining facility-aware forms, workflows, reports, website sections, and module defaults remain separate future slices.

## Decision

Facility terminology is a service-level profile, not a database naming change.

- Database table names and route names stay generic and stable.
- Existing `Facility.facility_type` drives the terminology pack.
- If an organization has no active facility, the resolver uses `organization.metadata["primary_facility_type"]` when valid.
- Unsupported or unknown facility types fall back to the online-store terminology pack.
- Passing a facility from another organization is rejected.

## Implemented Facility Types

- `online`
- `retail`
- `warehouse`
- `office`

Each pack resolves:

- core terms such as customer, offering, category, order, and inventory;
- Business Admin navigation labels;
- dashboard labels and empty states;
- product/category/order/inventory page titles.

## Changed Code

- `business_os/apps/organizations/facility_profiles.py`
- `business_os/apps/core/module_registry.py`
- `business_os/portals/views.py`
- `business_os/templates/admin_portal/dashboard.html`
- `business_os/templates/admin_portal/products.html`
- `business_os/templates/admin_portal/orders.html`

Tests:

- `tests/integration/test_facility_terminology.py`

## Verification

Recorded in `08-verification-log.md`.

Relevant tests:

- Online store terminology remains products/orders/inventory.
- Retail terminology resolves sales and stock labels.
- Warehouse terminology resolves items, fulfilment orders, and stock labels.
- Office terminology resolves services, work requests, and resources labels.
- Unsupported facility type falls back to online-store terms.
- Facility resolver rejects cross-organization facility input.
- Business Admin dashboard/navigation/page labels use the resolved terminology.

## Separate Future Features

- Facility-aware form schema resolver for remaining forms beyond catalogue offering creation.
- Facility-specific default modules and recommended modules.
- Facility-specific dashboard widget configuration beyond current label changes.
- Facility-specific workflow/report defaults.
- Facility-aware website section defaults.
- Facility-aware role dimensions and permissions.
