Yes, Master E — add this as a second rebranded product family under **Eburon AI**, covering the same Google Translate modes: **text**, **images**, **documents**, and **websites**. Use an official backend adapter instead of scraping the public Translate UI; text/document translation maps cleanly to Cloud Translation, while image translation should be handled as OCR + translation. Google’s docs describe Cloud Translation as a programmatic translation API for apps/websites, and Cloud Vision supports OCR/text detection from images. ([Google Cloud Documentation][1])

````md id="eburon-translate-todo"
# TODO Add-on — Eburon AI Translate API

## 1. Public rebrand identity

Public-facing API must expose only:

- Provider: Eburon AI
- Product: Eburon Translate
- Public model alias: translatehuman-3.1
- Endpoint family: Translate

Internal provider names must not appear in:

- Swagger UI
- OpenAPI examples
- frontend labels
- public response payloads
- public error messages
- browser logs
- client-side code

Internal routing can use official translation/OCR/document services, but public API should stay fully Eburon-branded.

---

## 2. URL mode mapping

The original modes map like this:

| Original Translate mode | New Eburon API endpoint |
|---|---|
| Text translate | POST /v1/eburon/translate/text |
| Image translate | POST /v1/eburon/translate/images |
| Document translate | POST /v1/eburon/translate/documents |
| Website translate | POST /v1/eburon/translate/websites |

Final public endpoint family:

```txt
/v1/eburon/translate/*
````

---

## 3. Add model alias mapping

Create:

```txt
app/core/translate_aliases.py
```

```python id="translate_aliases_py"
# app/core/translate_aliases.py

