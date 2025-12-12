import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .distortions import CBT_DISTORTIONS

# Deterministic keyword/pattern sets used across detectors.
ABSOLUTE_KEYWORDS = {
    "always",
    "never",
    "everything",
    "nothing",
    "everyone",
    "everybody",
    "noone",
    "no",
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
    "mess",
}

SHOULD_KEYWORDS = {"should", "must", "ought", "oughta", "have to", "need to", "supposed to"}
CATASTROPHIZING_TERMS = {
    "disaster",
    "catastrophe",
    "ruined",
    "ruin",
    "collapse",
    "fall apart",
    "falling apart",
    "worst case",
    "worst-case",
    "end of the world",
}
PERSONALIZATION_PATTERNS = [
    r"\bmy fault\b",
    r"\bbecause of me\b",
    r"\bit's on me\b",
    r"\bi caused\b",
    r"\bi made this happen\b",
]
EMOTIONAL_REASONING_PATTERNS = [
    r"\bi feel\b(?:\s+like|\s+that)?",
    r"\bit feels\b(?:\s+like|\s+that)?",
]
MAGNIFICATION_TERMS = {
    "totally",
    "completely",
    "utterly",
    "massive",
    "huge",
    "enormous",
    "disaster",
    "ruined",
    "worst",
    "nightmare",
}
MINIMIZATION_TERMS = {
    "just",
    "only",
    "no big deal",
    "not a big deal",
    "just a fluke",
    "just luck",
}
DISQUALIFYING_POSITIVE_PHRASES = {
    "just luck",
    "only luck",
    "doesn't count",
    "does not count",
    "anyone could do it",
    "anyone could have done it",
    "not a big deal",
    "no big deal",
    "just got lucky",
}
MENTAL_FILTER_PATTERNS = [
    r"\bonly\b.*\b(mistakes?|problems?|issues?|flaws?|faults?|failures?)\b",
    r"\bjust\b.*\b(negative|wrong|bad|awful|terrible)\b",
    r"\bfocus(ed)? on\b.*\b(negative|mistakes|problems)\b",
]
JUMPING_TO_CONCLUSIONS_PATTERNS = [
    r"\bthey (must|will|probably)\b",
    r"\bhe (must|will|probably)\b",
    r"\bshe (must|will|probably)\b",
    r"\bi'm sure\b",
    r"\bit will definitely\b",
    r"\bit's bound to\b",
    r"\bi bet\b",
    r"\bgoing to fail\b",
]

DISTORTION_NAMES = {d.name for d in CBT_DISTORTIONS}


@dataclass
class DetectedDistortion:
    name: str
    explanation: str  # Brief explanation of why detected
    confidence: str  # "high", "medium", "low" based on pattern strength


@dataclass
class DetectionResult:
    has_cognitive_distortion: bool
    distortions: List[DetectedDistortion]


def tokenize(text: str) -> List[str]:
    # Keep tokenization deliberately simple and deterministic.
    return re.findall(r"[a-zA-Z']+", text.lower())


def _build_detection(name: str, explanation: str, confidence: str = "medium") -> DetectedDistortion:
    if name not in DISTORTION_NAMES:
        raise ValueError(f"Unknown distortion name: {name}")
    return DetectedDistortion(name=name, explanation=explanation, confidence=confidence)


def _collect_terms(tokens: Iterable[str], vocabulary: Iterable[str]) -> List[str]:
    vocab_set = set(vocabulary)
    return sorted({t for t in tokens if t in vocab_set})


def detect_binary(text: str, tokens: List[str]) -> Optional[str]:
    lowered = text.lower()
    if re.search(r"\beither\b(?:\W+\w+){0,5}\W+\bor\b", lowered):
        return "binary framing pattern 'either ... or'"
    for i in range(len(tokens) - 2):
        if tokens[i] == "all" and tokens[i + 1] == "or" and tokens[i + 2] == "nothing":
            return "binary framing 'all or nothing'"
    for idx, token in enumerate(tokens):
        if token == "either":
            window_end = min(len(tokens), idx + 7)
            if "or" in tokens[idx + 1 : window_end]:
                return "binary framing within short window"
    return None


def detect_absolutes(text: str, tokens: List[str]) -> List[str]:
    matches: List[str] = []
    lowered = text.lower()
    if "no one" in lowered:
        matches.append("no one")
    matches.extend(_collect_terms(tokens, ABSOLUTE_KEYWORDS))
    return matches


def detect_identity_label_be_phrase(text: str) -> Optional[str]:
    lower = text.lower()
    labels = "|".join(sorted(NEGATIVE_IDENTITY_LABELS))
    be = "|".join(sorted(BE_VERBS))
    contractions = "|".join(sorted(CONTRACTED_SUBJECT_BE))
    pattern = re.compile(
        rf"\b(?:(?:i|you|we|they|he|she)\s+(?:{be})|(?:{contractions}))\s+(?:a|an|the)?\s*(?:\w+\s+)*({labels})\b"
    )
    match = pattern.search(lower)
    if match:
        return match.group(1)
    return None


