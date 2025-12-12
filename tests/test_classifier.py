from vague_language_detector.classifier import detect


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


def test_detects_contracted_identity_label_im():
    result = detect("I'm a failure.")
    assert result.has_cognitive_distortion is True


def test_detects_contracted_identity_label_youre():
    result = detect("You're useless.")
    assert result.has_cognitive_distortion is True


def test_detects_all_or_nothing_hyphenated():
    result = detect("It was an all-or-nothing bet.")
    assert result.has_cognitive_distortion is True


def test_does_not_flag_distant_either_or():
    result = detect(
        "Either this will eventually after many unexpected delays in the pipeline conclude or not."
    )
    assert result.has_cognitive_distortion is False
