import re
from dataclasses import dataclass
from typing import List

# v2.0: The application has a single responsibility: detect whether a statement
# contains a cognitive distortion (binary yes/no).

# Minimal, deterministic signals (heuristics):
# - Absolutist language (often all-or-nothing / overgeneralization)
# - Binary framing markers
# - Global identity-labeling statements ("I am a failure")

ABSOLUTE_KEYWORDS = {
    "always",
    "never",
    "everything",
    "nothing",
    "everyone",
    "no one",
    "nobody",
}

BINARY_MARKERS = {
    ("either", "or"),
    ("all", "or", "nothing"),
}

BE_VERBS = {"am", "is", "are", "was", "were", "be", "being", "been"}

NEGATIVE_IDENTITY_LABELS = {
    "failure",
    "loser",
    "idiot",
    "stupid",
    "worthless",
    "useless",
    "lazy",
    "incompetent",
    "bad",
    "terrible",
    "awful",
    "broken",
}


@dataclass
class DetectionResult:
    has_cognitive_distortion: bool


def tokenize(text: str) -> List[str]:
    # Keep tokenization deliberately simple and deterministic.
    return re.findall(r"[a-zA-Z']+", text.lower())


def detect_absolutes(text: str, tokens: List[str]) -> bool:
    # Support both single-token keywords and multi-token phrases (e.g. "no one").
    lowered = text.lower()
    if "no one" in lowered:
        return True
    return any(t in ABSOLUTE_KEYWORDS for t in tokens)


def detect_binary(tokens: List[str]) -> bool:
    token_set = set(tokens)
    for pattern in BINARY_MARKERS:
        if set(pattern).issubset(token_set):
            return True
    return False


def detect_identity_label_be_phrase(text: str) -> bool:
    # Detect identity-label constructions like:
    # - "I am a failure"
    # - "You are useless"
    lower = text.lower()
    labels = "|".join(sorted(NEGATIVE_IDENTITY_LABELS))
    be = "|".join(sorted(BE_VERBS))
    pattern = re.compile(
        rf"\b(i|you|we|they|he|she)\s+({be})\s+(?:a|an|the)?\s*(?:really\s+|so\s+)?({labels})\b"
    )
    return pattern.search(lower) is not None


def detect(text: str) -> DetectionResult:
    tokens = tokenize(text)

    # v2.0 objective-function choice:
    # Treat any "to be" verb usage as a cognitive distortion signal.
    has_be_verb = any(t in BE_VERBS for t in tokens)

    has_distortion = (
        has_be_verb
        or detect_absolutes(text, tokens)
        or detect_binary(tokens)
        or detect_identity_label_be_phrase(text)
    )

    return DetectionResult(has_cognitive_distortion=bool(has_distortion))
