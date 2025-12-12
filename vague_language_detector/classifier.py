import re
from dataclasses import dataclass
from typing import List

# v2.0: The application has a single responsibility: detect whether a statement
# contains a cognitive distortion (binary yes/no).

# Minimal, deterministic signals (heuristics):
# - Absolutist language (often absolute / globalizing language)
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

CONTRACTED_SUBJECT_BE = {"i'm", "you're", "we're", "they're", "he's", "she's"}

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


def detect_binary(text: str, tokens: List[str]) -> bool:
    # Require ordered/sequenced patterns to avoid distant false positives.
    lowered = text.lower()

    # "either ... or" with up to 5 words between terms.
    if re.search(r"\beither\b(?:\W+\w+){0,5}\W+\bor\b", lowered):
        return True

    # Direct "all or nothing" phrase (supports hyphenated via token walk below).
    for i in range(len(tokens) - 2):
        if tokens[i] == "all" and tokens[i + 1] == "or" and tokens[i + 2] == "nothing":
            return True

    # Fallback ordered check within a short window to catch tokenized variants.
    for idx, token in enumerate(tokens):
        if token == "either":
            window_end = min(len(tokens), idx + 7)
            if "or" in tokens[idx + 1 : window_end]:
                return True

    return False


def detect_identity_label_be_phrase(text: str) -> bool:
    # Detect identity-label constructions like:
    # - "I am a failure"
    # - "You are useless"
    # - "I'm a total failure"
    # - "I am a complete failure"
    lower = text.lower()
    labels = "|".join(sorted(NEGATIVE_IDENTITY_LABELS))
    be = "|".join(sorted(BE_VERBS))
    contractions = "|".join(sorted(CONTRACTED_SUBJECT_BE))
    # Allow optional article, then optional modifiers/adjectives (like "total", "complete", "absolute", "really", "so")
    # before the negative identity label
    pattern = re.compile(
        rf"\b(?:(?:i|you|we|they|he|she)\s+(?:{be})|(?:{contractions}))\s+(?:a|an|the)?\s*(?:\w+\s+)*({labels})\b"
    )
    return pattern.search(lower) is not None


def detect(text: str) -> DetectionResult:
    tokens = tokenize(text)

    # v2.0 objective-function choice:
    # Treat any "to be" verb usage as a cognitive distortion signal.
    be_tokens = BE_VERBS | CONTRACTED_SUBJECT_BE
    has_be_verb = any(t in be_tokens for t in tokens)

    has_distortion = (
        has_be_verb
        or detect_absolutes(text, tokens)
        or detect_binary(text, tokens)
        or detect_identity_label_be_phrase(text)
    )

    return DetectionResult(has_cognitive_distortion=bool(has_distortion))
