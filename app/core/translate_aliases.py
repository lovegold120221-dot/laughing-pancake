PUBLIC_TRANSLATE_MODELS = {
    "translatehuman-3.1": {
        "provider_label": "Eburon AI",
        "product": "Eburon Translate",
        "internal_text_adapter": "cloud_translation_v3",
        "internal_image_ocr_adapter": "cloud_vision_ocr",
        "type": "multimodal_translation",
        "capabilities": [
            "text_translation",
            "image_text_translation",
            "document_translation",
            "website_translation",
            "language_detection",
            "format_preservation",
            "batch_jobs",
        ],
    },
}


def resolve_translate_model(public_model: str) -> dict:
    if public_model not in PUBLIC_TRANSLATE_MODELS:
        raise ValueError(f"Unknown Eburon AI translation model alias: {public_model}")

    return PUBLIC_TRANSLATE_MODELS[public_model]


def get_public_translate_model_metadata(public_model: str) -> dict:
    data = resolve_translate_model(public_model).copy()

    # Never expose internal adapter names.
    data.pop("internal_text_adapter", None)
    data.pop("internal_image_ocr_adapter", None)

    return {
        "id": public_model,
        **data,
    }


def list_public_translate_models() -> list[dict]:
    return [
        get_public_translate_model_metadata(model_id)
        for model_id in PUBLIC_TRANSLATE_MODELS
    ]

