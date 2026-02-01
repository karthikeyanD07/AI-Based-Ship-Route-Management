# Production Deployment Checklist

## Pre-Deployment

### Security
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Configure `CORS_ORIGINS` with production domains only
- [ ] Set `DEBUG=false` in production
- [ ] Review and restrict `ALLOWED_HOSTS`
- [ ] Enable HTTPS/TLS
- [ ] Configure database SSL connection
- [ ] Rotate all API keys
- [ ] Review security headers configuration

### Database
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Create database backup strategy
- [ ] Configure database connection pooling
- [ ] Set up database monitoring
- [ ] Test database failover/recovery

### Configuration
- [ ] All environment variables set in `.env`
- [ ] No hardcoded secrets
- [ ] Rate limits configured appropriately
- [ ] Log levels set to INFO/WARNING in production
- [ ] CORS origins restricted

### Testing
- [ ] All tests passing: `pytest`
- [ ] Security tests passing: `pytest tests/test_security.py`
- [ ] Load testing completed
- [ ] Penetration testing completed
- [ ] Manual smoke testing

## Deployment

### Infrastructure
- [ ] Docker images built and tested
- [ ] Kubernetes manifests reviewed (if using K8s)
- [ ] Load balancer configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up

### Application
- [ ] Health checks responding correctly
- [ ] Database migrations applied
- [ ] Initial admin user created
- [ ] API documentation accessible
- [ ] Metrics endpoint working
- [ ] WebSocket connections working

### Post-Deployment

### Verification
- [ ] All endpoints responding
- [ ] Authentication working
- [ ] Rate limiting active
- [ ] Audit logs being written
- [ ] Monitoring dashboards populated
- [ ] Alerts configured and tested

### Documentation
- [ ] Runbooks created
- [ ] Incident response procedures documented
- [ ] Backup/restore procedures tested
- [ ] Rollback procedure documented

## Ongoing Maintenance

### Regular Tasks
- [ ] Review audit logs weekly
- [ ] Monitor error rates
- [ ] Review security alerts
- [ ] Update dependencies monthly
- [ ] Test backup restoration quarterly
- [ ] Review and rotate credentials
- [ ] Performance tuning as needed

### Security
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] Penetration testing (annual)
- [ ] Review access logs
- [ ] Monitor for suspicious activity

## Emergency Procedures

### Incident Response
1. Check health endpoints
2. Review recent audit logs
3. Check error logs for patterns
4. Verify database connectivity
5. Check external service status
6. Review rate limit violations
7. Isolate affected systems if needed

### Rollback
1. Stop new deployments
2. Revert to previous version
3. Restore database if needed
4. Verify system health
5. Document incident

## Monitoring Alerts

Configure alerts for:
- High error rate (>5% of requests)
- High latency (p95 > 1s)
- Database connection failures
- Weather API failures
- WebSocket connection drops
- Disk space usage
- Memory usage
- CPU usage

## Success Criteria

✅ All health checks passing
✅ Zero critical security vulnerabilities
✅ Test coverage >80%
✅ Response times <500ms (p95)
✅ Error rate <1%
✅ Uptime >99.9%
✅ All audit logs being written
✅ Monitoring dashboards operational
