# Business OS V2

Business OS is a modular Django monolith for all-in-one business operations:
websites, admin portals, marketplace subscriptions, entitlements, commerce,
appointments, inventory, CRM, workforce, payments, communications, marketing,
analytics, and future industry packs.

Ecommerce is the first production implementation slice, not the full product
identity.

## First Release Slice

- India and UAE ecommerce businesses.
- Boutique/fashion launch template without hard-coding the platform to dresses.
- Business Admin, Platform Superadmin, public website, catalogue, cart, checkout, orders, payment abstraction, inventory-lite, and analytics foundation.

## Local Setup

Python is currently not runnable through `python.exe` in this workspace. Once Python 3.13 is available, use:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
npm install
npm run build:css
python manage.py migrate
python manage.py seed_business_os
python manage.py runserver
```

Docker alternative:

```powershell
docker compose build web
docker compose run --rm web sh docker/entrypoint.sh python manage.py makemigrations
docker compose run --rm web sh docker/entrypoint.sh python manage.py migrate
docker compose run --rm web sh docker/entrypoint.sh python manage.py check
docker compose run --rm web sh docker/entrypoint.sh pytest
docker compose run --rm web sh docker/entrypoint.sh python manage.py seed_business_os
docker compose up
```

The Compose setup uses container service names:

- PostgreSQL: `db:5432`
- Redis: `redis:6379`
- Web: `localhost:8000`

Keep `.env.example` as the local-host reference. `docker-compose.yml` overrides `DATABASE_URL` and `REDIS_URL` inside containers so Django connects to the Compose services correctly.

## Frontend Assets

The committed Tailwind source is `business_os/static/css/businessos.css`.
The generated stylesheet is `business_os/static/css/businessos.generated.css`.

Rebuild it with:

```powershell
npm run build:css
```

## Planning Docs

Implementation plans and status are tracked in `docs/planning/`.
