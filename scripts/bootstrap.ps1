param(
    [switch]$UseDocker
)

if ($UseDocker) {
    docker compose up --build
    exit $LASTEXITCODE
}

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python manage.py migrate
python manage.py seed_business_os
python manage.py runserver

