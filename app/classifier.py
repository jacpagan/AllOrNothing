import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


# Core vocab and weights derived from the SRD tables.
ABSOLUTE_KEYWORDS = {"always", "never", "everything", "nothing"}
BINARY_MARKERS = {("either", "or"), ("all", "or", "nothing")}
EMOTIONAL_AMPLIFIERS = {"always", "never", "totally", "completely", "entirely", "absolutely"}
BE_VERBS = {"am", "is", "are", "was", "were", "be", "being", "been"}
ACTION_VERBS = {
    "do",
    "does",
    "did",
    "try",
    "tried",
    "make",
    "made",
    "take",
    "took",
    "fix",
    "fixed",
    "change",
    "changed",
    "improve",
    "improved",
    "learn",
    "learned",
    "learning",
    "practice",
    "practicing",
    "solve",
    "solved",
    "work",
    "worked",
    "build",
    "built",
    "create",
    "created",
}


@dataclass
class ClassificationResult:
    distortion: bool
    distortion_type: str
    objectivity_score: int
    subjectivity_score: int
    verb_tense: str
    verb_type: Dict[str, int]
    confidence: float
    rationale: str


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def detect_absolutes(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t in ABSOLUTE_KEYWORDS]


def detect_emotional(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t in EMOTIONAL_AMPLIFIERS]


def detect_binary(tokens: List[str]) -> bool:
    token_set = set(tokens)
    for pattern in BINARY_MARKERS:
        if set(pattern).issubset(token_set):
            return True
    return False


def detect_verb_tense(tokens: List[str]) -> str:
    past_cues = {"was", "were", "did", "had"}
    if any(t in past_cues or t.endswith("ed") for t in tokens):
        return "past"
    return "present"


def detect_verb_types(tokens: List[str]) -> Dict[str, int]:
    be_count = sum(1 for t in tokens if t in BE_VERBS)
    action_count = sum(1 for t in tokens if t in ACTION_VERBS)
    return {"be": be_count, "action": action_count}


def score_text(
    absolutes: List[str],
    binary: bool,
    emotional: List[str],
    verb_tense: str,
    verb_types: Dict[str, int],
) -> Tuple[int, List[str]]:
    score = 100
    rationale_bits: List[str] = []

    for word in absolutes:
        score -= 40 if word in {"always", "never"} else 30
    if binary:
        rationale_bits.append("Binary framing detected")
    if verb_tense == "past":
        score -= 20
        rationale_bits.append("Past tense reduces objectivity")
    else:
        score += 5
        rationale_bits.append("Present tense boosts clarity")

    be_penalty = 10 * verb_types["be"]
    if be_penalty:
        score -= be_penalty
        rationale_bits.append(f"{verb_types['be']} be-verb(s) found")

    action_reward = 5 * verb_types["action"]
    if action_reward:
        score += action_reward
        rationale_bits.append(f"{verb_types['action']} action verb(s) found")

    if emotional:
        score -= 15 * len(emotional)
        rationale_bits.append("Emotional amplifiers present")

    score = max(0, min(100, score))
    return score, rationale_bits


def derive_confidence(absolutes: List[str], binary: bool, emotional: List[str]) -> float:
    confidence = 0.5
    confidence += 0.15 * len(absolutes)
    confidence += 0.1 if binary else 0
    confidence += 0.05 * len(emotional)
    return round(max(0.0, min(1.0, confidence)), 2)


def classify(text: str) -> ClassificationResult:
    tokens = tokenize(text)
    absolutes = detect_absolutes(tokens)
    emotional = detect_emotional(tokens)
    binary = detect_binary(tokens)
    verb_tense = detect_verb_tense(tokens)
    verb_types = detect_verb_types(tokens)

    score, rationale_bits = score_text(absolutes, binary, emotional, verb_tense, verb_types)
    subjectivity = 100 - score

    distortion = bool(absolutes or binary)
    distortion_type = "all-or-nothing" if distortion else "none"
    rationale_parts = []
    if absolutes:
        rationale_parts.append(f"Absolutes found: {', '.join(sorted(set(absolutes)))}")
    if binary:
        rationale_parts.append("Binary framing terms present")
    if emotional:
        rationale_parts.append(f"Amplifiers: {', '.join(sorted(set(emotional)))}")
    rationale_parts.extend(rationale_bits)
    rationale = "; ".join(rationale_parts) if rationale_parts else "No strong distortion signals found."

    confidence = derive_confidence(absolutes, binary, emotional)

    return ClassificationResult(
        distortion=distortion,
        distortion_type=distortion_type,
        objectivity_score=score,
        subjectivity_score=subjectivity,
        verb_tense=verb_tense,
        verb_type=verb_types,
        confidence=confidence,
        rationale=rationale,
    )
