# Verification Log

## 2026-07-11

Commands run:

- `docker compose config`: passed. Compose file renders valid service configuration.
- `rg "timezone\\.timedelta|datetime\\.utcnow|pass$" business_os tests`: passed with no matches.
- `npm install`: passed. Frontend dependencies installed.
- `npm run build:css`: passed. Tailwind and DaisyUI generated `businessos.generated.css`.
- `npm audit --audit-level=high`: passed with 0 vulnerabilities.
- `python manage.py check`: blocked because `python.exe` cannot be accessed by the system.
- `docker compose build web`: blocked because Docker Desktop's Linux engine is not running.

Current verification status:

- Static text-level checks completed.
- Frontend asset build completed.
- Runtime Django checks, migrations, and pytest are pending environment repair.

Required next verification once Python or Docker is available:

1. `docker compose build web`
2. `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations`
3. `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate`
4. `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`
5. `docker compose run --rm web sh docker/entrypoint.sh ruff check .`
6. `docker compose run --rm web sh docker/entrypoint.sh pytest`
7. `docker compose run --rm web sh docker/entrypoint.sh python manage.py seed_business_os`
8. `docker compose up`
9. Browser smoke test for Platform Superadmin, Business Admin, and public website.

## 2026-07-11 Docker Runtime Pass

Commands run:

- `docker compose build web`: completed; initial client timeout occurred after image build completed.
- `docker compose build worker`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations inventory commerce`: passed after replacing the unserializable inventory lambda default with a named function.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 5 tests.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py seed_business_os`: passed and rerun successfully.
- `docker compose up -d --no-build web worker`: passed after building both images.
- `Invoke-WebRequest http://localhost:8000/health/live`: passed, HTTP 200.
- `Invoke-WebRequest http://localhost:8000/health/database`: passed, HTTP 200.
- `Invoke-WebRequest http://localhost:8000/sites/nova-boutique/`: passed, HTTP 200.
- `Invoke-WebRequest http://localhost:8000/`: passed, HTTP 200 after adding a root redirect.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed after excluding migrations and formatting source files.
- `curl.exe -I -H "Host: nova-boutique.businessos.local" http://localhost:8000/`: passed, HTTP 200 with `X-BusinessOS-Surface: generated_site`.
- `curl.exe -i -H "Host: nova-boutique.businessos.local" http://localhost:8000/app/o/nova-boutique/dashboard/`: passed, HTTP 404 with public-host admin isolation.

Planning audit after domain miss:

- Reviewed all master prompt headings from sections 0 through 42.
- Added `10-master-spec-gap-register.md` for missed or under-specified requirements.
- Added `11-section-verification-gates.md` so every future task maps to affected master-spec sections before completion.
- Updated implementation steps, test strategy, release checklist, work status, planning index, and compliance snapshot.
- `rg -n "ecommerce-only|ecommerce-first Business OS|P0/P1|demo" docs/planning README.md`: checked for stale or misleading wording. Remaining matches are intentional warnings or scope clarifications.

Canonical host and portal guard implementation:

- Added route-surface allow-listing for local, marketing, business admin, platform admin, API, docs, status, generated site, custom site, preview, and unknown surfaces.
- Added canonical business-admin routes under `/o/<organization_slug>/...`.
- Added canonical platform routes for `/modules/` and `/organizations/`.
- Added platform-staff enforcement to platform portal views.
- Added canonical generated-site page routes under `/p/<page_slug>/`.
- Added domain routing integration tests. Targeted domain routing pytest passed with 12 tests.

Final verification for canonical host guard:

- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check`: passed with no unapplied migrations.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 17 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.
- `curl.exe -s -i -H "Host: api.businessos.local" http://localhost:8000/api/v1/health`: passed, HTTP 200 with `X-BusinessOS-Surface: api`.
- `curl.exe -I -H "Host: api.businessos.local" http://localhost:8000/o/nova-boutique/dashboard/`: passed, HTTP 404.
- `curl.exe -I -H "Host: nova-boutique.businessos.local" http://localhost:8000/sites/nova-boutique/`: passed, HTTP 404.
- `curl.exe -I -H "Host: platform.businessos.local" http://localhost:8000/organizations/`: passed, HTTP 403 for unauthenticated platform access.

