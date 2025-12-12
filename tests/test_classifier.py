from vague_language_detector.classifier import detect


def names(result):
    return {d.name for d in result.distortions}


def test_detects_all_or_nothing_and_binary():
    result = detect("It is either perfect or a complete failure.")
    assert result.has_cognitive_distortion is True
    assert "All-or-Nothing Thinking" in names(result)


def test_detects_overgeneralization():
    result = detect("Everyone always ignores me.")
    assert result.has_cognitive_distortion is True
    assert "Overgeneralization" in names(result)


def test_detects_labeling():
    result = detect("I'm a failure.")
    assert result.has_cognitive_distortion is True
    assert "Labeling" in names(result)


def test_detects_should_statements():
    result = detect("I should always get everything right.")
    assert "Should Statements" in names(result)


def test_detects_catastrophizing():
    result = detect("If I slip once, everything will fall apart and be a disaster.")
    assert "Catastrophizing" in names(result)


def test_detects_personalization():
    result = detect("The delay is my fault.")
    assert "Personalization" in names(result)


def test_detects_emotional_reasoning():
    result = detect("I feel like this proves I'm a failure.")
    assert "Emotional Reasoning" in names(result)


def test_detects_magnification_minimization():
    result = detect("This tiny typo is a complete disaster.")
    assert "Magnification/Minimization" in names(result)


def test_detects_disqualifying_positive():
    result = detect("I did well, but it was just luck and doesn't count.")
    assert "Disqualifying the Positive" in names(result)


def test_detects_mental_filter():
    result = detect("I only saw the mistakes and ignored the good parts.")
    assert "Mental Filter" in names(result)


def test_detects_jumping_to_conclusions():
    result = detect("They must be laughing at me already.")
    assert "Jumping to Conclusions" in names(result)


def test_detects_all_or_nothing_hyphenated():
    result = detect("It was an all-or-nothing bet.")
    assert "All-or-Nothing Thinking" in names(result)


def test_does_not_flag_distant_either_or():
    result = detect(
        "Either this will eventually after many unexpected delays in the pipeline conclude or not."
    )
    assert result.has_cognitive_distortion is False
    assert result.distortions == []


def test_handles_neutral_sentence():
    result = detect("I practice coding daily.")
    assert result.has_cognitive_distortion is False
    assert result.distortions == []


def test_detects_multiple_distortions_and_explanations_present():
    result = detect("I always mess everything up; it's a disaster and entirely my fault.")
    detected_names = names(result)
    assert result.has_cognitive_distortion is True
    # Expect multiple overlapping detections
    assert "All-or-Nothing Thinking" in detected_names
    assert "Overgeneralization" in detected_names
    assert "Catastrophizing" in detected_names
    assert "Personalization" in detected_names
    assert all(d.explanation for d in result.distortions)
