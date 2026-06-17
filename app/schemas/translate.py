from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class EburonTranslateBase(BaseModel):
    model: Literal["translatehuman-3.1"] = "translatehuman-3.1"
    source_language: str = "auto"
    target_language: str = Field(default="es", min_length=2)


class TextTranslateRequest(EburonTranslateBase):
    text: str = Field(min_length=1)
    format: Literal["text", "html"] = "text"
    preserve_tone: bool = True


class TextTranslateResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "Eburon Translate"
    model: str = "translatehuman-3.1"
    source_language: str
    target_language: str
    translated_text: str
    detected_language: str | None = None


class ImagePayload(BaseModel):
    mime_type: Literal["image/png", "image/jpeg", "image/webp"]
    data: str = Field(min_length=1)


class BoundingBox(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=0)
    height: int = Field(ge=0)


class ImageTextBlock(BaseModel):
    source_text: str
    translated_text: str
    bounding_box: BoundingBox


class ImageTranslateRequest(EburonTranslateBase):
    image: ImagePayload
    output_mode: Literal[
        "text_only",
        "text_blocks",
        "overlay_data",
        "translated_image_job",
    ] = "text_blocks"


class ImageTranslateResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "Eburon Translate"
    model: str = "translatehuman-3.1"
    source_language: str
    target_language: str
    status: str
    output_mode: str
    blocks: list[ImageTextBlock] = Field(default_factory=list)
    translated_text: str | None = None
    job_id: str | None = None


class DocumentPayload(BaseModel):
    filename: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    data: str = Field(min_length=1)


class DocumentTranslateRequest(EburonTranslateBase):
    document: DocumentPayload
    preserve_layout: bool = True


class DocumentTranslateResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "Eburon Translate"
    model: str = "translatehuman-3.1"
    job_id: str
    status: str
    source_language: str
    target_language: str


class WebsiteTranslateRequest(EburonTranslateBase):
    url: HttpUrl
    mode: Literal["single_page", "crawl_same_domain", "html_snippet"] = "single_page"
    preserve_links: bool = True
    preserve_html_structure: bool = True


class WebsiteTranslateResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "Eburon Translate"
    model: str = "translatehuman-3.1"
    website_job_id: str
    status: str
    source_language: str
    target_language: str
    preview_url: str


class DetectLanguageRequest(BaseModel):
    model: Literal["translatehuman-3.1"] = "translatehuman-3.1"
    text: str = Field(min_length=1)


class DetectLanguageResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "Eburon Translate"
    model: str = "translatehuman-3.1"
    detected_language: str
    confidence: float = Field(ge=0.0, le=1.0)


class TranslateJobResponse(BaseModel):
    provider: str = "Eburon AI"
    product: str = "Eburon Translate"
    model: str = "translatehuman-3.1"
    job_id: str
    status: str
    kind: str
    source_language: str
    target_language: str

