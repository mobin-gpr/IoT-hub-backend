# 🚀 IoT Hub Backend

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0.6-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-8.0-red?style=for-the-badge&logo=redis)
![EMQX](https://img.shields.io/badge/EMQX-5.x-teal?style=for-the-badge&logo=mqtt)

![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success.svg?style=for-the-badge)

</div>

---

## 📖 Overview

IoT Hub Backend is a robust Django REST API for managing IoT devices with MQTT authentication and authorization. It provides secure device management, topic-based access control (ACL), and seamless integration with EMQX MQTT broker.

## ✨ Features

- 🔐 **OTP-based Authentication** - Secure phone number authentication with SMS verification
- 📱 **Device Management** - Create, update, and delete IoT devices
- 🎯 **Topic-based ACL** - Fine-grained publish/subscribe permissions per device
- ⚡ **Redis Caching** - High-performance ACL caching for EMQX authorization
- 🔄 **Auto-sync** - Automatic Redis cache updates on device changes
- 🛠️ **Management Commands** - CLI tools for bulk ACL caching
- 📚 **OpenAPI Documentation** - Interactive Swagger/ReDoc API docs
- 🎨 **Beautiful Admin Panel** - Django admin with organized fieldsets

## 🏗️ Architecture

```
┌─────────────┐
│   Django    │
│   Backend   │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌─────────────┐  ┌─────────┐
│ PostgreSQL  │  │  Redis  │
│  (Devices)  │  │  (ACL)  │
└─────────────┘  └────┬────┘
                       │
                       ▼
                    ┌───────┐
                    │ EMQX  │
                    │ Broker│
                    └───────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 8.0+
- EMQX 5.x (optional, for MQTT)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ioT-hub-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/accounts/login/` | Send OTP to phone number |
| POST | `/api/v1/accounts/login/verify/` | Verify OTP and get token |
| POST | `/api/v1/accounts/token/refresh/` | Refresh access token |
| GET | `/api/v1/accounts/sessions/` | List user sessions |
| DELETE | `/api/v1/accounts/sessions/<id>/` | Revoke specific session |
| DELETE | `/api/v1/accounts/sessions/revoke-all/` | Revoke all sessions |

### Devices

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/devices/create` | Create new device | ✅ |
| GET | `/api/v1/devices/<uuid>/` | Get device details | ✅ |
| PUT/PATCH | `/api/v1/devices/<uuid>/` | Update device | ✅ |
| DELETE | `/api/v1/devices/<uuid>/` | Delete device | ✅ |
| POST | `/api/v1/devices/auth/` | Device auth for EMQX | ❌ |
| POST | `/api/v1/devices/cache-acls/` | Cache all ACLs in Redis | 🔒 |

## 🔧 Device Topics Format

When creating or updating a device, specify topics in JSON format:

```json
{
  "name": "My Device",
  "model": "ESP32",
  "username": "device_001",
  "topics": [
    {
      "name": "status",
      "actions": ["publish"]
    },
    {
      "name": "cmd",
      "actions": ["subscribe"]
    },
    {
      "name": "config",
      "actions": ["publish", "subscribe"]
    }
  ]
}
```

## 🗄️ Redis ACL Structure

Device ACLs are cached in Redis with the following structure:

```
Key: emqx:acl:{username}
Value: {
  "pub": ["status_uuid", "config_uuid"],
  "sub": ["cmd_uuid", "config_uuid"]
}
```

Topic names are formatted as: `{topic_name}_{device_uuid}`

## 🛠️ Management Commands

### Cache All Device ACLs

Use this command when Redis data is lost (e.g., power outage):

```bash
python manage.py cache_device_acls
```

This command reads all devices from PostgreSQL and caches their ACLs in Redis.

## 📚 Documentation

Interactive API documentation is available:

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **Admin Panel**: `http://localhost:8000/admin/`

## 🔐 Permissions

- **Device Creation**: Superusers and members of `device_creators` group
- **Device Management**: Superusers and members of `device_creators` group
- **ACL Caching**: Superusers only
- **Device Auth**: Public (for EMQX)

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 Environment Variables

Key environment variables (see `.env` for full list):

```env
DATABASE_URL=postgresql://user:password@localhost:5432/iot_hub
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=amqp://user:password@localhost:5672//
SMS_API_URL=https://api.sms.ir/v1/send
SMS_TEMPLATE_ID=523562
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m '✨feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django REST Framework
- EMQX Team
- Redis Team
- All contributors

---

<div align="center">

Made with ❤️ by IoT Hub Team

</div>