Localhost subdomain support:

- Added localhost subdomain resolution for reserved platform surfaces and generated public websites.
- `app.localhost` resolves as `business_admin`.
- `platform.localhost` resolves as `platform_admin`.
- `api.localhost` resolves as `api`.
- `<site_slug>.localhost` resolves as `generated_site` when the website exists.
- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_domain_routing.py`: passed, 16 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check business_os/apps/websites/domain_services.py tests/integration/test_domain_routing.py`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 21 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.
- `curl.exe -s -i -H "Host: api.localhost" http://localhost:8000/api/v1/health`: passed, HTTP 200 with `X-BusinessOS-Surface: api`.
- `curl.exe -I -H "Host: platform.localhost" http://localhost:8000/organizations/`: passed, HTTP 403 with `X-BusinessOS-Surface: platform_admin`.
- `curl.exe -I -H "Host: nova-boutique.localhost" http://localhost:8000/`: passed, HTTP 200 with `X-BusinessOS-Surface: generated_site`.

Follow-up domain pass:

- Added `WebsiteDomain` lifecycle model.
- Added host resolution for generated and custom domains.
- Added public host route isolation.
- Added generated-host root rendering.
- Added domain routing tests. Pytest now passes with 9 tests.

Final verification after master-spec/domain review:

- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 9 tests.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check`: passed with no unapplied migrations.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py seed_business_os`: passed.
- `curl.exe -I http://localhost:8000/`: passed, HTTP 302 to `/sites/nova-boutique/`.
- `curl.exe -I -H "Host: nova-boutique.businessos.local" http://localhost:8000/`: passed, HTTP 200 with `X-BusinessOS-Surface: generated_site`.
- `curl.exe -i -H "Host: nova-boutique.businessos.local" http://localhost:8000/app/o/nova-boutique/dashboard/`: passed, HTTP 404 with public-host admin isolation.

Current running services:

- `db`: healthy on port 5432.
- `redis`: running on port 6379.
- `web`: running on port 8000.
- `worker`: running and connected to Redis.

Seeded data:

- Organizations: 1.
- Products: 3.
- Websites: 1.

## 2026-07-12 Actor, Portal, And Support Access Foundation

Affected master-spec sections:

- Section 16: Security and multi-tenancy.
- Section 25: Canonical domain and routing architecture.
- Section 26: Actor, portal, and permission model.
- Section 35: Privacy, security, legal, and audit.
- Section 36: Support mode and superadmin organization workspace.
- Section 40: Codex delivery protocol.

Implemented:

- Added `PlatformRole` and `PlatformRoleAssignment` as platform-global roles separate from organization tenant roles.
- Added explicit platform permission service checks for platform portal, organization view, and support-session permissions.
- Added `SupportSession` with actor, target organization, reason, ticket reference, read-only scope, expiry, end metadata, and audit linkage.
- Added support-session start/end/access service methods.
- Removed the shortcut that allowed platform staff to act as implicit members of every business organization.
- Added canonical platform organization workspace and support start/end routes under `/organizations/<organization_slug>/...`.
- Added visible support-mode banner and exit control on the platform organization workspace.
- Extended audit events with support session, support mode, IP address, user agent, and request context.
- Added implementation note `13-actor-portal-support-foundation.md`.

Commands run:

- `git pull --ff-only`: passed, already up to date.
- `docker compose ps`: passed; PostgreSQL healthy, Redis running.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations core`: passed and generated `core.0002_platformrole_supportsession_and_more`.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate`: passed; applied `core.0002_platformrole_supportsession_and_more`.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check`: passed with no unapplied migrations.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_domain_routing.py tests/integration/test_actor_support_access.py -q`: passed, 24 tests.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 29 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.

Test coverage added:

- Business member can access only their own organization admin.
- Platform staff with an explicit platform role can access the platform portal.
- Non-platform users cannot access the platform portal.
- Platform staff without a platform role cannot access the platform portal.
- Read-only support session grants scoped platform organization workspace access.
- Support session does not grant business-admin tenant access or create tenant membership.
- Expired support session fails and is cleared from the browser session.
- Support start/access/end audit events are written.

Known dev-only warning:

