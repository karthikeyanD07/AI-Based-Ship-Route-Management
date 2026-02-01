# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Token expiration and refresh

### Input Validation
- Pydantic schema validation
- Input sanitization middleware
- SQL injection protection (ORM)
- XSS prevention

### Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HSTS)
- Content-Security-Policy
- Referrer-Policy

### Rate Limiting
- Per-user rate limiting
- Per-IP rate limiting
- Configurable limits

### Audit Logging
- All user actions logged
- IP address tracking
- Request ID correlation
- Compliance-ready

## Reporting a Vulnerability

Please report security vulnerabilities to: security@example.com

Do not open public issues for security vulnerabilities.

## Security Best Practices

1. **Always use HTTPS in production**
2. **Change default SECRET_KEY**
3. **Use strong passwords**
4. **Keep dependencies updated**
5. **Regular security audits**
6. **Monitor audit logs**
7. **Use environment variables for secrets**

## Penetration Testing

This system has been designed with security in mind:

- ✅ Input validation and sanitization
- ✅ SQL injection protection
- ✅ XSS prevention
- ✅ CSRF protection (via CORS)
- ✅ Authentication required for sensitive operations
- ✅ Rate limiting to prevent abuse
- ✅ Security headers
- ✅ Audit logging
- ✅ Error message sanitization

## Known Limitations

- WebSocket connections don't require authentication (by design for public tracking)
- Some endpoints allow anonymous access (documented)
- Rate limits are per-user/IP, not per-API-key
