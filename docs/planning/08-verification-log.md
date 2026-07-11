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
