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