- Pytest still reports the existing local staticfiles warning: `No directory at: /app/staticfiles/`.

## 2026-07-12 Catalogue Offering Admin Lifecycle Completion

Affected master-spec sections:

- Section 7: Business Admin UI/UX.
- Section 11: Forms and controls, especially product/offering form.
- Section 16: Security and multi-tenancy.
- Section 27: Facility model and facility-aware adaptation.
- Section 29: Catalogue & Offerings.
- Section 39: Database governance.
- Section 40: Codex delivery protocol.

Implemented:

- Added tenant-scoped Business Admin offering detail, edit, archive, and restore routes.
- Reused the facility-aware offering form for edit mode with initial values and current-row duplicate exclusions.
- Added `update_offering`, `archive_offering`, and `restore_offering` service methods.
- Added detail template and row actions from the offerings list.
- Added POST-only archive/restore actions.
- Added default-variant synchronization on edit.
- Added audit events for update, archive, and restore.
- Added implementation note `17-catalogue-offering-admin-lifecycle-completion.md`.

Commands run:

- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_catalogue_admin_lifecycle.py -q`: passed, 6 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check business_os/apps/catalogue/forms.py business_os/apps/catalogue/services.py business_os/apps/catalogue/selectors.py business_os/portals/admin_urls.py business_os/portals/views.py tests/integration/test_catalogue_admin_lifecycle.py`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_catalogue_admin_create.py tests/integration/test_catalogue_admin_lifecycle.py -q`: passed, 12 tests.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check`: passed with no unapplied migrations.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 60 tests.

Test coverage added:

- Business Admin can view and edit an offering.
- Edit updates the offering and synchronizes the default variant.
- Edit writes an audit event with before/after payloads.
- Duplicate edit code returns a form error and preserves the original offering.
- Archive is POST-only, hides public visibility, and writes audit.
- Restore returns the offering as draft, keeps public visibility off, and writes audit.
- Business member cannot access another organization's offering lifecycle.
- Office facility edit uses service terms.

Known dev-only warning:

- Pytest still reports the existing local staticfiles warning: `No directory at: /app/staticfiles/`.

## 2026-07-12 Catalogue Offering Admin Create Completion

Affected master-spec sections:

- Section 7: Business Admin UI/UX.
- Section 11: Forms and controls, especially product/offering form.
- Section 16: Security and multi-tenancy.
- Section 27: Facility model and facility-aware adaptation.
- Section 29: Catalogue & Offerings.
- Section 39: Database governance.
- Section 40: Codex delivery protocol.

Implemented:

- Added facility-aware Business Admin offering form schema and form validation.
- Added canonical create route `/o/<organization_slug>/products/new/`.
- Added Business Admin create view/template for catalogue offerings.
- Added generic `create_offering` service while keeping `create_product` backwards compatible.
- Added tenant/facility scope validation, duplicate code/SKU checks, unique slug generation, status/visibility support, default variant creation, and create audit event.
- Added admin selector that includes drafts while public selectors remain active/visible-only.
- Replaced catalogue dead-anchor actions with canonical admin routes.
- Added implementation note `16-catalogue-offering-admin-create-completion.md`.

Commands run:

- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_catalogue_admin_create.py -q`: passed, 6 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check business_os/apps/catalogue/forms.py business_os/apps/catalogue/services.py business_os/apps/catalogue/selectors.py business_os/apps/core/module_registry.py business_os/portals/views.py tests/integration/test_catalogue_admin_create.py`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_facility_terminology.py tests/integration/test_catalogue_admin_create.py -q`: passed, 15 tests.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check`: passed with no unapplied migrations.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 54 tests.

Test coverage added:

- Business Admin can create an online product offering with a default variant and audit event.
- Business Admin product list shows draft offerings.
- Office facility create form uses service terms and creates a service offering.
- Duplicate code returns a form error and does not create a second offering.
- Business member cannot create an offering for another organization.
- Catalogue admin links are real canonical routes, not dead anchors.

Known dev-only warning:

- Pytest still reports the existing local staticfiles warning: `No directory at: /app/staticfiles/`.

## 2026-07-12 Facility Terminology Resolver Completion

Affected master-spec sections:

