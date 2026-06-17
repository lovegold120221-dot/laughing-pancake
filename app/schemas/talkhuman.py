# app/schemas/talkhuman.py

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ExpressiveVoiceProfile(BaseModel):
    warmth: float = Field(default=0.75, ge=0.0, le=1.0)
    emotional_range: float = Field(default=0.8, ge=0.0, le=1.0)
    laughter_frequency: float = Field(default=0.25, ge=0.0, le=1.0)
    giggle_frequency: float = Field(default=0.15, ge=0.0, le=1.0)
    breathiness: float = Field(default=0.25, ge=0.0, le=1.0)
    hesitation_naturalness: float = Field(default=0.35, ge=0.0, le=1.0)
    empathy_level: float = Field(default=0.85, ge=0.0, le=1.0)
    conversational_energy: float = Field(default=0.65, ge=0.0, le=1.0)
    interruption_sensitivity: float = Field(default=0.75, ge=0.0, le=1.0)


class HumanExpressionSettings(BaseModel):
    allow_laughs: bool = True
    allow_giggles: bool = True
    allow_sighs: bool = True
    allow_soft_pauses: bool = True
    allow_backchanneling: bool = True
    allow_emotional_reflection: bool = True

    expression_style: Literal[
        "normal_human",
        "warm_friend",
        "professional_agent",
        "soft_emotional",
        "playful",
        "calm_supportive"
    ] = "normal_human"


class TalkHumanSessionCreateRequest(BaseModel):
    model: Literal["talkhuman-3.1"] = "talkhuman-3.1"
    voice_name: str = "Phoenix"

    response_mode: Literal[
        "audio_only",
        "audio_with_text_events"
    ] = "audio_with_text_events"

    personality: Literal[
        "normal_human",
        "friendly",
        "empathetic",
        "professional",
        "playful",
        "calm"
    ] = "normal_human"

    expression: HumanExpressionSettings = Field(default_factory=HumanExpressionSettings)
    voice_profile: ExpressiveVoiceProfile = Field(default_factory=ExpressiveVoiceProfile)

    system_behavior: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class TalkHumanSessionCreateResponse(BaseModel):
    session_id: str
    provider: str = "Eburon AI"
    model: str = "talkhuman-3.1"
    product: str = "TalkHuman"
    voice_name: str = "Phoenix"
    status: str
    created_at: str


class TalkHumanMessageRequest(BaseModel):
    text: str
    end_of_turn: bool = True

    emotional_intent: Literal[
        "neutral",
        "happy",
        "amused",
        "empathetic",
        "sad",
        "excited",
        "calm",
        "concerned",
        "reassuring",
        "curious"
    ] = "neutral"

    expression_hint: Optional[Literal[
        "laugh",
        "soft_laugh",
        "giggle",
        "sigh",
        "pause",
        "smile_in_voice",
        "warm_acknowledgment",
        "gentle_reassurance"
    ]] = None

    humanize: bool = True
