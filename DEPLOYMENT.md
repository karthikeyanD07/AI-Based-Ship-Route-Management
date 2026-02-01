# Deployment Guide

## Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Check logs
docker-compose logs -f backend
```

## Production Deployment

### 1. Environment Setup

Create `.env` file:
```env
SECRET_KEY=<generate-strong-key>
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
OPENWEATHER_API_KEY=your-key
CORS_ORIGINS=https://yourdomain.com
DEBUG=false
```

### 2. Database Setup

```bash
# Create database
createdb ship_route_db

# Run migrations
alembic upgrade head

# Create admin user (via API or script)
```

### 3. Run Application

```bash
# Development
uvicorn backend.app.main:app --reload

# Production (with Gunicorn)
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/health/detailed
```

## Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (create if needed).

## CI/CD

GitHub Actions workflow is configured in `.github/workflows/ci.yml`.

## Monitoring

- Prometheus metrics: `/metrics`
- System metrics: `/metrics/system`
- Health checks: `/health`, `/health/detailed`

## Backup & Recovery

### Database Backup
```bash
pg_dump ship_route_db > backup.sql
```

### Restore
```bash
psql ship_route_db < backup.sql
```

## Security Checklist

- [ ] Change SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure CORS origins
- [ ] Set up firewall rules
- [ ] Enable database SSL
- [ ] Configure rate limits
- [ ] Set up monitoring alerts
- [ ] Review audit logs regularly
