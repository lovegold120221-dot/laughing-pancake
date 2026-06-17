# app/core/model_aliases.py

PUBLIC_MODEL_ALIASES = {
    "talkhuman-3.1": {
        "provider_label": "Eburon AI",
        "product": "TalkHuman",
        "internal_model": "models/gemini-3.1-flash-live-preview",
        "response_modalities": ["AUDIO"],
        "default_voice": "Phoenix",
        "capabilities": [
            "realtime_voice",
            "human_expression",
            "emotional_nuance",
            "audio_input",
            "vision_input",
            "screen_context",
            "natural_interruptions"
        ],
    }
}


def resolve_public_model(public_model: str) -> str:
    if public_model not in PUBLIC_MODEL_ALIASES:
        raise ValueError(f"Unknown Eburon AI model alias: {public_model}")

    return PUBLIC_MODEL_ALIASES[public_model]["internal_model"]


def get_public_model_metadata(public_model: str) -> dict:
    if public_model not in PUBLIC_MODEL_ALIASES:
        raise ValueError(f"Unknown Eburon AI model alias: {public_model}")

    data = PUBLIC_MODEL_ALIASES[public_model].copy()
    data.pop("internal_model", None)
    return data
