# Language Detection Tools

A collection of FastAPI-based language analysis services for detecting cognitive distortions and vague language patterns in text.

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
- Global identity-label statements (e.g., "I am a failure")

**API Endpoints:**
- `GET /health` - Health check endpoint
- `POST /classify` - Classify text for cognitive distortions

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/classify \
  -H 'Content-Type: application/json' \
  -d '{"text":"I always mess everything up."}'
```

**Example Response:**
```json
{
  "has_cognitive_distortion": true
}
```

### Objective Language Detector

*Coming soon* - A service for detecting objective vs. subjective language patterns.

## Quick Start

### Prerequisites
- Python 3.8+
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

## Documentation

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

## License

[Add your license here]

## Contact

For questions or contributions, please visit [jpagan.com](https://jpagan.com)
