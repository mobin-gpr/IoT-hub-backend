# EMQX MQTT Broker Setup

EMQX has been added to both development and production Docker Compose configurations.

## Ports Configuration

EMQX exposes the following ports:

- **1883**: MQTT TCP port (standard MQTT)
- **8883**: MQTT SSL port (secure MQTT)
- **8083**: MQTT WebSocket port
- **8084**: MQTT WebSocket SSL port
- **18083**: Dashboard HTTP port (web interface)

## Environment Variables

### Development (`docker-compose.dev.yml`)
- `EMQX_DASHBOARD__DEFAULT_USERNAME`: admin
- `EMQX_DASHBOARD__DEFAULT_PASSWORD`: public
- `EMQX_ALLOW_ANONYMOUS`: true
- `EMQX_LOG__LEVEL`: info

### Production (`docker-compose.prod.yml`)
- `EMQX_DASHBOARD__DEFAULT_USERNAME`: admin
- `EMQX_DASHBOARD__DEFAULT_PASSWORD`: ${EMQX_PASSWORD:-public} (from .env.prod)
- `EMQX_ALLOW_ANONYMOUS`: ${EMQX_ALLOW_ANONYMOUS:-false} (from .env.prod)
- `EMQX_LOG__LEVEL`: info

## .env.prod Configuration

Add the following variables to your `.env.prod` file:

```
# EMQX MQTT Broker
EMQX_PASSWORD=strong-password-here
EMQX_ALLOW_ANONYMOUS=false
```

## Service Dependencies

All Django services (web, celery_worker, celery_beat) now depend on EMQX, ensuring EMQX starts before the application services.

## Volumes

EMQX uses two persistent volumes:
- `emqx_data`: For EMQX data storage
- `emqx_log`: For EMQX logs

## Usage

### Development
```bash
docker-compose -f docker/compose/docker-compose.dev.yml up -d
```

### Production
```bash
docker-compose -f docker/compose/docker-compose.prod.yml up -d
```

## Accessing EMQX Dashboard

1. Open browser to: `http://localhost:18083`
2. Login with:
   - Username: `admin`
   - Password: `public` (development) or your configured password (production)

## Connecting to MQTT

Use any MQTT client to connect:
- Host: `localhost`
- Port: `1883` (TCP) or `8883` (SSL)
- Username: (optional if anonymous access is enabled)
- Password: (optional if anonymous access is enabled)

## Security Notes

For production:
1. Change the default password in `.env.prod`
2. Set `EMQX_ALLOW_ANONYMOUS=false` for better security
3. Consider using SSL ports (8883, 8084) for encrypted communication