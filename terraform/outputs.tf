output "api_endpoint" {
  description = "Base URL for the HTTP API"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.api.function_name
}

output "frontend_bucket" {
  description = "S3 bucket hosting the frontend"
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain for the frontend"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = aws_cloudwatch_dashboard.api.dashboard_name
}

