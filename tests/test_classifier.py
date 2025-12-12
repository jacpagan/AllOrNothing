from app.classifier import detect


def test_detects_distortion_with_absolutes():
    result = detect("I always mess everything up.")
    assert result.has_cognitive_distortion is True


def test_handles_neutral_sentence():
    # Neutral example must avoid be-verbs because this app treats be-verbs as distortion signals.
    result = detect("I practice coding daily.")
    assert result.has_cognitive_distortion is False


def test_detects_distortion_with_identity_label():
    result = detect("I am a failure.")
    assert result.has_cognitive_distortion is True


def test_detects_distortion_with_binary_framing():
    result = detect("It is either a total success or a complete failure.")
    assert result.has_cognitive_distortion is True
