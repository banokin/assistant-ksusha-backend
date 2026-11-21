from pydantic import BaseModel, Field


class EmotionCreate(BaseModel):
    emotion_group: str
    emotion_name: str
    intensity: int = Field(ge=0, le=10)
    situation: str
    automatic_thought: str


class EmotionAnalysis(BaseModel):
    emotion_group: str
    emotion_name: str
    intensity: int = Field(ge=0, le=10)
    situation: str
    automatic_thought: str

    cognitive_distortions: list[str]
    alternative_thought: str
    psychologist_question: str