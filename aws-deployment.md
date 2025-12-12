# AWS Showcase Deployment Guide

This guide deploys the Objective Language Detector FastAPI app to AWS using Lambda + API Gateway, with a static frontend on S3 + CloudFront.

## Prerequisites
- AWS CLI configured with credentials and a default region (or set `AWS_REGION`)
- Terraform >= 1.5
- Python 3.11+
- `zip` utility

## One-command deploy
```bash
bash deploy.sh
```

What it does:
1) Builds `build/lambda.zip` with app code + deps (`lambda_requirements.txt`)
2) `terraform init` + `terraform apply`
3) Syncs `frontend/` to the provisioned S3 bucket

Outputs printed at the end:
- API base URL (`api_endpoint`)
- S3 bucket name
- CloudFront domain for the frontend
- CloudWatch dashboard name

## Manual steps (if you prefer)
1) Package Lambda
   ```bash
   rm -rf build && mkdir -p build/package
   python -m pip install --upgrade -r lambda_requirements.txt -t build/package
   rsync -av --exclude '__pycache__' --exclude '.git' --exclude '.venv' \
     --exclude 'build' --exclude 'terraform' --exclude 'frontend' \
     vague_language_detector lambda_handler.py requirements.txt build/package/
   (cd build/package && zip -r ../lambda.zip .)
   ```

2) Deploy infra
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

3) Upload frontend
   ```bash
   FRONTEND_BUCKET=$(terraform output -raw frontend_bucket)
   aws s3 sync ../frontend "s3://${FRONTEND_BUCKET}" --delete
   ```

4) Test API
   ```bash
   API_ENDPOINT=$(terraform output -raw api_endpoint)
   curl -X POST "${API_ENDPOINT}/classify" \
     -H "Content-Type: application/json" \
     -d '{"text":"I always mess everything up."}'
   ```

5) Test frontend
   - Open `https://<cloudfront_domain>/`
   - Paste the API endpoint into the field and click **Analyze**

## Configuration
- Default values live in `terraform/variables.tf` (project name, stage, memory, timeout, log retention).
- To override, export env vars (Terraform standard), e.g.:
  ```bash
  export TF_VAR_stage=prod
  export TF_VAR_project_name=objective-language-detector
  ```
- Example env file: `env.example`

## Stress test against the deployed API
```bash
API_ENDPOINT=$(cd terraform && terraform output -raw api_endpoint)
python scripts/stress_test.py --url "${API_ENDPOINT}/classify" --concurrency 50 --duration 15
```

## Teardown
```bash
cd terraform
terraform destroy
```

After destroy, empty the S3 bucket first if Terraform reports it is not empty:
```bash
FRONTEND_BUCKET=$(terraform output -raw frontend_bucket)
aws s3 rm "s3://${FRONTEND_BUCKET}" --recursive
terraform destroy
```

## Notes
- CORS is enabled on the HTTP API for GET/POST/OPTIONS.
- Logging: Lambda logs go to `/aws/lambda/<name>` with retention set via `log_retention_days`.
- CloudWatch dashboard is created with basic Lambda and API Gateway metrics.

