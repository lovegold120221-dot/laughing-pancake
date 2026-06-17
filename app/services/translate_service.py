import base64
import binascii
import html
from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import count
from urllib.parse import urlparse

from app.core.errors import EburonTranslateError
from app.core.translate_languages import language_dropdown_payload
from app.schemas.translate import (
    BoundingBox,
    DocumentTranslateRequest,
    ImageTextBlock,
    ImageTranslateRequest,
    TextTranslateRequest,
    WebsiteTranslateRequest,
)
from app.services import official_translate_adapter

SUPPORTED_LANGUAGES = [
    {"code": "auto", "name": "Auto detect"},
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "it", "name": "Italian"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "zh", "name": "Chinese"},
]

_TEXT_TRANSLATIONS = {
    ("en", "es", "hello, how are you?"): "Hola, ¿cómo estás?",
    ("en", "fr", "hello, how are you?"): "Bonjour, comment allez-vous ?",
    ("en", "de", "hello, how are you?"): "Hallo, wie geht es dir?",
    ("en", "it", "hello, how are you?"): "Ciao, come stai?",
    ("en", "pt", "hello, how are you?"): "Olá, como vai?",
    ("es", "en", "hola, ¿cómo estás?"): "Hello, how are you?",
    ("es", "en", "hola, como estas?"): "Hello, how are you?",
    ("en", "es", "open"): "Abierto",
    ("en", "fr", "open"): "Ouvert",
    ("en", "de", "open"): "Geöffnet",
}

_LANGUAGE_MARKERS = {
    "es": ("hola", "gracias", "cómo", "como", "estás", "estas", "adiós"),
    "fr": ("bonjour", "merci", "comment", "salut"),
    "de": ("hallo", "danke", "guten", "tschüss"),
    "it": ("ciao", "grazie", "buongiorno"),
    "pt": ("olá", "ola", "obrigado", "obrigada"),
}

_DOCUMENT_COUNTER = count(1)
_WEBSITE_COUNTER = count(1)
_IMAGE_COUNTER = count(1)


@dataclass
class TranslateJob:
    job_id: str
    kind: str
    status: str
    source_language: str
    target_language: str
    created_at: str
    filename: str | None = None
    content: bytes | None = None
    preview_html: str | None = None


@dataclass
class InMemoryTranslateStore:
    jobs: dict[str, TranslateJob] = field(default_factory=dict)

    def add(self, job: TranslateJob) -> TranslateJob:
        self.jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> TranslateJob:
        if job_id not in self.jobs:
            raise EburonTranslateError("Translation job was not found.", status_code=404)
        return self.jobs[job_id]

    def cancel(self, job_id: str) -> TranslateJob:
        job = self.get(job_id)
        job.status = "cancelled"
        return job


store = InMemoryTranslateStore()


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def list_languages() -> dict:
    dropdowns = language_dropdown_payload()
    languages = dropdowns["languages"]
    source_languages = dropdowns["source_languages"]
    target_languages = dropdowns["target_languages"]

    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": "translatehuman-3.1",
        "languages": languages,
        "source_languages": source_languages,
        "target_languages": target_languages,
        "source_count": len(source_languages),
        "target_count": len(target_languages),
    }


def validate_base64(data: str, label: str) -> bytes:
    try:
        return base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise EburonTranslateError(f"The {label} payload must be valid base64.") from exc


def detect_language(text: str) -> tuple[str, float]:
    if official_translate_adapter.is_configured():
        return official_translate_adapter.detect_language(text)

    normalized = text.casefold()
    for language, markers in _LANGUAGE_MARKERS.items():
        if any(marker in normalized for marker in markers):
            return language, 0.97

    if any(ord(character) > 127 for character in text):
        return "auto", 0.55

    return "en", 0.92


def translate_text_value(
    text: str,
    source_language: str,
    target_language: str,
    *,
    text_format: str = "text",
) -> tuple[str, str]:
    detected_language = source_language
    if source_language == "auto":
        detected_language, _confidence = detect_language(text)
        if detected_language == "auto":
            detected_language = "en"

    lookup_key = (detected_language, target_language, text.strip().casefold())
    translated = _TEXT_TRANSLATIONS.get(lookup_key)
    if translated is None:
        translated = f"[{target_language}] {text}"

    if text_format == "html":
        translated = html.escape(translated)

    return translated, detected_language


