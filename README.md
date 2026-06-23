```markdown
<div align="center">

# 🚀 IoT Hub Backend

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-5.6-brightgreen.svg?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg?logo=redis&logoColor=white)](https://redis.io/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3-orange.svg?logo=rabbitmq&logoColor=white)](https://www.rabbitmq.com/)
[![InfluxDB](https://img.shields.io/badge/InfluxDB-2.7-lightblue.svg?logo=influxdb&logoColor=white)](https://www.influxdata.com/)
[![Nginx](https://img.shields.io/badge/Nginx-1.25-green.svg?logo=nginx&logoColor=white)](https://nginx.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-26.0-cyan.svg?logo=gunicorn&logoColor=white)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/Docker-24-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

</div>

---

## 📋 Table of Contents

- [📖 About](#-about)
- [✨ Features](#-features)
- [🛠️ Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start](#-quick-start)
- [🧪 Testing](#-testing)
- [🐳 Docker Commands](#-docker-commands)
- [📝 Environment Variables](#-environment-variables)
- [📄 License](#-license)

---

## 📖 About

IoT Hub Backend is a production-ready Django-based platform for IoT applications featuring asynchronous task processing, real-time data handling, and time-series analytics.

---

## ✨ Features

- Modular Django settings (base / development / production)
- Async task processing with Celery and RabbitMQ
- Redis caching and broker support
- PostgreSQL as primary database
- InfluxDB for time-series data storage
- Docker-based development and production setup
- Nginx reverse proxy (production)
- Gunicorn WSGI server
- Environment-based configuration
- Security-focused configuration

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|----------|------------|---------|
| Framework | Django | 6.0 |
| API | Django REST Framework | 3.15 |
| Async Tasks | Celery | 5.6 |
| Message Broker | RabbitMQ | 3 |
| Cache | Redis | 7 |
| Database | PostgreSQL | 15 |
| Time-Series DB | InfluxDB | 2.7 |
| WSGI Server | Gunicorn | 26.0 |
| Reverse Proxy | Nginx | Alpine |
| Containerization | Docker | Latest |
| Package Manager | uv | Latest |

---

## 📁 Project Structure

```

.
├── core/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── celery.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── docker/
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── compose/
│   │   ├── docker-compose.dev.yml
│   │   ├── docker-compose.prod.yml
│   │   └── .env.prod.example
│   └── nginx/
│       └── nginx.conf
├── templates/
├── pyproject.toml
├── uv.lock
├── manage.py
└── README.md

````

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- uv (optional)

---

### Development

```bash
cd docker/compose
docker-compose -f docker-compose.dev.yml up --build
````

Access:

* Django: [http://localhost:8000](http://localhost:8000)
* RabbitMQ UI: [http://localhost:15672](http://localhost:15672)
* InfluxDB: [http://localhost:8086](http://localhost:8086)

---

### Production

```bash
cd docker/compose

cp .env.prod.example .env.prod
nano .env.prod

docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build
```

Access:

* Nginx: [http://localhost:80](http://localhost:80)

---

## 🧪 Testing

```bash
curl http://localhost:8000

docker exec -it compose-redis-1 redis-cli ping

docker exec -it compose-web-1 python manage.py shell -c "from core.celery import debug_task; debug_task.delay()"

curl http://localhost:8086/health
```

---

## 🐳 Docker Commands

### Development

```bash
docker-compose -f docker-compose.dev.yml up --build
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml down -v
```

### Production

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml down -v
```

### Utilities

```bash
docker logs compose-web-1 -f
docker exec -it compose-web-1 bash
docker exec -it compose-web-1 python manage.py migrate
docker exec -it compose-web-1 python manage.py createsuperuser
```

---

## 📝 Environment Variables

```env
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://iotuser:iotpass@db:5432/iotdb

RABBITMQ_USER=iotuser
RABBITMQ_PASS=iotpass

INFLUXDB_DB=iotdb
INFLUXDB_USER=iotuser
INFLUXDB_PASSWORD=iotpass
```

---

## 📄 License

Proprietary License

© 2026 All Rights Reserved.

Unauthorized use, copying, or distribution is strictly prohibited.

```
```
