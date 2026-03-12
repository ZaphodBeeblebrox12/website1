# Community Platform - Phase 1

A Django-based community platform with Telegram authentication, role management, and audit logging.

## Features

- **Telegram Web Login**: Secure authentication using Telegram Login Widget with HMAC-SHA256 verification
- **Custom User Model**: UUID-based users with Telegram integration
- **Role Management**: Admin, Staff, and User roles with approval workflows
- **Ban System**: Comprehensive ban/unban functionality with audit trails
- **Audit Logging**: Complete audit trail for all system actions
- **System Settings**: Dynamic key-value configuration

## Tech Stack

- Django 5.x
- Django REST Framework
- SQLite (Phase 1) / PostgreSQL ready
- Celery + Redis (placeholder)
- pytest for testing
- ruff, black, mypy for quality

## Quick Start

### 1. Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings
# Add your TELEGRAM_BOT_TOKEN from @BotFather
```

### 2. Install Dependencies

```bash
make install
# or
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
make migrate
# or
python manage.py migrate
```

### 4. Create Superuser

```bash
make superuser
# or
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
make run
# or
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see the landing page.

## Telegram Login Setup

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Add to `.env`: `TELEGRAM_BOT_TOKEN=your_token`
4. Configure the domain in BotFather with `/setdomain`
5. Visit `/auth/telegram/` to test login

## API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/telegram/` | POST | Telegram authentication callback |
| `/api/auth/me/` | GET | Current user info (authenticated) |

### Admin Endpoints (Admin only)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/staff-approvals/` | GET | List pending staff approvals |
| `/api/admin/staff-approvals/action/` | POST | Approve/reject staff |
| `/api/admin/ban/` | POST | Ban a user |
| `/api/admin/unban/` | POST | Unban a user |

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run linting
make lint

# Run all checks
make check
```

## Docker

```bash
# Build and start containers
make docker-build
make docker-up

# Or use docker-compose directly
docker-compose up --build
```

## Project Structure

```
phase1-community_platform/
├── apps/
│   ├── accounts/          # User management, Telegram auth
│   ├── core/              # Landing pages, health checks
│   ├── system_settings/   # Dynamic configuration
│   └── audit/             # Audit logging
├── config/                # Django settings
├── integrations/          # External service integrations
│   └── telegram/          # Telegram auth utilities
├── services/              # Business logic services
├── tasks/                 # Celery tasks
├── tests/                 # Test suite
├── templates/             # HTML templates
├── static/                # Static files
├── requirements.txt       # Python dependencies
├── Makefile              # Common commands
├── Dockerfile            # Container build
├── docker-compose.yml    # Container orchestration
└── README.md             # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | Database connection | `sqlite:///db.sqlite3` |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | (required for auth) |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |

## License

MIT License
