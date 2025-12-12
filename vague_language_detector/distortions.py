from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DistortionDefinition:
    """Static taxonomy entry describing a CBT cognitive distortion."""

    name: str
    description: str
    cues: List[str]
    example: str


# Core CBT distortions the detector will surface.
CBT_DISTORTIONS: List[DistortionDefinition] = [
    DistortionDefinition(
        name="All-or-Nothing Thinking",
        description="Viewing situations in absolute, black-or-white terms without nuance.",
        cues=["always", "never", "either/or", "all or nothing", "perfect or failure"],
        example="It is either perfect or a complete failure.",
    ),
    DistortionDefinition(
        name="Overgeneralization",
        description="Making sweeping conclusions from a single event.",
        cues=["everyone", "no one", "nothing ever works", "everything", "never again"],
        example="Everyone ignores me every time I speak.",
    ),
    DistortionDefinition(
        name="Mental Filter",
        description="Focusing only on the negative details while ignoring positives.",
        cues=["only the mistakes", "just the problems", "ignore the good parts"],
        example="I only noticed the mistakes in my presentation.",
    ),
    DistortionDefinition(
        name="Disqualifying the Positive",
        description="Rejecting or discounting positive experiences.",
        cues=["just luck", "doesn't count", "anyone could do it"],
        example="I did fine, but it was just luck and doesn't count.",
    ),
    DistortionDefinition(
        name="Jumping to Conclusions",
        description="Assuming outcomes or others' thoughts without evidence.",
        cues=["they must think", "I know they'll", "it will definitely"],
        example="They must think I'm incompetent.",
    ),
    DistortionDefinition(
        name="Magnification/Minimization",
        description="Exaggerating negatives or downplaying positives.",
        cues=["disaster", "ruined", "massive problem", "just a fluke", "not a big deal"],
        example="This small mistake is a complete disaster.",
    ),
    DistortionDefinition(
        name="Emotional Reasoning",
        description="Assuming feelings reflect facts.",
        cues=["I feel like", "it feels as if", "because I feel it, it is true"],
        example="I feel like I'm a failure, so it must be true.",
    ),
    DistortionDefinition(
        name="Should Statements",
        description="Using rigid 'should', 'must', or 'ought' statements.",
        cues=["should", "must", "ought", "have to", "supposed to"],
        example="I should never make mistakes.",
    ),
    DistortionDefinition(
        name="Labeling",
        description="Assigning a global, negative label to oneself or others.",
        cues=["I am a failure", "you're useless", "they're idiots"],
        example="I am a total failure.",
    ),
    DistortionDefinition(
        name="Personalization",
        description="Blaming oneself for events outside one's control.",
        cues=["my fault", "because of me", "it's on me"],
        example="The project's delay is entirely my fault.",
    ),
    DistortionDefinition(
        name="Catastrophizing",
        description="Assuming the worst-case scenario will happen.",
        cues=["it will be a disaster", "everything will collapse", "this will ruin everything"],
        example="If I slip once, everything will fall apart.",
    ),
]


