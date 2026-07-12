# Catalogue Offering Admin Lifecycle Completion

Date: 2026-07-12

## Scope

This note records the completed Business Admin catalogue offering lifecycle slice for master-spec sections 7, 11, 16, 27, 29, 39, and 40.

This is complete for the declared scope: tenant-safe detail, edit, archive, and restore workflows for the basic catalogue offering form introduced in `16-catalogue-offering-admin-create-completion.md`.

It does not claim completion of advanced catalogue management such as categories, collections, images, options, variants, add-ons, price lists, imports, exports, bulk actions, or public checkout screens.

## Decision

The basic offering lifecycle uses soft status transitions rather than hard deletion.

- Active and draft offerings remain visible in Business Admin.
- Archived offerings remain visible in Business Admin for recovery and audit.
- Archived offerings are hidden from public catalogue selectors.
- Restore returns an offering as `draft` with public visibility off, so archived offerings are not accidentally republished.
- Edit keeps the current default variant synchronized with the offering code and name for the basic catalogue flow.

## Implemented

- Added canonical Business Admin routes:
  - `/o/<organization_slug>/products/<offering_id>/`
  - `/o/<organization_slug>/products/<offering_id>/edit/`
  - `/o/<organization_slug>/products/<offering_id>/archive/`
  - `/o/<organization_slug>/products/<offering_id>/restore/`
- Added Business Admin offering detail page.
- Reused the facility-aware offering form for edit mode with initial values and duplicate checks that exclude the current offering/default variant.
- Added service-level `update_offering`, `archive_offering`, and `restore_offering`.
- Added selector for a single tenant-scoped admin offering.
- Added list-page row actions for view/edit.
- Added lifecycle audit events:
  - `catalogue.offering.updated`
  - `catalogue.offering.archived`
  - `catalogue.offering.restored`
- Added POST-only archive and restore actions.
- Added default-variant synchronization on edit.

## Changed Code

- `business_os/apps/catalogue/forms.py`
- `business_os/apps/catalogue/services.py`
- `business_os/apps/catalogue/selectors.py`
- `business_os/portals/admin_urls.py`
- `business_os/portals/views.py`
- `business_os/templates/admin_portal/products.html`
- `business_os/templates/admin_portal/product_form.html`
- `business_os/templates/admin_portal/product_detail.html`

Tests:

- `tests/integration/test_catalogue_admin_lifecycle.py`

## Verification

Recorded in `08-verification-log.md`.

Relevant tests:

- Business Admin can view and edit an offering.
- Edit updates the offering and synchronizes the default variant SKU/title.
- Edit writes an audit event with before/after payloads.
- Duplicate edit code returns a form error and preserves the original offering.
- Archive is POST-only, hides public visibility, and writes audit.
- Restore returns the offering as draft, keeps public visibility off, and writes audit.
- Business members cannot access another organization's offering lifecycle.
- Office facility edit uses service terminology.

## Separate Future Features

- Category, collection, image/media, option, variant, add-on, and price-list admin CRUD.
- Entitlement-gated advanced catalogue fields and submodules.
- Bulk import/export, filtering, pagination, saved views, and bulk actions.
- Public product/detail pages, cart pages, and checkout pages.
