from pydantic import BaseModel, Field, conint
from typing import List

class CitedItem(BaseModel):
    """A schema for any inferred trait that requires a citation."""
    description: str = Field(
        description="The detailed description of the inferred trait, behavior, or interest."
    )
    citations: List[str] = Field(
        description="A list of source URLs used as evidence for this inference."
    )

class PersonalityTraits(BaseModel):
    """Personality traits scored on a 1-10 scale based on user's content."""
    introvert_extrovert: conint(ge=1, le=10) = Field(description="Score from 1 (Introvert) to 10 (Extrovert).")
    analytical_creative: conint(ge=1, le=10) = Field(description="Score from 1 (Analytical) to 10 (Creative).")
    skeptical_trusting: conint(ge=1, le=10) = Field(description="Score from 1 (Skeptical) to 10 (Trusting).")
    passive_proactive: conint(ge=1, le=10) = Field(description="Score from 1 (Passive/Reactive) to 10 (Proactive/Initiator).")

class UserPersona(BaseModel):
    """The complete, structured user persona based on Reddit activity."""
    username: str = Field(description="The Reddit username of the user.")
    summary: str = Field(description="A brief, one-paragraph narrative summary of the user's online personality.")
    personality_traits: PersonalityTraits
    behaviors_and_habits: List[CitedItem] = Field(description="Observable behaviors and posting habits.")
    topics_of_interest: List[CitedItem] = Field(description="Key topics the user is interested in or has expertise in.")
    motivations_and_values: List[CitedItem] = Field(description="Inferred motivations and core values driving the user's engagement.")
    frustrations_and_pain_points: List[CitedItem] = Field(description="Common frustrations or problems the user discusses.")