from typing import Literal, Optional
from pydantic import BaseModel, Field


class RolePlayPerformanceProfile(BaseModel):
    duration_minutes: float = Field(default=5.0, ge=0.5, le=15.0)
    target_words_min: int = Field(default=650, ge=100, le=3000)
    target_words_max: int = Field(default=800, ge=100, le=3500)

    emotional_intensity: float = Field(default=0.75, ge=0.0, le=1.0)
    cinematic_detail: float = Field(default=0.85, ge=0.0, le=1.0)
    human_pause_level: float = Field(default=0.55, ge=0.0, le=1.0)
    performance_cue_level: float = Field(default=0.35, ge=0.0, le=1.0)
    character_commitment: float = Field(default=0.95, ge=0.0, le=1.0)


class RolePlaySessionCreateRequest(BaseModel):
    model: Literal["talkhuman-3.1"] = "talkhuman-3.1"
    voice_name: str = "Batman"

    roleplay_mode: Literal[
        "cinematic_live_monologue",
        "character_scene",
        "narrator",
        "villain",
        "hero",
        "teacher",
        "business_pitch",
        "horror",
        "comedy",
        "confession",
        "survivor",
        "spy_message"
    ] = "cinematic_live_monologue"

    output_mode: Literal[
        "audio_only",
        "audio_with_text_events",
        "text_only"
    ] = "audio_with_text_events"

    performance_profile: RolePlayPerformanceProfile = Field(default_factory=RolePlayPerformanceProfile)
    safety_mode: Literal["standard", "strict"] = "standard"
    metadata: dict = Field(default_factory=dict)


class RolePlaySessionCreateResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "TalkHuman"
    feature: str = "RolePlay"
    model: str = "talkhuman-3.1"
    voice_name: str = "Batman"
    session_id: str
    status: str
    created_at: str


class RolePlayPerformRequest(BaseModel):
    topic_or_roleplay_request: str

    tone: Literal[
        "auto",
        "dramatic",
        "comedy",
        "horror",
        "business",
        "educational",
        "villain",
        "hero",
        "cinematic",
        "emotional",
        "calm"
    ] = "auto"

    start_immediately_in_character: bool = True
    allow_performance_cues: bool = True
    end_of_turn: bool = True


class RolePlayContinueRequest(BaseModel):
    instruction: Optional[str] = "continue"
    resume_from_last_emotional_point: bool = True


class RolePlayChangeSceneRequest(BaseModel):
    new_topic_or_roleplay_request: str
    transition_style: Literal[
        "smooth",
        "hard_cut",
        "cinematic_shift",
        "character_adapts"
    ] = "smooth"
