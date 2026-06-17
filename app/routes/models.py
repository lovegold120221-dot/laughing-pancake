# app/routes/models.py

from fastapi import APIRouter, HTTPException
from app.core.model_aliases import PUBLIC_MODEL_ALIASES, get_public_model_metadata
from app.core.translate_aliases import PUBLIC_TRANSLATE_MODELS, get_public_translate_model_metadata

router = APIRouter(
    prefix="/v1/eburon/models",
    tags=["Eburon AI Models"]
)


@router.get("")
@router.get("/")
async def list_models():
    models = []

    # TalkHuman models
    for model_id in PUBLIC_MODEL_ALIASES:
        metadata = get_public_model_metadata(model_id)
        models.append({
            "id": model_id,
            "family": metadata.get("product"),
            "type": "realtime_expressive_voice",
            "default_voice": metadata.get("default_voice"),
            "capabilities": metadata.get("capabilities")
        })

    # Translate models
    for model_id in PUBLIC_TRANSLATE_MODELS:
        metadata = get_public_translate_model_metadata(model_id)
        models.append({
            "id": model_id,
            "family": metadata.get("product"),
            "type": "multimodal_translation",
            "capabilities": metadata.get("capabilities")
        })

    return {
        "provider": "Eburon AI",
        "models": models
    }


@router.get("/{model_id}")
async def get_model(model_id: str):
    if model_id in PUBLIC_MODEL_ALIASES:
        metadata = get_public_model_metadata(model_id)
        return {
            "id": model_id,
            "provider": "Eburon AI",
            "family": metadata.get("product"),
            "type": "realtime_expressive_voice",
            "default_voice": metadata.get("default_voice"),
            "capabilities": metadata.get("capabilities")
        }
    elif model_id in PUBLIC_TRANSLATE_MODELS:
        metadata = get_public_translate_model_metadata(model_id)
        return {
            "id": model_id,
            "provider": "Eburon AI",
            "family": metadata.get("product"),
            "type": "multimodal_translation",
            "capabilities": metadata.get("capabilities")
        }
    else:
        raise HTTPException(
            status_code=404,
            detail={
                "provider": "Eburon AI",
                "error": {
                    "code": "EBURON_MODEL_NOT_FOUND",
                    "message": "The requested Eburon AI model alias was not found.",
                },
            },
        )
