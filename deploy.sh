#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
PACKAGE_DIR="${BUILD_DIR}/package"
TERRAFORM_DIR="${ROOT_DIR}/terraform"
FRONTEND_DIR="${ROOT_DIR}/frontend"
ZIP_PATH="${BUILD_DIR}/lambda.zip"

echo "==> Cleaning build directory"
rm -rf "${BUILD_DIR}"
mkdir -p "${PACKAGE_DIR}"

echo "==> Installing Lambda dependencies into package/ (Linux-compatible)"
# Use Docker to build Linux-compatible packages if available, otherwise try platform flags
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "   Using Docker to build Linux-compatible package..."
    if docker run --rm -v "${ROOT_DIR}:/var/task" \
        public.ecr.aws/lambda/python:3.11 \
        /bin/bash -c "pip install -r /var/task/lambda_requirements.txt -t /var/task/build/package && chmod -R 755 /var/task/build/package" 2>/dev/null; then
        echo "   Docker build successful"
    else
        echo "   Docker build failed, falling back to cross-platform install..."
        python3 -m pip install --upgrade --platform manylinux2014_x86_64 --only-binary=:all: --implementation cp --python-version 3.11 --target "${PACKAGE_DIR}" -r "${ROOT_DIR}/lambda_requirements.txt" || \
        python3 -m pip install --upgrade -r "${ROOT_DIR}/lambda_requirements.txt" -t "${PACKAGE_DIR}"
    fi
else
    echo "   Docker not available, attempting cross-platform install..."
    python3 -m pip install --upgrade --platform manylinux2014_x86_64 --only-binary=:all: --implementation cp --python-version 3.11 --target "${PACKAGE_DIR}" -r "${ROOT_DIR}/lambda_requirements.txt" || \
    python3 -m pip install --upgrade -r "${ROOT_DIR}/lambda_requirements.txt" -t "${PACKAGE_DIR}"
fi

echo "==> Copying application source"
rsync -av --quiet \
  --exclude "__pycache__" \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude "build" \
  --exclude "terraform" \
  --exclude "frontend" \
  "${ROOT_DIR}/vague_language_detector" \
  "${ROOT_DIR}/lambda_handler.py" \
  "${ROOT_DIR}/requirements.txt" \
  "${PACKAGE_DIR}/"

echo "==> Creating Lambda zip ${ZIP_PATH}"
(
  cd "${PACKAGE_DIR}"
  # Security: Set proper file permissions before zipping
  find . -type f -exec chmod 644 {} \;
  find . -type d -exec chmod 755 {} \;
  zip -r "${ZIP_PATH}" . >/dev/null
)

# Security: Verify zip file was created and has reasonable size
if [ ! -f "${ZIP_PATH}" ]; then
  echo "ERROR: Lambda zip file was not created"
  exit 1
fi

ZIP_SIZE=$(stat -f%z "${ZIP_PATH}" 2>/dev/null || stat -c%s "${ZIP_PATH}" 2>/dev/null)
if [ "${ZIP_SIZE}" -lt 1000 ] || [ "${ZIP_SIZE}" -gt 52428800 ]; then
  echo "WARNING: Lambda zip size (${ZIP_SIZE} bytes) seems unusual"
fi

echo "==> Running Terraform"
cd "${TERRAFORM_DIR}"

# Security: Initialize Terraform with backend configuration if available
terraform init

# Security: Validate Terraform configuration before applying
echo "==> Validating Terraform configuration"
if ! terraform validate; then
  echo "ERROR: Terraform validation failed"
  exit 1
fi

# Security: Plan before apply (optional, can be skipped with -y flag)
if [ "${1:-}" != "-y" ]; then
  echo "==> Running Terraform plan (use -y to skip plan and auto-approve)"
  terraform plan
  echo ""
  read -p "Apply these changes? (yes/no): " -r
  if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Deployment cancelled."
    exit 0
  fi
fi

terraform apply -auto-approve

API_ENDPOINT="$(terraform output -raw api_endpoint)"
FRONTEND_BUCKET="$(terraform output -raw frontend_bucket)"
CF_DOMAIN="$(terraform output -raw cloudfront_domain)"

echo "==> Syncing frontend to S3 bucket ${FRONTEND_BUCKET}"
aws s3 sync "${FRONTEND_DIR}" "s3://${FRONTEND_BUCKET}" --delete

echo ""
echo "Deployment complete."
echo "API base URL     : ${API_ENDPOINT}"
echo "Frontend (S3)    : s3://${FRONTEND_BUCKET}"
echo "Frontend (CDN)   : https://${CF_DOMAIN}"
echo "CloudWatch Dash  : $(terraform output -raw dashboard_name)"