- Section 7: Business Admin UI/UX.
- Section 11: Forms and controls.
- Section 16: Security and multi-tenancy.
- Section 27: Facility model and facility-aware adaptation.
- Section 29: Module catalogue.
- Section 40: Codex delivery protocol.

Implemented:

- Added tenant-scoped facility terminology resolver for online, retail, warehouse, and office facility types.
- Added safe fallback to online-store terminology for unknown or unsupported facility types.
- Added cross-organization facility rejection.
- Wired facility terminology into Business Admin navigation labels.
- Wired facility terminology into dashboard labels and empty states.
- Wired facility terminology into product/order page titles and empty states.
- Added implementation note `15-facility-terminology-completion.md`.

Commands run:

- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_facility_terminology.py -q`: passed, 9 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check business_os/apps/organizations/facility_profiles.py business_os/apps/core/module_registry.py business_os/portals/views.py tests/integration/test_facility_terminology.py`: passed after wrapping one long function signature.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check`: passed with no unapplied migrations.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 48 tests.

Test coverage added:

- Online store terminology remains products/orders/inventory.
- Retail terminology resolves sales and stock labels.
- Warehouse terminology resolves items, fulfilment orders, and stock labels.
- Office terminology resolves services, work requests, and resources labels.
- Unknown facility type falls back safely to online-store terminology.
- Resolver rejects a facility from another organization.
- Business Admin dashboard/navigation/page labels use the resolved terminology.

Known dev-only warning:

- Pytest still reports the existing local staticfiles warning: `No directory at: /app/staticfiles/`.

## 2026-07-12 Business Admin And Platform Login Completion

Affected master-spec sections:

- Section 16: Security and multi-tenancy.
- Section 25: Canonical domain and routing architecture.
- Section 26: Actor, portal, and permission model.
- Section 35: Privacy, security, legal, and audit.
- Section 40: Codex delivery protocol.

Implemented:

- Added portal session service with explicit `business_admin`, `platform_admin`, and reserved `customer` scopes.
- Added Business Admin and Platform login/logout views.
- Added password reset routes and templates for privileged app/platform hosts.
- Added visible POST-only logout controls in Business Admin and Platform shells.
- Added login failure rate limiting by portal, username, and IP address.
- Added auth audit events for login success, login failure, login denied, login rate limiting, logout, and rejected cross-portal sessions.
- Added portal session boundary enforcement in request middleware.
- Added canonical `/login/` and `/logout/` routes plus legacy `/app/login/` and `/platform/login/` compatibility routes.
- Added host-guard allow-listing for canonical login/logout/password-reset paths on business and platform hosts.
- Added host-only session/CSRF cookie defaults.
- Added explicit canonical CSRF trusted origins in base settings and Docker Compose.
- Added implementation note `14-business-platform-login-session-completion.md`.

Commands run:

- `docker compose run --rm web sh docker/entrypoint.sh python manage.py check`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_portal_session_isolation.py tests/integration/test_domain_routing.py tests/integration/test_actor_support_access.py -q`: passed, 30 tests.
- `docker compose run --rm web sh docker/entrypoint.sh pytest tests/integration/test_portal_session_isolation.py -q`: passed, 10 tests.
- `docker compose run --rm web sh docker/entrypoint.sh ruff check .`: passed.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations --check --dry-run`: passed with no changes detected.
- `docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate --check`: passed with no unapplied migrations.
- `docker compose run --rm web sh docker/entrypoint.sh pytest`: passed, 39 tests.

Test coverage added:

- Business login marks a Business Admin session and redirects to the organization dashboard.
- Platform login marks a Platform session.
- External `next` redirects are rejected during login.
- Business sessions cannot be reused on the Platform host.
- Platform sessions cannot be reused on the Business Admin host.
- Leaked privileged sessions are cleared on public website hosts.
- Session and CSRF cookies remain host-scoped by default.
- CSRF trusted origins include explicit canonical app/platform/API hosts.
- Failed login is audited and rate-limited.
- Logout is POST-only, audited, and clears the portal session.
- Password reset sends email without revealing account existence.
- Password reset is blocked on public website hosts.

Known dev-only warning:

- Pytest still reports the existing local staticfiles warning: `No directory at: /app/staticfiles/`.
