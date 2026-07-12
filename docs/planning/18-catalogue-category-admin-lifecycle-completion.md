# Catalogue Category Admin Lifecycle Completion

Date: 2026-07-12

## Scope

This note records the completed Business Admin catalogue category lifecycle slice for master-spec sections 7, 11, 16, 27, 29, 39, and 40.

This is complete for the declared scope: tenant-safe category list, create, detail, edit, archive, and restore workflows, plus category assignment from the basic offering create/edit form.

It does not claim completion of advanced catalogue management such as collections, images, options, variants, add-ons, price lists, import/export, filtering, pagination, saved views, or bulk actions.

## Decision

Categories are facility-aware catalogue organization records, but database terminology remains generic.

- Online uses category terminology.
- Retail uses department terminology.
- Warehouse uses item group terminology.
- Office uses service area terminology.
- Category URLs stay canonical under `/o/<organization_slug>/categories/...`.
- Categories are soft-archived via status transitions instead of deleted.
- Restore returns a category as `draft`, so archived categories are not automatically treated as active.
- Offering create/edit now includes a category selector filtered by organization and facility.

## Implemented

- Added facility-aware `CategoryAdminForm` and `CategoryFormSchema`.
- Added canonical Business Admin routes:
  - `/o/<organization_slug>/categories/`
  - `/o/<organization_slug>/categories/new/`
  - `/o/<organization_slug>/categories/<category_id>/`
  - `/o/<organization_slug>/categories/<category_id>/edit/`
  - `/o/<organization_slug>/categories/<category_id>/archive/`
  - `/o/<organization_slug>/categories/<category_id>/restore/`
- Added category list, form, and detail templates.
- Added category selectors for list/detail tenant scope.
- Added service-level `create_category`, `update_category`, `archive_category`, and `restore_category`.
- Added category parent validation:
  - parent must belong to the same organization;
  - parent must be in the same facility scope when a facility exists;
  - parent cannot be archived/deleted;
  - category cannot be its own parent;
  - category cannot be moved under one of its descendants.
- Added unique slug generation and duplicate slug validation.
- Added lifecycle audit events:
  - `catalogue.category.created`
  - `catalogue.category.updated`
  - `catalogue.category.archived`
  - `catalogue.category.restored`
- Wired category selection into offering create/edit.

## Changed Code

- `business_os/apps/catalogue/forms.py`
- `business_os/apps/catalogue/services.py`
- `business_os/apps/catalogue/selectors.py`
- `business_os/portals/admin_urls.py`
- `business_os/portals/views.py`
- `business_os/templates/admin_portal/categories.html`
- `business_os/templates/admin_portal/category_form.html`
- `business_os/templates/admin_portal/category_detail.html`
- `business_os/templates/admin_portal/product_form.html`
- `business_os/templates/admin_portal/product_detail.html`

Tests:

- `tests/integration/test_catalogue_category_admin.py`

## Verification

Recorded in `08-verification-log.md`.

Relevant tests:

- Business Admin can create a category with auto slug and audit event.
- Facility terminology changes category UI labels, including office service areas.
- Business Admin can edit category parent/sort/status and audit changes.
- Duplicate slugs return validation errors and preserve existing data.
- Archive/restore are POST-only and audited.
- Business member cannot access another organization's category lifecycle.
- Parent category must belong to the same organization.
- Offering create/edit can assign a category.

## Separate Future Features

- Collections, image/media, option, variant, add-on, and price-list admin CRUD.
- Public category pages and SEO metadata.
- Filtering, pagination, saved views, column controls, export, import, and bulk actions.
- Entitlement-gated advanced catalogue fields and submodules.
