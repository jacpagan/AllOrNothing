from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import os

from .classifier import DetectionResult, detect

# Security: Maximum text length (10KB default, ~2000 characters)
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "2000"))


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH, description="Sentence or short paragraph to analyze")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty or whitespace only.")
        if len(v) > MAX_TEXT_LENGTH:
            raise ValueError(f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters.")
        return v


class DetectionResponse(BaseModel):
    has_cognitive_distortion: bool

    @classmethod
    def from_result(cls, result: DetectionResult) -> "DetectionResponse":
        return cls(has_cognitive_distortion=result.has_cognitive_distortion)


app = FastAPI(
    title="Vague Language Detector",
    version="0.3.0",
    docs_url=None,  # Security: Disable docs in production
    redoc_url=None,  # Security: Disable redoc in production
)

# Security: CORS middleware (configured at API Gateway level, but adding here for defense in depth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Controlled by API Gateway CORS config
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=3600,
)


# Security: Add security headers to all responses
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # Security: Don't expose internal error details
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Security: Don't expose internal error details
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", response_model=DetectionResponse)
def classify_text(request: TextRequest):
    # Additional validation (defense in depth)
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    # Security: Additional length check
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters."
        )
    
    try:
        result = detect(text)
        return DetectionResponse.from_result(result)
    except Exception as e:
        # Security: Log error but don't expose details to client
        raise HTTPException(status_code=500, detail="Error processing request.")
