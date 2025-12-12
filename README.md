# Language Detection Tools

A collection of FastAPI-based language analysis services for detecting cognitive distortions and vague language patterns in text.

## 🚀 Live Deployment

**Access the deployed application:**
- **Frontend:** https://d1ldmuzlvu5xxs.cloudfront.net
- **API Endpoint:** https://hff2mpuk6i.execute-api.us-east-1.amazonaws.com

**Quick Test:**
```bash
curl -X POST "https://hff2mpuk6i.execute-api.us-east-1.amazonaws.com/classify" \
  -H "Content-Type: application/json" \
  -d '{"text":"I am a total failure"}'
```

The app is deployed on AWS using:
- **Lambda** - Serverless function hosting
- **API Gateway** - HTTP API with rate limiting and security
- **CloudFront + S3** - Frontend hosting with CDN
- **Terraform** - Infrastructure as Code

See [AWS Deployment Guide](aws-deployment.md) for deployment details.

## Projects

### Vague Language Detector

A lightweight FastAPI service that performs binary detection of vague language patterns in statements. The detector identifies cognitive distortions by analyzing text for patterns that are not guaranteed to be 100% true in all cases.

**Features:**
- Binary classification: returns `true` or `false` for cognitive distortion detection
- Fast, deterministic heuristics-based detection
- No data persistence or logging of user text
- Low latency (<100ms typical response time)

**Detection Patterns:**
- Be-verbs ("to be" verbs: am/is/are/was/were/be/being/been)
- Absolutist language (always/never/everything/nothing/everyone/no one)
- Binary framing markers (either/or, all or nothing)
- Global identity-label statements (e.g., "I am a failure", "I'm a total failure")
- Handles contractions with modifiers (e.g., "I'm a complete failure")

**API Endpoints:**
- `GET /health` - Health check endpoint
- `POST /classify` - Classify text for cognitive distortions

**Example Request:**
```bash
# Local development
curl -X POST http://127.0.0.1:8000/classify \
  -H 'Content-Type: application/json' \
  -d '{"text":"I always mess everything up."}'

# Deployed API
curl -X POST https://hff2mpuk6i.execute-api.us-east-1.amazonaws.com/classify \
  -H 'Content-Type: application/json' \
  -d '{"text":"I am a total failure"}'
```

**Example Response:**
```json
{
  "has_cognitive_distortion": true
}
```

**Test Examples:**
- ✅ "I always mess everything up." → `true` (absolutist language)
- ✅ "I'm a total failure" → `true` (identity label with contraction)
- ✅ "I am a complete failure" → `true` (identity label)
- ❌ "This project failed yesterday." → `false` (neutral, factual statement)

### Objective Language Detector

*Coming soon* - A service for detecting objective vs. subjective language patterns.

## Quick Start

### Option 1: Use the Deployed App (Easiest)

1. Open https://d1ldmuzlvu5xxs.cloudfront.net in your browser
2. Paste the API endpoint: `https://hff2mpuk6i.execute-api.us-east-1.amazonaws.com`
3. Enter text to analyze and click "Analyze"

### Option 2: Local Development

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Vague Language Detector

Start the FastAPI server:
```bash
python -m uvicorn vague_language_detector.main:app --host 127.0.0.1 --port 8000
```

The API will be available at:
- API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`
- Alternative docs: `http://127.0.0.1:8000/redoc`

### Testing

Run the test suite:
```bash
pytest
```

### Stress Testing

Start the server, then in a separate terminal:
```bash
python scripts/stress_test.py --concurrency 50 --duration 15
```

## Deployment

### AWS Deployment

The application is deployed on AWS using Terraform. To deploy or update:

```bash
./deploy.sh
```

This will:
1. Build a Linux-compatible Lambda package
2. Deploy infrastructure with Terraform
3. Sync frontend files to S3
4. Output deployment endpoints

**Deployment Features:**
- ✅ Rate limiting (100 req/s, 200 burst)
- ✅ Security headers (HSTS, CSP, X-Frame-Options, etc.)
- ✅ S3 encryption and versioning
- ✅ CloudFront CDN with HTTPS
- ✅ CloudWatch logging and monitoring
- ✅ Input validation and size limits

See [AWS Deployment Guide](aws-deployment.md) and [Security Documentation](SECURITY.md) for details.

### Prerequisites for Deployment
- AWS CLI configured
- Terraform >= 1.5
- AWS credentials with deployment permissions

## Documentation

- [AWS Deployment Guide](aws-deployment.md) - Complete deployment instructions
- [Security Features](SECURITY.md) - Security implementation details
- [Vague Language Detector PRD](vague_language_detector_prd.md) - Product Requirements Document
- [Vague Language Detector SRD](vague_language_detector_srd.md) - Software Requirements Document
- [Objective Language Detector PRD](objective_language_detector_prd.md) - Product Requirements Document
- [Objective Language Detector SRD](objective_language_detector_srd.md) - Software Requirements Document

## Architecture

Both services are built using:
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation

The services are:
- Stateless (no database or persistent storage)
- Deterministic (same input always yields same output)
- Privacy-focused (no logging or storage of user text)
- Secure (rate limiting, encryption, security headers)
- Scalable (serverless Lambda architecture)

## License

[Add your license here]

## Contact

For questions or contributions, please visit [jpagan.com](https://jpagan.com)
