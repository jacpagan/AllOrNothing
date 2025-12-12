variable "aws_region" {
  type        = string
  description = "AWS region to deploy to"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Project name prefix"
  default     = "objective-language-detector"
}

variable "stage" {
  type        = string
  description = "Deployment stage (e.g. dev, prod)"
  default     = "dev"
}

variable "lambda_memory_mb" {
  type        = number
  description = "Lambda memory size in MB"
  default     = 256
}

variable "lambda_timeout_seconds" {
  type        = number
  description = "Lambda timeout in seconds"
  default     = 5
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention days"
  default     = 14
}

variable "frontend_bucket_name" {
  type        = string
  description = "Optional custom bucket name for the frontend (must be globally unique). Leave empty to auto-generate."
  default     = ""
}

variable "allowed_cors_origins" {
  type        = list(string)
  description = "List of allowed CORS origins (use ['*'] for all, not recommended for production)"
  default     = ["*"]
}

variable "api_rate_limit" {
  type        = number
  description = "API Gateway rate limit (requests per second)"
  default     = 100
}

variable "api_burst_limit" {
  type        = number
  description = "API Gateway burst limit (concurrent requests)"
  default     = 200
}

variable "max_request_size_kb" {
  type        = number
  description = "Maximum request body size in KB"
  default     = 10
}