def translate_text(payload: TextTranslateRequest) -> dict:
    if official_translate_adapter.is_configured():
        translated, detected_language = official_translate_adapter.translate_text(
            payload.text,
            payload.source_language,
            payload.target_language,
            payload.format,
        )
    else:
        translated, detected_language = translate_text_value(
            payload.text,
            payload.source_language,
            payload.target_language,
            text_format=payload.format,
        )

    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "source_language": detected_language or payload.source_language,
        "target_language": payload.target_language,
        "translated_text": translated,
        "detected_language": detected_language,
    }


def translate_image(payload: ImageTranslateRequest) -> dict:
    validate_base64(payload.image.data, "image")

    blocks: list[ImageTextBlock] = []
    source_language = payload.source_language
    if source_language == "auto":
        source_language = "en"

    if official_translate_adapter.is_configured():
        blocks, source_language = official_translate_adapter.translate_image_blocks(
            payload.image.data,
            payload.source_language,
            payload.target_language,
        )

    job_id = None
    translated_text = None
    if payload.output_mode == "translated_image_job":
        job_id = f"trimg_{next(_IMAGE_COUNTER):08d}"
        store.add(
            TranslateJob(
                job_id=job_id,
                kind="image",
                status="processing",
                source_language=source_language,
                target_language=payload.target_language,
                created_at=utc_now(),
            )
        )

    if payload.output_mode == "text_only":
        translated_text = "\n".join(block.translated_text for block in blocks)

    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "source_language": source_language,
        "target_language": payload.target_language,
        "status": "processed",
        "output_mode": payload.output_mode,
        "blocks": [block.model_dump() for block in blocks],
        "translated_text": translated_text,
        "job_id": job_id,
    }


def create_document_job(payload: DocumentTranslateRequest) -> dict:
    original = validate_base64(payload.document.data, "document")
    source_language = payload.source_language
    if source_language == "auto":
        source_language = "en"

    translated_note = (
        f"Eburon Translate output\n"
        f"source={source_language}\n"
        f"target={payload.target_language}\n"
        f"filename={payload.document.filename}\n"
        f"bytes={len(original)}\n"
    )
    job_id = f"trdoc_{next(_DOCUMENT_COUNTER):08d}"
    store.add(
        TranslateJob(
            job_id=job_id,
            kind="document",
            status="completed",
            source_language=source_language,
            target_language=payload.target_language,
            created_at=utc_now(),
            filename=payload.document.filename,
            content=translated_note.encode("utf-8"),
        )
    )

    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "job_id": job_id,
        "status": "completed",
        "source_language": source_language,
        "target_language": payload.target_language,
    }


def create_website_job(payload: WebsiteTranslateRequest) -> dict:
    source_language = payload.source_language
    if source_language == "auto":
        source_language = "en"

    parsed_url = urlparse(str(payload.url))
    host = parsed_url.netloc or "website"
    job_id = f"trweb_{next(_WEBSITE_COUNTER):08d}"
    escaped_url = html.escape(str(payload.url))
    translated_title, _detected = translate_text_value(
        f"Translated preview for {host}",
        source_language,
        payload.target_language,
    )
    preview_html = (
        "<!doctype html><html><head>"
        "<meta charset=\"utf-8\">"
        f"<title>{html.escape(translated_title)}</title>"
        "</head><body>"
        f"<main><h1>{html.escape(translated_title)}</h1>"
        f"<p>Source URL: <a href=\"{escaped_url}\">{escaped_url}</a></p>"
        f"<p>Mode: {html.escape(payload.mode)}</p></main>"
        "</body></html>"
    )
    store.add(
        TranslateJob(
            job_id=job_id,
            kind="website",
            status="completed",
            source_language=source_language,
            target_language=payload.target_language,
            created_at=utc_now(),
            preview_html=preview_html,
        )
    )

    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": payload.model,
        "website_job_id": job_id,
        "status": "completed",
        "source_language": source_language,
        "target_language": payload.target_language,
        "preview_url": f"/v1/eburon/translate/websites/{job_id}/preview",
    }


def job_payload(job: TranslateJob) -> dict:
    return {
        "provider": "Eburon AI",
        "product": "Eburon Translate",
        "model": "translatehuman-3.1",
        "job_id": job.job_id,
        "status": job.status,
        "kind": job.kind,
        "source_language": job.source_language,
        "target_language": job.target_language,
    }
