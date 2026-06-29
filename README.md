# VPS Monitor

A server monitoring platform with automatic alerting and Telegram notifications.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup/` | Register a new user |
| POST | `/api/auth/login/` | Get JWT token |
| GET | `/api/auth/profile/` | Current user info |
| GET | `/api/servers/` | List servers |
| POST | `/api/servers/` | Register a server |
| GET | `/api/servers/<id>/` | Single server with metrics |
| POST | `/api/metrics/` | Submit metric (agent) |
| GET | `/api/metrics/alerts/` | View alerts |

Interactive docs at [/swagger/](http://localhost:8000/swagger/).

## Alert Rules

If CPU or RAM exceeds **90%**, an alert is created and a Telegram notification is sent.

## Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('demo', '', 'demo123')"
python manage.py runserver
```

## Agent (on monitored servers)

```bash
pip install requests psutil python-dotenv
```

Create `.env` on each server:

```env
API_URL=http://your-server:8000
SERVER_ID=1
API_USERNAME=demo
API_PASSWORD=demo123
```

Run:

```bash
python agents.py
```

The agent sends CPU, RAM, and disk metrics every 10 seconds.

## Telegram Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Stack

Django, DRF, PostgreSQL, SimpleJWT, drf-spectacular, python-telegram-bot (requests), psutil.
