from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .classifier import ClassificationResult, classify


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Sentence or short paragraph to analyze")


class ClassificationResponse(BaseModel):
    distortion: bool
    distortion_type: str
    objectivity_score: int
    subjectivity_score: int
    verb_tense: str
    verb_type: dict
    confidence: float
    rationale: str

    @classmethod
    def from_result(cls, result: ClassificationResult) -> "ClassificationResponse":
        return cls(
            distortion=result.distortion,
            distortion_type=result.distortion_type,
            objectivity_score=result.objectivity_score,
            subjectivity_score=result.subjectivity_score,
            verb_tense=result.verb_tense,
            verb_type=result.verb_type,
            confidence=result.confidence,
            rationale=result.rationale,
        )


app = FastAPI(title="All-or-Nothing Classifier", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", response_model=ClassificationResponse)
def classify_text(request: TextRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = classify(text)
    return ClassificationResponse.from_result(result)