PUBLIC_TRANSLATE_MODELS = {
    "translatehuman-3.1": {
        "provider_label": "Eburon AI",
        "product": "Eburon Translate",
        "internal_text_adapter": "cloud_translation_v3",
        "internal_image_ocr_adapter": "cloud_vision_ocr",
        "capabilities": [
            "text_translation",
            "image_text_translation",
            "document_translation",
            "website_translation",
            "language_detection",
            "format_preservation",
            "batch_jobs"
        ],
    }
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
```

---

## 4. Add public model endpoints

```txt
GET /v1/eburon/translate/models
GET /v1/eburon/translate/models/translatehuman-3.1
```

Response:

```json id="translate_model_response"
{
  "provider": "Eburon AI",
  "product": "Eburon Translate",
  "models": [
    {
      "id": "translatehuman-3.1",
      "type": "multimodal_translation",
      "capabilities": [
        "text_translation",
        "image_text_translation",
        "document_translation",
        "website_translation",
        "language_detection",
        "format_preservation",
        "batch_jobs"
      ]
    }
  ]
}
```

---

## 5. Final endpoint list

```txt id="translate_endpoint_list"
GET     /v1/eburon/translate/models
GET     /v1/eburon/translate/models/translatehuman-3.1
GET     /v1/eburon/translate/languages

POST    /v1/eburon/translate/detect
POST    /v1/eburon/translate/text
POST    /v1/eburon/translate/images
POST    /v1/eburon/translate/documents
POST    /v1/eburon/translate/websites

GET     /v1/eburon/translate/jobs/{job_id}
DELETE  /v1/eburon/translate/jobs/{job_id}

GET     /v1/eburon/translate/documents/{document_id}/download
GET     /v1/eburon/translate/websites/{website_job_id}/preview
```

---

## 6. Text translation endpoint

```txt
POST /v1/eburon/translate/text
```

Request:

```json id="translate_text_request"
{
  "model": "translatehuman-3.1",
  "source_language": "en",
  "target_language": "es",
  "text": "Hello, how are you?",
  "format": "text",
  "preserve_tone": true
}
```

Response:

```json id="translate_text_response"
{
  "provider": "Eburon AI",
  "product": "Eburon Translate",
  "model": "translatehuman-3.1",
  "source_language": "en",
  "target_language": "es",
  "translated_text": "Hola, ¿cómo estás?",
  "detected_language": "en"
}
```

---

## 7. Image translation endpoint

```txt
POST /v1/eburon/translate/images
```

Purpose:

* Accept uploaded image or base64 image.
* Extract visible text using OCR.
* Translate detected text.
* Optionally return:

  * translated text only
  * bounding boxes
  * overlay-ready data
  * generated translated image later

Request:

```json id="translate_image_request"
{
  "model": "translatehuman-3.1",
  "source_language": "auto",
  "target_language": "es",
  "image": {
    "mime_type": "image/png",
    "data": "base64_image_here"
  },
  "output_mode": "text_blocks"
}
```

Response:

```json id="translate_image_response"
{
  "provider": "Eburon AI",
  "product": "Eburon Translate",
  "model": "translatehuman-3.1",
  "source_language": "en",
  "target_language": "es",
  "blocks": [
    {
      "source_text": "Open",
      "translated_text": "Abierto",
      "bounding_box": {
        "x": 120,
        "y": 80,
        "width": 220,
        "height": 60
      }
    }
  ]
}
```

Supported `output_mode` values:

```txt
text_only
text_blocks
overlay_data
translated_image_job
```

---

## 8. Document translation endpoint

```txt
POST /v1/eburon/translate/documents
```

Purpose:

* Upload PDF, DOCX, PPTX, XLSX, TXT, HTML, or Markdown.
* Translate document.
* Preserve formatting where possible.
* Return a `job_id` because document translation can be async.

Request:

```json id="translate_doc_request"
{
  "model": "translatehuman-3.1",
  "source_language": "en",
  "target_language": "es",
  "document": {
    "filename": "contract.pdf",
    "mime_type": "application/pdf",
    "data": "base64_document_here"
  },
  "preserve_layout": true
}
```

Response:

```json id="translate_doc_response"
{
  "provider": "Eburon AI",
  "product": "Eburon Translate",
  "model": "translatehuman-3.1",
  "job_id": "trdoc_01JXYZ123",
  "status": "processing",
  "source_language": "en",
  "target_language": "es"
}
```

Download translated document:

```txt
GET /v1/eburon/translate/documents/{document_id}/download
```

---

## 9. Website translation endpoint

```txt
POST /v1/eburon/translate/websites
```

Purpose:

* Accept a website URL.
* Fetch page content server-side.
* Translate visible HTML text.
* Preserve links, structure, and basic formatting.
* Return translated HTML or a preview URL.

Request:

```json id="translate_website_request"
{
  "model": "translatehuman-3.1",
  "source_language": "en",
  "target_language": "es",
  "url": "https://example.com",
  "mode": "single_page",
  "preserve_links": true,
  "preserve_html_structure": true
}
```

Response:

```json id="translate_website_response"
{
  "provider": "Eburon AI",
  "product": "Eburon Translate",
  "model": "translatehuman-3.1",
  "website_job_id": "trweb_01JXYZ123",
  "status": "completed",
  "source_language": "en",
  "target_language": "es",
  "preview_url": "/v1/eburon/translate/websites/trweb_01JXYZ123/preview"
}
```

Supported website modes:

```txt
single_page
crawl_same_domain
html_snippet
```

---

## 10. Language detection endpoint

```txt
POST /v1/eburon/translate/detect
```

Request:

```json id="detect_language_request"
{
  "model": "translatehuman-3.1",
  "text": "Hola, ¿cómo estás?"
}
```

Response:

```json id="detect_language_response"
{
  "provider": "Eburon AI",
  "product": "Eburon Translate",
  "model": "translatehuman-3.1",
  "detected_language": "es",
  "confidence": 0.97
}
```

---

## 11. Pydantic schemas

Create:

```txt
app/schemas/translate.py
```

```python id="translate_schemas_py"
from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


class EburonTranslateBase(BaseModel):
    model: Literal["translatehuman-3.1"] = "translatehuman-3.1"
    source_language: str = "auto"
    target_language: str = Field(default="es", min_length=2)


class TextTranslateRequest(EburonTranslateBase):
    text: str
    format: Literal["text", "html"] = "text"
    preserve_tone: bool = True


class TextTranslateResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "Eburon Translate"
    model: str = "translatehuman-3.1"
    source_language: str
    target_language: str
    translated_text: str
    detected_language: Optional[str] = None


class ImagePayload(BaseModel):
    mime_type: Literal["image/png", "image/jpeg", "image/webp"]
    data: str


class ImageTranslateRequest(EburonTranslateBase):
    image: ImagePayload
    output_mode: Literal[
        "text_only",
        "text_blocks",
        "overlay_data",
        "translated_image_job"
    ] = "text_blocks"


class DocumentPayload(BaseModel):
    filename: str
    mime_type: str
    data: str


class DocumentTranslateRequest(EburonTranslateBase):
    document: DocumentPayload
    preserve_layout: bool = True


class WebsiteTranslateRequest(EburonTranslateBase):
    url: HttpUrl
    mode: Literal["single_page", "crawl_same_domain", "html_snippet"] = "single_page"
    preserve_links: bool = True
    preserve_html_structure: bool = True


class DetectLanguageRequest(BaseModel):
    model: Literal["translatehuman-3.1"] = "translatehuman-3.1"
    text: str
```

---

## 12. Route file

Create:

```txt
app/routes/eburon_translate.py
```

```python id="eburon_translate_routes_py"
from fastapi import APIRouter, HTTPException
from app.schemas.translate import (
    TextTranslateRequest,
    TextTranslateResponse,
    ImageTranslateRequest,
    DocumentTranslateRequest,
    WebsiteTranslateRequest,
    DetectLanguageRequest,
)

router = APIRouter(
    prefix="/v1/eburon/translate",
    tags=["Eburon AI Translate"]
)


@router.get("/models")
async def list_translate_models():
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "models": [
            {
                "id": "translatehuman-3.1",
                "type": "multimodal_translation",
                "capabilities": [
                    "text_translation",
                    "image_text_translation",
                    "document_translation",
                    "website_translation",
                    "language_detection",
                    "format_preservation",
                    "batch_jobs"
                ]
            }
        ]
    }


