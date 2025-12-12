# Security Features

This document outlines the security measures implemented in the Objective Language Detector deployment.

## Infrastructure Security

### API Gateway
- **Rate Limiting**: Configured with rate limit (100 req/s) and burst limit (200 concurrent)
- **Throttling**: Prevents API abuse and DDoS attacks
- **CORS**: Configurable allowed origins (default: all, but can be restricted)
- **Access Logging**: All API requests are logged to CloudWatch
- **HTTPS Only**: All traffic is encrypted in transit

### Lambda Function
- **Least Privilege IAM Role**: Only has permissions for CloudWatch Logs
- **Concurrent Execution Limits**: Limited to 10 concurrent executions to prevent resource exhaustion
- **X-Ray Tracing**: Enabled for security monitoring and debugging
- **Timeout Limits**: 5-second timeout prevents long-running requests
- **Memory Limits**: 256MB memory limit prevents resource abuse

### S3 Bucket
- **Public Access Blocked**: All public access is blocked
- **Encryption**: Server-side encryption (AES256) enabled
- **Versioning**: Enabled for data recovery and audit trails
- **Origin Access Control**: Only CloudFront can access the bucket
- **Bucket Policy**: Restricts access to CloudFront service principal only

### CloudFront
- **HTTPS Enforcement**: All traffic redirected to HTTPS
- **Security Headers**: 
  - Strict-Transport-Security (HSTS)
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Referrer-Policy: strict-origin-when-cross-origin
  - Content-Security-Policy
- **Origin Access Control**: Uses OAC (not OAI) for secure S3 access

## Application Security

### Input Validation
- **Text Length Limits**: Maximum 2000 characters per request
- **Empty Input Rejection**: Whitespace-only input is rejected
- **Type Validation**: Pydantic models ensure correct data types
- **Request Size Limits**: API Gateway limits request body size

### Error Handling
- **No Information Leakage**: Internal errors don't expose system details
- **Generic Error Messages**: 500 errors return generic messages
- **Validation Errors**: Clear but safe error messages for invalid input

### Security Headers
All API responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`

### API Documentation
- **Disabled in Production**: FastAPI docs and ReDoc are disabled
- **No Debug Endpoints**: No debug or admin endpoints exposed

## Data Security

### No Data Persistence
- **Stateless Service**: No user data is stored
- **No Logging of User Input**: User-provided text is not logged
- **Ephemeral Processing**: All processing happens in memory

### Logging
- **Access Logs**: API Gateway access logs (no request bodies)
- **Lambda Logs**: Function execution logs (no user data)
- **Log Retention**: 14 days (configurable)

## Deployment Security

### Build Process
- **Linux-Compatible Builds**: Uses Docker or platform flags for secure builds
- **No Secrets in Code**: No hardcoded credentials
- **Dependency Management**: Uses requirements.txt with version control

### Terraform
- **State Encryption**: Terraform state should be stored in encrypted S3 bucket
- **Least Privilege**: IAM roles follow least privilege principle
- **Resource Tagging**: All resources are tagged for security auditing

## Recommendations for Production

1. **CORS Configuration**: Update `allowed_cors_origins` to specific domains instead of `["*"]`
2. **API Keys**: Consider adding API key authentication for production
3. **WAF**: Add AWS WAF for additional protection against common attacks
4. **VPC**: Consider deploying Lambda in VPC for additional network isolation
5. **Secrets Management**: Use AWS Secrets Manager if secrets are needed
6. **Monitoring**: Set up CloudWatch Alarms for suspicious activity
7. **Backup**: Ensure Terraform state is backed up and encrypted

## Security Best Practices Followed

- ✅ Defense in depth (multiple security layers)
- ✅ Least privilege access
- ✅ Encryption at rest and in transit
- ✅ Input validation and sanitization
- ✅ Error handling without information leakage
- ✅ Security headers on all responses
- ✅ Rate limiting and throttling
- ✅ No public access to resources
- ✅ Audit logging enabled
- ✅ No data persistence

