# Nexum IT Asset Management System

**Nexum Technologies** — Smart Asset Management. Connected Technology.

A customized IT Asset Management System for Nexum Technologies, built on the open-source
[Asseto Asset Management](https://github.com/VyrazuLabs/asseto-asset-management)
platform by [Vyrazu Labs](https://vyrazu.com).

This is an academic project demonstrating a professional IT asset tracking system.

---

## Features

- **Dashboard** — Live summary of total assets, assigned assets, licenses, vendors,
  locations, products, users, and total asset cost. Charts for asset status and utilization.
- **Asset Management** — Create, view, edit, delete, and assign assets with full details:
  asset tag, name, category, manufacturer, serial number, status, assigned employee,
  location, purchase information, and notes.
- **Employee / User Management** — View and manage user accounts and departments.
  See which assets are assigned to a particular user.
- **Vendor and Product Management** — Track vendors and product catalog.
- **Search and Filtering** — Global search across assets, products, and users.
  Filter by category, status, and assigned user.
- **Audit History** — Every change is logged automatically via django-simple-history.
- **Recycle Bin** — Soft-deleted records are recoverable from the Recycle Bin.
- **Role-Based Access Control** — Custom roles with granular permissions.
- **Two-Factor Authentication** — TOTP-based 2FA via any authenticator app.
- **Gate Pass Module** — Manage inward and outward asset movements.
- **Consumables Tracking** — Stock quantities, checkout history, low-stock alerts.
- **Support Tickets** — List and Kanban views with client portal access.
- **REST API** — Secure JWT-authenticated endpoints.
- **Bulk Upload** — CSV import for assets, vendors, locations, and more.

---

## Technology Stack

| Component       | Technology                           |
|-----------------|--------------------------------------|
| Language        | Python 3.11                          |
| Framework       | Django 5.2                           |
| Database        | PostgreSQL 15                        |
| Application server | Gunicorn 23                       |
| Reverse proxy   | Nginx (Alpine)                       |
| Frontend        | Django Templates + Bootstrap 5       |
| Interactivity   | HTMX + ApexCharts                    |
| Task queue      | Celery + Redis (optional)            |
| API             | Django REST Framework + SimpleJWT    |
| Audit history   | django-simple-history                |
| Containerization| Docker + Docker Compose              |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows or macOS)
- **WSL 2** must be installed on Windows (required by Docker Desktop)
  - Install with: `wsl --install` in an Administrator PowerShell, then restart
- At least 4 GB of free disk space for images and volumes

---

## Quick Start (Docker)

### 1. Clone or download the repository

```bash
git clone <your-repository-url>
cd asseto-asset-management-main
```

### 2. Configure the environment

Copy the example file and edit it:

```bash
# Windows PowerShell
Copy-Item .env.example .env
```

Edit `.env` and fill in at minimum:

```env
SECRET_KEY="your-secret-key-here"
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=nexum_itam
DB_USERNAME=nexum_user
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

A working `.env` for local development is already included in this repository for
convenience. **Replace it with your own secrets before deploying to any server.**

### 3. Build and start the containers

```bash
docker compose up -d --build
```

This command:
- Builds the Django application image
- Pulls PostgreSQL 15 and Nginx images
- Runs database migrations automatically
- Collects static files automatically
- Starts all three services in the background

### 4. Create an administrator account

```bash
docker compose exec -T -e ASSETO_ADMIN_PASSWORD="YourSecurePassword123" web python manage.py user_register \
  --fullname "Admin User" \
  --email admin@nexumtech.local \
  --username admin \
  --phone "+1234567890" \
  --company_name "Nexum Technologies" \
  --company_website "nexumtech.local"
```

Or use the Django superuser command for a basic admin:

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Open the application

Visit: **http://localhost:8080**

---

## Managing the Application

| Action | Command |
|--------|---------|
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| View logs | `docker compose logs -f` |
| Rebuild after code changes | `docker compose up -d --build` |
| Run migrations manually | `docker compose exec web python manage.py migrate` |
| Open Django shell | `docker compose exec web python manage.py shell` |

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Enable debug mode (`True`/`False`) | Yes |
| `DB_ENGINE` | Database backend | Yes |
| `DB_NAME` | Database name | Yes |
| `DB_USERNAME` | Database user | Yes |
| `DB_PASSWORD` | Database password | Yes |
| `DB_HOST` | Database host (use `db` in Docker) | Yes |
| `DB_PORT` | Database port (`5432` for PostgreSQL) | Yes |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | Yes |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | Yes |
| `EMAIL_HOST` | SMTP server host | Optional |
| `EMAIL_HOST_USER` | SMTP username | Optional |
| `EMAIL_HOST_PASSWORD` | SMTP password | Optional |
| `EMAIL_PORT` | SMTP port | Optional |
| `FIREBASE_APPLICATION_CREDENTIALS_FILE_DIRECTORY` | Firebase credentials file | Optional |

---

## Ports

| Service | Internal port | Host port |
|---------|--------------|-----------|
| Nginx (web access) | 80 | **8080** |
| Gunicorn (internal) | 8000 | Not exposed |
| PostgreSQL (internal) | 5432 | Not exposed |

The application is accessible at **http://localhost:8080**.

The database is not exposed externally for security.

---

## Troubleshooting

### Docker Desktop won't start on Windows
Ensure WSL 2 is installed: run `wsl --install` in an Administrator PowerShell
and restart your computer.

### "Docker Desktop is unable to start"
This usually means WSL 2 is missing or outdated. Run `wsl --update` after installing.

### Port 8080 is already in use
Edit `compose.yaml` and change `"8080:80"` to another port, e.g. `"9080:80"`.
Update `CSRF_TRUSTED_ORIGINS` in `.env` accordingly.

### Migrations fail on first start
If the database wasn't ready when the web container started, run:
```bash
docker compose restart web
```
The web container runs `manage.py migrate` on startup automatically.

### Static files not loading (404 on CSS/JS)
```bash
docker compose exec web python manage.py collectstatic --noinput
```

### View container logs
```bash
docker compose logs web      # Django application logs
docker compose logs db       # PostgreSQL logs
docker compose logs nginx    # Nginx logs
```

---

## Running Tests

```bash
docker compose exec web python manage.py test
docker compose exec web python manage.py test assets   # specific app
docker compose exec web python manage.py test -v 2     # verbose
```

---

## Project Structure

```
.
├── AssetManagement/       # Django project settings, URLs, WSGI/ASGI
├── assets/                # Asset models, views, forms
├── authentication/        # Custom user model, login, 2FA
├── audit/                 # Audit log functionality
├── clients/               # Client module
├── client_portal/         # Client self-service portal
├── configurations/        # Branding, localization, organization settings
├── consumables/           # Consumable stock tracking
├── custom_fields/         # Universal custom fields
├── dashboard/             # Dashboard views, locations, departments
├── gate_pass/             # Gate pass management
├── license/               # Software license tracking
├── notifications/         # Multi-channel notifications
├── products/              # Product catalog
├── recycle_bin/           # Soft-delete recovery
├── roles/                 # Role-based access control
├── support/               # Support ticket system
├── upload/                # Bulk CSV import
├── users/                 # User management views
├── vendors/               # Vendor management
├── templates/             # Django HTML templates
├── static/                # CSS, JS, images, fonts
├── compose.yaml           # Docker Compose configuration
├── Dockerfile             # Application container definition
├── nginx.conf             # Nginx reverse proxy configuration
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variable template
```

---

## Branding and Customization

This version has been customized for Nexum Technologies:

- **Color palette**: Deep Navy (`#14213D`), Teal (`#0F9D8A`), Light Blue (`#E8F1FA`)
- **Logo**: Nexum Technologies SVG logo (`static/images/nexum-logo.svg`)
- **Theme file**: `static/css/nexum-theme.css` — overrides the default color scheme
- **Templates updated**: `auth-layout.html`, `login.html`, `sidebar.html`,
  `header.html`, `footer.html`, `index.html`

The Configurations section (Admin → Configurations → Branding) allows uploading
a custom logo and favicon through the web interface at runtime.

---

## Known Limitations

- Celery task queue (for background jobs) is not started in this Docker configuration.
  Celery-dependent features (scheduled jobs, async notifications) will not function
  without adding a Redis service and Celery worker to `compose.yaml`.
- Firebase push notifications require a `firebase-credentials.json` file.
- The `setup.sh` script is designed for Linux servers and cannot be run on Windows.
  Use `compose.yaml` directly on Windows.
- Email delivery uses the Django console backend by default (printed to logs).
  Configure SMTP settings in `.env` for real email delivery.

---

## License and Attribution

This project is licensed under the
[Vyrazu License](LICENSE.md) (based on GPL v3), inherited from the original Asseto project.

**Original project:** [Asseto Asset Management](https://github.com/VyrazuLabs/asseto-asset-management)
by [Vyrazu Labs Pvt Ltd](https://vyrazu.com) — used and modified under the Vyrazu License.

This repository is a **customized academic project** based on Asseto.
The original Asseto code was written by Vyrazu Labs.
Modifications include Nexum Technologies branding, color theming, Docker configuration,
and this documentation.

Do not claim this as original work. Attribution to Vyrazu Labs is required per the license terms.

---

## Contact

This is an academic project for **Nexum Technologies** (fictional company).

For issues with the original Asseto platform, contact:
- [Vyrazu Labs GitHub](https://github.com/VyrazuLabs/asseto-asset-management)
- [info@vyrazu.com](mailto:info@vyrazu.com)
