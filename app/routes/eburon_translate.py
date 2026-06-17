from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

from app.core.errors import EburonTranslateError
from app.core.translate_aliases import (
    get_public_translate_model_metadata,
    list_public_translate_models,
)
from app.schemas.translate import (
    DetectLanguageRequest,
    DetectLanguageResponse,
    DocumentTranslateRequest,
    DocumentTranslateResponse,
    ImageTranslateRequest,
    ImageTranslateResponse,
    TextTranslateRequest,
    TextTranslateResponse,
    TranslateJobResponse,
    WebsiteTranslateRequest,
    WebsiteTranslateResponse,
)
from app.services.translate_service import (
    create_document_job,
    create_website_job,
    detect_language as detect_language_value,
    job_payload,
    list_languages,
    store,
    translate_image,
    translate_text,
)

router = APIRouter(
    prefix="/v1/eburon/translate",
    tags=["Eburon AI Translate"],
)


@router.get("/models")
async def list_translate_models() -> dict:
    models = [
        {
            "id": model["id"],
            "type": model["type"],
            "capabilities": model["capabilities"],
        }
        for model in list_public_translate_models()
    ]
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "models": models,
    }


@router.get("/models/{model_id}")
async def get_translate_model(model_id: str) -> dict:
    try:
        model = get_public_translate_model_metadata(model_id)
    except ValueError as exc:
        raise EburonTranslateError(
            "Unknown Eburon AI translation model alias.",
            status_code=404,
        ) from exc

    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "id": model["id"],
        "type": model["type"],
        "capabilities": model["capabilities"],
        "status": "available",
    }


@router.get("/languages")
async def get_translate_languages() -> dict:
    return list_languages()


@router.post("/detect", response_model=DetectLanguageResponse)
async def detect_language(payload: DetectLanguageRequest) -> dict:
    language, confidence = detect_language_value(payload.text)
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "detected_language": language,
        "confidence": confidence,
    }


@router.post("/text", response_model=TextTranslateResponse)
async def translate_text_endpoint(payload: TextTranslateRequest) -> dict:
    return translate_text(payload)


@router.post("/images", response_model=ImageTranslateResponse)
async def translate_image_endpoint(payload: ImageTranslateRequest) -> dict:
    return translate_image(payload)


@router.post("/documents", response_model=DocumentTranslateResponse)
async def translate_document(payload: DocumentTranslateRequest) -> dict:
    return create_document_job(payload)


@router.post("/websites", response_model=WebsiteTranslateResponse)
async def translate_website(payload: WebsiteTranslateRequest) -> dict:
    return create_website_job(payload)


@router.get("/jobs/{job_id}", response_model=TranslateJobResponse)
async def get_translate_job(job_id: str) -> dict:
    return job_payload(store.get(job_id))


@router.delete("/jobs/{job_id}", response_model=TranslateJobResponse)
async def cancel_translate_job(job_id: str) -> dict:
    return job_payload(store.cancel(job_id))


@router.get("/documents/{document_id}/download")
async def download_translated_document(document_id: str) -> Response:
    job = store.get(document_id)
    if job.kind != "document" or job.content is None:
        raise EburonTranslateError("Translated document was not found.", status_code=404)
    if job.status == "cancelled":
        raise EburonTranslateError("Translated document is no longer available.", status_code=409)

    filename = job.filename or f"{document_id}.txt"
    return Response(
        content=job.content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="translated-{filename}"',
            "X-Eburon-Provider": "Eburon AI",
            "X-Eburon-Product": "Eburon Translate",
        },
    )


@router.get("/websites/{website_job_id}/preview", response_class=HTMLResponse)
async def preview_translated_website(website_job_id: str) -> HTMLResponse:
    job = store.get(website_job_id)
    if job.kind != "website" or job.preview_html is None:
        raise EburonTranslateError("Translated website preview was not found.", status_code=404)
    if job.status == "cancelled":
        raise EburonTranslateError("Translated website preview is no longer available.", status_code=409)

    return HTMLResponse(job.preview_html)

