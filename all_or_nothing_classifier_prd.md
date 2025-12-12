# Cognitive Distortion Detector — Product Requirements Document (PRD)
Version: 2.0  
Owner: Jose

---

## 1. Purpose (single responsibility)
The application does **exactly one thing**:

- Given a single user-provided statement (one sentence or short paragraph), it returns **whether the statement contains a cognitive distortion** (**true/false**).

Everything else (scores, verb tense/type, rewriting, analytics, billing, multi-distortion labels, etc.) is out of scope.

---

## 2. Problem statement
People frequently write and speak in ways that reflect cognitive distortions (e.g., absolutist language, global self-labeling, blame-heavy phrasing). They often do not notice it while drafting messages, journaling, or reflecting.

We need a small, reliable detector that answers one question:

> Does this statement contain a cognitive distortion?

---

## 3. Target users
- Individuals writing a sentence/short paragraph who want quick feedback.
- Developers integrating a simple “distortion present?” check into their app.

---

## 4. In-scope behavior
- **Binary classification only**: `has_cognitive_distortion = true|false`
- **Single input**: one string (`text`)
- **Low latency** suitable for interactive use

### 4.1 What counts as a “cognitive distortion” in this app (definition)
For this application, we optimize for **objective truth claims**: language that is not guaranteed to be **100% true in all cases, every single time** is treated as a cognitive distortion signal.

As a result, **any use of “to be” / be-verbs** (e.g., “am/is/are/was/were/be/being/been”) is categorized as a cognitive distortion signal, because it commonly encodes absolute identity or permanence (E-prime rationale).

---

## 5. Out of scope (explicit)
- Distortion type classification (e.g., “all-or-nothing”, “labeling”, etc.)
- Severity scoring (numeric scales)
- Verb tense/type analysis
- Suggestions / rewrites / coaching
- Multi-sentence aggregation
- User accounts, billing, quotas, dashboards
- Storing or logging user-provided text

---

## 6. Functional requirements

### 6.1 Input
- A single field: `text` (string, non-empty after trimming)

### 6.2 Output
The API returns a JSON object:

```json
{
  "has_cognitive_distortion": true
}
```

---

## 7. Quality requirements (what “correctly” means here)
- **Consistency**: same input always yields the same output.
- **Safety**: do not store or log user-provided text.
- **Performance**: typical response time under 100ms on a local machine.
- **Clarity**: error on empty input with a clear message.

---

## 8. Success criteria
- The API reliably returns `true` for obvious cognitive-distortion statements and `false` for neutral, grounded statements.
- The implementation and tests match the spec exactly (binary output only).

---

## 9. Appendix
- Software Requirements Document (SRD): [`all_or_nothing_classifier_srd.md`](all_or_nothing_classifier_srd.md)