def detect_all_or_nothing(text: str, tokens: List[str]) -> Optional[DetectedDistortion]:
    evidence: List[str] = []
    binary_signal = detect_binary(text, tokens)
    if binary_signal:
        evidence.append(binary_signal)
    absolute_terms = detect_absolutes(text, tokens)
    if absolute_terms:
        evidence.append(f"absolutist terms: {', '.join(sorted(set(absolute_terms)))}")
    if "all-or-nothing" in text.lower():
        evidence.append("explicit phrase 'all-or-nothing'")
    if not evidence:
        return None
    confidence = "high" if binary_signal else "medium"
    explanation = "; ".join(evidence)
    return _build_detection("All-or-Nothing Thinking", explanation, confidence)


def detect_overgeneralization(text: str, tokens: List[str]) -> Optional[DetectedDistortion]:
    general_terms = [t for t in tokens if t in {"everyone", "everybody", "nobody", "everything", "nothing", "always", "never"}]
    if not general_terms:
        return None
    explanation = f"sweeping terms: {', '.join(sorted(set(general_terms)))}"
    confidence = "medium"
    return _build_detection("Overgeneralization", explanation, confidence)


def detect_labeling(text: str, tokens: List[str]) -> Optional[DetectedDistortion]:
    label_match = detect_identity_label_be_phrase(text)
    if label_match:
        explanation = f"identity label paired with be-verb: '{label_match}'"
        return _build_detection("Labeling", explanation, "high")
    return None


def detect_should_statements(text: str, tokens: List[str]) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    found_phrases = []
    for phrase in SHOULD_KEYWORDS:
        if phrase in lowered:
            found_phrases.append(phrase)
    if not found_phrases:
        return None
    explanation = f"rigid expectations via: {', '.join(sorted(set(found_phrases)))}"
    confidence = "medium"
    if any(p in {"must", "have to"} for p in found_phrases):
        confidence = "high"
    return _build_detection("Should Statements", explanation, confidence)


def detect_catastrophizing(text: str) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    hits = [term for term in CATASTROPHIZING_TERMS if term in lowered]
    if not hits:
        return None
    explanation = f"worst-case language: {', '.join(sorted(set(hits)))}"
    confidence = "high" if len(hits) > 0 else "medium"
    return _build_detection("Catastrophizing", explanation, confidence)


def detect_personalization(text: str) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    for pattern in PERSONALIZATION_PATTERNS:
        if re.search(pattern, lowered):
            return _build_detection("Personalization", f"self-blame phrase matched '{pattern}'", "medium")
    return None


def detect_emotional_reasoning(text: str) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    for pattern in EMOTIONAL_REASONING_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            snippet = match.group(0)
            return _build_detection("Emotional Reasoning", f"feeling-as-fact phrasing: '{snippet}'", "medium")
    return None


def detect_magnification_minimization(text: str, tokens: List[str]) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    magnifiers = [term for term in MAGNIFICATION_TERMS if term in lowered]
    minimizers = [phrase for phrase in MINIMIZATION_TERMS if phrase in lowered]
    if not magnifiers and not minimizers:
        return None
    parts = []
    if magnifiers:
        parts.append(f"exaggerating terms: {', '.join(sorted(set(magnifiers)))}")
    if minimizers:
        parts.append(f"downplaying terms: {', '.join(sorted(set(minimizers)))}")
    explanation = "; ".join(parts)
    confidence = "medium"
    if magnifiers and "disaster" in magnifiers:
        confidence = "high"
    return _build_detection("Magnification/Minimization", explanation, confidence)


def detect_disqualifying_positive(text: str) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    hits = [phrase for phrase in DISQUALIFYING_POSITIVE_PHRASES if phrase in lowered]
    if not hits:
        return None
    explanation = f"dismissing positives: {', '.join(sorted(set(hits)))}"
    confidence = "medium"
    return _build_detection("Disqualifying the Positive", explanation, confidence)


def detect_mental_filter(text: str) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    for pattern in MENTAL_FILTER_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            return _build_detection("Mental Filter", f"focus on negatives: '{match.group(0)}'", "medium")
    return None


def detect_jumping_to_conclusions(text: str) -> Optional[DetectedDistortion]:
    lowered = text.lower()
    for pattern in JUMPING_TO_CONCLUSIONS_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            return _build_detection("Jumping to Conclusions", f"assumption language: '{match.group(0)}'", "medium")
    return None


def detect(text: str) -> DetectionResult:
    tokens = tokenize(text)
    detectors = [
        detect_all_or_nothing,
        detect_overgeneralization,
        detect_labeling,
        detect_should_statements,
        detect_catastrophizing,
        detect_personalization,
        detect_emotional_reasoning,
        detect_magnification_minimization,
        detect_disqualifying_positive,
        detect_mental_filter,
        detect_jumping_to_conclusions,
    ]

    found: List[DetectedDistortion] = []
    seen_names = set()
    for detector in detectors:
        result = detector(text, tokens) if detector.__code__.co_argcount == 2 else detector(text)
        if result and result.name not in seen_names:
            seen_names.add(result.name)
            found.append(result)

    return DetectionResult(has_cognitive_distortion=bool(found), distortions=found)