@router.get("/models/translatehuman-3.1")
async def get_translate_model():
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "id": "translatehuman-3.1",
        "type": "multimodal_translation",
        "status": "available"
    }


@router.post("/detect")
async def detect_language(payload: DetectLanguageRequest):
    # TODO:
    # - route to internal language detection adapter
    # - never expose internal provider name
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "detected_language": "auto_detected_language_here",
        "confidence": 0.0
    }


@router.post("/text", response_model=TextTranslateResponse)
async def translate_text(payload: TextTranslateRequest):
    # TODO:
    # - resolve translatehuman-3.1 internally
    # - call internal translation adapter
    # - return Eburon-branded response only
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "source_language": payload.source_language,
        "target_language": payload.target_language,
        "translated_text": "translated_text_here",
        "detected_language": None
    }


@router.post("/images")
async def translate_image(payload: ImageTranslateRequest):
    # TODO:
    # - validate base64 image
    # - OCR image text
    # - translate detected text
    # - return text blocks / overlay data / image job
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "status": "processed",
        "output_mode": payload.output_mode,
        "blocks": []
    }


@router.post("/documents")
async def translate_document(payload: DocumentTranslateRequest):
    # TODO:
    # - upload/store original document
    # - create async translation job
    # - preserve layout when possible
    # - return job_id
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "job_id": "trdoc_dev_job",
        "status": "processing"
    }


@router.post("/websites")
async def translate_website(payload: WebsiteTranslateRequest):
    # TODO:
    # - fetch URL server-side
    # - sanitize HTML
    # - extract visible text nodes
    # - translate text nodes
    # - rebuild translated HTML
    # - return preview URL or translated HTML
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "website_job_id": "trweb_dev_job",
        "status": "processing"
    }


@router.get("/jobs/{job_id}")
async def get_translate_job(job_id: str):
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": "translatehuman-3.1",
        "job_id": job_id,
        "status": "processing"
    }


@router.delete("/jobs/{job_id}")
async def cancel_translate_job(job_id: str):
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": "translatehuman-3.1",
        "job_id": job_id,
        "status": "cancelled"
    }
```

---

## 13. Update main app

```python id="main_translate_update_py"
# app/main.py

from fastapi import FastAPI
from app.routes import health
from app.routes import talkhuman
from app.routes import eburon_translate

app = FastAPI(
    title="Eburon AI API",
    version="1.0.0",
    description="""
Eburon AI unified API gateway.

Products:
- TalkHuman-3.1: realtime expressive human-like voice API.
- TranslateHuman-3.1: multimodal translation API for text, images, documents, and websites.

All public model names are Eburon AI aliases.
""",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(health.router)
app.include_router(talkhuman.router)
app.include_router(eburon_translate.router)
```

---

## 14. Swagger/OpenAPI tags

```python id="translate_openapi_tags"
openapi_tags = [
    {
        "name": "Eburon AI TalkHuman",
        "description": "Realtime expressive voice endpoints using talkhuman-3.1."
    },
    {
        "name": "Eburon AI Translate",
        "description": "Multimodal translation endpoints using translatehuman-3.1 for text, images, documents, and websites."
    },
    {
        "name": "Health",
        "description": "Server health and readiness checks."
    }
]
```

---

## 15. Public error format

Every translation error should look like this:

```json id="translate_error_format"
{
  "provider": "Eburon AI",
  "product": "Eburon Translate",
  "model": "translatehuman-3.1",
  "error": {
    "code": "EBURON_TRANSLATE_ERROR",
    "message": "The translation request could not be completed."
  }
}
```

Never return raw provider exceptions to the frontend.

---

## 16. Build order

```txt id="translate_build_order"
Phase 1:
- Add translate_aliases.py
- Add schemas/translate.py
- Add routes/eburon_translate.py
- Register router in app/main.py

Phase 2:
- Implement /text
- Implement /detect
- Add Swagger examples
- Export /openapi.json

Phase 3:
- Implement /images as OCR + translation
- Return text blocks and overlay data

Phase 4:
- Implement /documents as async jobs
- Add document download endpoint
- Add job polling

Phase 5:
- Implement /websites
- Add translated preview endpoint
- Add domain crawl limits
- Add HTML sanitizer

Phase 6:
- Lock branding
- Remove internal provider names from OpenAPI
- Add auth, rate limits, logging, and payload caps
```

Final clean public product set:

```txt id="final_eburon_products"
Eburon AI TalkHuman
Model: talkhuman-3.1
Base: /v1/eburon/talkhuman

Eburon AI Translate
Model: translatehuman-3.1
Base: /v1/eburon/translate
```

[1]: https://docs.cloud.google.com/translate/docs?utm_source=chatgpt.com "Cloud Translation documentation | Google Cloud Documentation"
