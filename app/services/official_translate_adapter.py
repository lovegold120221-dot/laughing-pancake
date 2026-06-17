import json
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.core.errors import EburonTranslateError
from app.schemas.translate import BoundingBox, ImageTextBlock

TRANSLATE_BASE_URL = "https://translation.googleapis.com/language/translate/v2"
VISION_ANNOTATE_URL = "https://vision.googleapis.com/v1/images:annotate"


def is_configured() -> bool:
    return bool(get_settings().translation_api_key)


def _post_json(url: str, payload: dict) -> dict:
    settings = get_settings()
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=settings.translation_api_timeout_seconds,
        ) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EburonTranslateError(
            "The translation request could not be completed.",
            status_code=502,
        ) from exc


def _get_json(url: str) -> dict:
    settings = get_settings()
    request = Request(url, method="GET")

    try:
        with urlopen(
            request,
            timeout=settings.translation_api_timeout_seconds,
        ) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EburonTranslateError(
            "The translation request could not be completed.",
            status_code=502,
        ) from exc


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
    text_format: str,
) -> tuple[str, str | None]:
    settings = get_settings()
    query = {"key": settings.translation_api_key}
    url = f"{TRANSLATE_BASE_URL}?{urlencode(query)}"
    body = {
        "q": text,
        "target": target_language,
        "format": text_format,
    }
    if source_language != "auto":
        body["source"] = source_language

    data = _post_json(url, body)
    translations = data.get("data", {}).get("translations", [])
    if not translations:
        raise EburonTranslateError(status_code=502)

    first = translations[0]
    translated_text = unescape(first.get("translatedText", ""))
    detected_language = first.get("detectedSourceLanguage")
    if source_language != "auto":
        detected_language = source_language

    return translated_text, detected_language


def detect_language(text: str) -> tuple[str, float]:
    settings = get_settings()
    query = {"key": settings.translation_api_key}
    url = f"{TRANSLATE_BASE_URL}/detect?{urlencode(query)}"
    data = _post_json(url, {"q": text})
    detections = data.get("data", {}).get("detections", [])
    first_group = detections[0] if detections else []
    first = first_group[0] if first_group else {}
    language = first.get("language")

    if not language:
        raise EburonTranslateError(status_code=502)

    return language, float(first.get("confidence") or 0.0)


def list_languages() -> list[dict]:
    settings = get_settings()
    query = {
        "key": settings.translation_api_key,
        "target": "en",
    }
    url = f"{TRANSLATE_BASE_URL}/languages?{urlencode(query)}"
    data = _get_json(url)
    languages = data.get("data", {}).get("languages", [])

    return [
        {
            "code": item.get("language", ""),
            "name": item.get("name") or item.get("language", ""),
        }
        for item in languages
        if item.get("language")
    ]


def _bounding_box(vertices: list[dict]) -> BoundingBox:
    xs = [int(vertex.get("x", 0)) for vertex in vertices]
    ys = [int(vertex.get("y", 0)) for vertex in vertices]
    if not xs or not ys:
        return BoundingBox(x=0, y=0, width=0, height=0)

    left = min(xs)
    top = min(ys)
    return BoundingBox(
        x=left,
        y=top,
        width=max(xs) - left,
        height=max(ys) - top,
    )


def ocr_image_blocks(image_data: str) -> list[tuple[str, BoundingBox]]:
    settings = get_settings()
    query = {"key": settings.translation_api_key}
    url = f"{VISION_ANNOTATE_URL}?{urlencode(query)}"
    body = {
        "requests": [
            {
                "image": {"content": image_data},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }
    data = _post_json(url, body)
    responses = data.get("responses", [])
    first_response = responses[0] if responses else {}
    if "error" in first_response:
        raise EburonTranslateError(status_code=502)

    annotations = first_response.get("textAnnotations", [])
    blocks = []
    for annotation in annotations[1:]:
        text = annotation.get("description", "").strip()
        if not text:
            continue
        vertices = annotation.get("boundingPoly", {}).get("vertices", [])
        blocks.append((text, _bounding_box(vertices)))

    if not blocks and annotations:
        full_text = annotations[0].get("description", "").strip()
        if full_text:
            vertices = annotations[0].get("boundingPoly", {}).get("vertices", [])
            blocks.append((full_text, _bounding_box(vertices)))

    return blocks


def translate_image_blocks(
    image_data: str,
    source_language: str,
    target_language: str,
) -> tuple[list[ImageTextBlock], str]:
    raw_blocks = ocr_image_blocks(image_data)
    translated_blocks: list[ImageTextBlock] = []
    detected_language = source_language

    for source_text, bounding_box in raw_blocks:
        translated_text, block_detected = translate_text(
            source_text,
            source_language,
            target_language,
            "text",
        )
        if source_language == "auto" and detected_language == "auto" and block_detected:
            detected_language = block_detected
        translated_blocks.append(
            ImageTextBlock(
                source_text=source_text,
                translated_text=translated_text,
                bounding_box=bounding_box,
            )
        )

    if detected_language == "auto":
        detected_language = "und"

    return translated_blocks, detected_language

