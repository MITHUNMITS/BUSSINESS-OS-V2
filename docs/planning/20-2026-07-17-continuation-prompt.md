# Continuation Prompt - 2026-07-17

Use this prompt when continuing Business OS V2 development from the current working tree.

## Start Here

Read these files first and treat them as the current source of truth:

1. `business_os_complete_master_codex_prompt_v3.md`
2. `docs/planning/README.md`
3. `docs/planning/06-work-status.md`
4. `docs/planning/08-verification-log.md`
5. `docs/planning/09-master-spec-compliance.md`
6. `docs/planning/10-master-spec-gap-register.md`
7. `docs/planning/11-section-verification-gates.md`
8. `docs/planning/12-next-day-prompt.md`
9. Latest relevant completion notes in `docs/planning/13-*` through `19-*`

Business OS is a modular, multi-tenant, all-in-one Django monolith. Ecommerce is only the first production slice, and the boutique/fashion seed is only a template/customer configuration.

Do not hard-code boutique, fashion, dresses, products, ecommerce, or the current seed customer into generic platform architecture.

## Current Working Tree State

The latest verified completed slice remains:

- `19-catalogue-collection-admin-lifecycle-completion.md`

The next planned slice from `12-next-day-prompt.md` has been started:

- Catalogue options/variants admin lifecycle.

This work is currently staged in the working tree but is not complete under the project gate because Docker/Python verification was blocked on 2026-07-17.

Staged files include:

- `business_os/apps/catalogue/forms.py`
- `business_os/apps/catalogue/selectors.py`
- `business_os/apps/catalogue/services.py`
- `business_os/portals/admin_urls.py`
- `business_os/portals/views.py`
- `business_os/templates/admin_portal/product_detail.html`
- `business_os/templates/admin_portal/option_form.html`
- `business_os/templates/admin_portal/option_value_form.html`
- `business_os/templates/admin_portal/variant_form.html`
- `tests/integration/test_catalogue_variant_admin.py`
- Planning status updates in `06`, `08`, `09`, and `10`

Known extra untracked item:

- `NUL` appears in Git status but cannot be opened as a normal PowerShell path. Do not delete it unless the user explicitly asks and the filesystem behavior is understood.

## Current Staged Slice

Declared scope:

- Business Admin management of `OptionDefinition`
- Business Admin management of `OptionValue`
- Business Admin management of explicit `OfferingVariant`
- Variant-to-option-value assignment
- Preserve simple offering default-variant behavior

Implemented in the working tree:

- Facility-aware forms for options, values, and variants.
- Service-level create/update/archive/restore functions.
- Tenant/facility validation.
- Duplicate option code, option value, and variant SKU validation.
- One value per option validation for variants.
- `catalogue.variants` entitlement checks for new option/variant admin routes.
- Canonical routes under `/o/<organization_slug>/products/<offering_id>/...`.
- Offering detail UI sections for options and variants.
- Audit events for option, option value, and variant lifecycle actions.
- Tests for happy path, edit path, entitlement denial, cross-tenant denial, duplicate validation, same-option validation, archive/restore, and default-variant preservation.

Do not mark this slice complete until verification passes.

## Required First Action

Check the runtime:

```powershell
git status --short
docker compose ps
python --version
git diff --check
```

If Docker is available, run:

```powershell
docker compose run --rm web sh docker/entrypoint.sh python manage.py check
docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run
docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check
docker compose run --rm web sh docker/entrypoint.sh ruff check .
docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_catalogue_variant_admin.py -q
docker compose run --rm web sh docker/entrypoint.sh pytest
```

If verification fails, fix the staged options/variants slice before starting new feature work.

If Docker and Python are still unavailable, do not claim completion. Continue only with static review, documentation cleanup, or clearly bounded code inspection.

## Completion Rules

For every next action:

- Enforce organization scope.
- Enforce facility scope where applicable.
- Enforce permissions and entitlements outside the UI.
- Preserve Business Admin, Platform Admin, API, public website, preview, customer, and support boundaries.
- Preserve canonical host isolation.
- Do not grant platform users implicit tenant membership.
- Use transactions for critical writes.
- Use explicit status transitions.
- Write audit events for sensitive changes.
- Keep terminology generic and facility-aware.
- Update planning docs only with true verification evidence.

## Deferred Work

Do not jump to these until the staged options/variants slice is verified:

- Catalogue media uploads
- Add-ons
- Price lists
- Import/export
- Public category/collection/detail pages
- Cart and checkout UI
- Order management UI
- Marketplace/subscription purchase workflows
- Customer actor login
- Domain lifecycle automation
- Broad future modules such as CRM, appointments, marketing, AI, or workforce

## Next Slice After Verification

Once the options/variants admin lifecycle is verified and documented, choose the next vertical slice based on the end-to-end ecommerce launch path.

Likely candidates:

1. Catalogue media/image admin lifecycle.
2. Inventory-lite admin wiring for variants.
3. Public catalogue listing/detail pages for generated websites.

Pick one coherent slice, produce the required pre-implementation plan, and keep the change reviewable.
