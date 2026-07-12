# Catalogue Collection Admin Lifecycle Completion

Date: 2026-07-12

## Scope

This note records the completed Business Admin catalogue collection lifecycle slice for master-spec sections 7, 11, 16, 27, 29, 39, and 40.

This is complete for the declared scope: tenant-safe collection list, create, detail, edit, archive, and restore workflows, plus basic offering membership assignment and synchronization.

It does not claim completion of advanced catalogue management such as drag/drop collection ordering, media/hero images, variants, add-ons, price lists, imports, exports, filtering, pagination, saved views, or bulk actions.

## Decision

Collections are generic catalogue curation records across facility types.

- The route remains canonical and generic under `/o/<organization_slug>/collections/...`.
- Collection forms adapt the membership label to the facility terminology, such as products, items, or services.
- Collection membership is managed through a basic multi-select in this slice.
- `CollectionItem` rows are synchronized from the selected offerings.
- Archive/restore use status transitions instead of hard deletion.
- Restore returns a collection as `draft`, so archived collections are not accidentally treated as active.

## Implemented

- Added facility-aware `CollectionAdminForm` and `CollectionFormSchema`.
- Added canonical Business Admin routes:
  - `/o/<organization_slug>/collections/`
  - `/o/<organization_slug>/collections/new/`
  - `/o/<organization_slug>/collections/<collection_id>/`
  - `/o/<organization_slug>/collections/<collection_id>/edit/`
  - `/o/<organization_slug>/collections/<collection_id>/archive/`
  - `/o/<organization_slug>/collections/<collection_id>/restore/`
- Added collection list, form, and detail templates.
- Added Collections to catalogue navigation and host route mapping.
- Added collection selectors for list/detail tenant scope.
- Added service-level `create_collection`, `update_collection`, `archive_collection`, and `restore_collection`.
- Added collection offering membership validation:
  - offering must belong to the same organization;
  - offering must be in the same facility scope when a facility exists;
  - archived/deleted offerings cannot be assigned.
- Added unique slug generation and duplicate slug validation.
- Added collection item synchronization.
- Added lifecycle audit events:
  - `catalogue.collection.created`
  - `catalogue.collection.updated`
  - `catalogue.collection.archived`
  - `catalogue.collection.restored`
- Added collection membership display on offering detail.

## Changed Code

- `business_os/apps/catalogue/forms.py`
- `business_os/apps/catalogue/services.py`
- `business_os/apps/catalogue/selectors.py`
- `business_os/apps/catalogue/module_config.py`
- `business_os/apps/core/module_registry.py`
- `business_os/apps/organizations/facility_profiles.py`
- `business_os/portals/admin_urls.py`
- `business_os/portals/views.py`
- `business_os/templates/admin_portal/collections.html`
- `business_os/templates/admin_portal/collection_form.html`
- `business_os/templates/admin_portal/collection_detail.html`
- `business_os/templates/admin_portal/product_detail.html`

Tests:

- `tests/integration/test_catalogue_collection_admin.py`

## Verification

Recorded in `08-verification-log.md`.

Relevant tests:

- Business Admin can create a collection with offering membership and audit event.
- Business Admin can edit collection metadata and synchronize membership.
- Duplicate collection slugs return validation errors and preserve existing data.
- Archive/restore are POST-only and audited.
- Business member cannot access another organization's collection lifecycle.
- Collection offering membership must stay in the same organization.
- Office collection form uses service terminology.
- Collections navigation route is real.
- Offering detail shows collection membership.

## Separate Future Features

- Drag/drop collection item ordering and collection-specific merchandising controls.
- Collection hero images/media and SEO metadata.
- Public collection pages and website section wiring.
- Variants, add-ons, price lists, import/export, filtering, pagination, saved views, and bulk actions.
