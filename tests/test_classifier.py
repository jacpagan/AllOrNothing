from app.classifier import classify


def test_detects_all_or_nothing_with_absolutes():
    result = classify("I always mess everything up.")
    assert result.distortion is True
    assert result.distortion_type == "all-or-nothing"
    assert result.objectivity_score < 70
    assert result.subjectivity_score > 30


def test_handles_neutral_sentence():
    result = classify("I am learning to code and I practice daily.")
    assert result.distortion is False
    assert 50 <= result.objectivity_score <= 100
    assert result.verb_type["action"] >= 1


def test_past_tense_penalty():
    result = classify("I was always failing before, but I changed.")
    assert result.verb_tense == "past"
    assert result.objectivity_score < 90
