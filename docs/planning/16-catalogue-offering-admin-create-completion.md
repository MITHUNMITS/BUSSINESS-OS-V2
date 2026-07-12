# Catalogue Offering Admin Create Completion

Date: 2026-07-12

## Scope

This note records the completed Business Admin catalogue offering create slice for master-spec sections 7, 11, 16, 27, 29, 39, and 40.

This is complete for the declared scope: a tenant-safe, facility-aware Business Admin create workflow for the first catalogue offering form. It does not claim completion of advanced catalogue management such as categories, collections, images, options, variants, price lists, imports, or bulk editing.

## Decision

Catalogue creation now uses a generic offering workflow rather than an ecommerce-only product assumption.

- The form schema is resolved from the organization's active facility profile.
- Online and retail facilities create product offerings.
- Warehouse facilities keep item terminology while using product-compatible catalogue records.
- Office facilities create service offerings.
- The database table names and route names remain stable and generic.
- Public catalogue visibility remains separate from the admin list, so drafts are visible in Business Admin but not public website selectors.

## Implemented

- Added a facility-aware `OfferingAdminForm` and `OfferingFormSchema`.
- Added canonical Business Admin route `/o/<organization_slug>/products/new/`.
- Added a Business Admin create view and form template.
- Added success messaging after create.
- Added audit event `catalogue.offering.created` with organization, facility, actor, target offering, status, offering type, visibility, and facility type.
- Hardened the catalogue service with:
  - generic `create_offering`;
  - backwards-compatible `create_product`;
  - organization/facility scope validation;
  - case-insensitive code and SKU duplicate checks;
  - unique slug generation for repeated names;
  - default variant creation;
  - support for draft/active status and website visibility.
- Added an admin selector that shows draft offerings while leaving public visible selectors unchanged.
- Replaced dead admin anchor links for catalogue actions with real canonical routes.

## Changed Code

- `business_os/apps/catalogue/forms.py`
- `business_os/apps/catalogue/services.py`
- `business_os/apps/catalogue/selectors.py`
- `business_os/apps/core/module_registry.py`
- `business_os/portals/admin_urls.py`
- `business_os/portals/views.py`
- `business_os/templates/admin_portal/base.html`
- `business_os/templates/admin_portal/dashboard.html`
- `business_os/templates/admin_portal/products.html`
- `business_os/templates/admin_portal/product_form.html`

Tests:

- `tests/integration/test_catalogue_admin_create.py`

## Verification

Recorded in `08-verification-log.md`.

Relevant tests:

- Business Admin can create an online-store product offering.
- Create flow writes a default variant.
- Create flow writes an audit event.
- Office facility create flow uses service terminology and creates a service offering.
- Draft offerings appear in Business Admin.
- Duplicate code validation returns a form error and does not create a second offering.
- Business members cannot create offerings for another organization.
- Catalogue admin links use real canonical routes instead of dead anchors.

## Separate Future Features

- Category, collection, image/media, option, variant, add-on, and price-list admin CRUD.
- Facility-aware form schema resolution for the remaining catalogue and non-catalogue forms.
- Entitlement-gated advanced catalogue fields and submodules.
- Bulk import/export, filtering, pagination, saved views, and bulk actions.
- Public cart and checkout pages.
