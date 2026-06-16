# Material Logistics

A Django-based logistics and materials management system for projects and subcontractors. Tracks project lifecycle, budgets, materials, procurement requests, stock usage, accounts, and contractor compliance.

## Features

- Project CRUD and lifecycle tracking
- Project subcontractor allocations and financials
- Contractor registry and per-year compliance matrix with file uploads
- Material inventory, requests, records, store management, and usage tracking
- Dashboard with aggregated metrics and charts

## Quickstart (development)

1. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows PowerShell
# or
source .venv/bin/activate # macOS / Linux
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure (optional)

- By default the project uses SQLite (`db.sqlite3`). To use another database, set `DATABASE_URL` in the environment.
- If you need file uploads in production, configure `MEDIA_ROOT` and a production storage backend.

4. Run migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server

```bash
python manage.py runserver
```

6. Open http://127.0.0.1:8000/ and log in.

## Key files & apps

- `material_logistics/settings.py` — project settings and installed apps
- `core/` — accounts, materials, requests, records, stores, usage, and dashboard logic
- `projects/` — `Project`, `ProjectAllocation`, lifecycle stages, and project views/templates
- `contractors/` — subcontractors, compliance requirements, and compliance tracking
- `templates/` — base layout and app templates (Tailwind + Chart.js used in UI)

## Running tests

```bash
python manage.py test
```

## Notes

- Uses Django 5.0 (see `requirements.txt`).
- File uploads are stored under paths defined in model `upload_to` values (e.g., `projects/`, `compliance_docs/`).

## Contribution

Create issues or pull requests with changes. For local development, follow the Quickstart steps above.

## License

Proprietary / internal (update as needed).
