import base64
import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TranslateApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_models_are_publicly_branded(self) -> None:
        response = self.client.get("/v1/eburon/translate/models")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["product"], "Eburon Translate")
        self.assertEqual(payload["models"][0]["id"], "translatehuman-3.1")
        self.assertNotIn("internal_text_adapter", json.dumps(payload))
        self.assertNotIn("internal_image_ocr_adapter", json.dumps(payload))

    def test_combined_model_index_lists_public_aliases(self) -> None:
        response = self.client.get("/v1/eburon/models")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        model_ids = {model["id"] for model in payload["models"]}

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertIn("talkhuman-3.1", model_ids)
        self.assertIn("translatehuman-3.1", model_ids)
        self.assertNotIn("gemini", json.dumps(payload).casefold())
        self.assertNotIn("cloud_translation_v3", json.dumps(payload).casefold())

    def test_talkhuman_session_is_publicly_branded(self) -> None:
        response = self.client.post(
            "/v1/eburon/talkhuman/sessions",
            json={"model": "talkhuman-3.1", "voice_name": "Superman"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["product"], "TalkHuman")
        self.assertEqual(payload["model"], "talkhuman-3.1")
        self.assertEqual(payload["voice_name"], "Superman")
        self.assertNotIn("gemini", json.dumps(payload).casefold())

    def test_talkhuman_voices_are_public_aliases(self) -> None:
        response = self.client.get("/v1/eburon/talkhuman/voices")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        aliases = {voice["alias"] for voice in payload["voices"]}
        text = json.dumps(payload).casefold()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["product"], "TalkHuman")
        self.assertEqual(payload["count"], 30)
        self.assertIn("Superman", aliases)
        self.assertIn("Batman", aliases)
        self.assertIn("Phoenix", aliases)
        for private_voice in ("zephyr", "puck", "charon", "aoede", "sulafat"):
            self.assertNotIn(private_voice, text)

    def test_roleplay_session_accepts_public_voice_alias(self) -> None:
        response = self.client.post(
            "/v1/eburon/talkhuman/roleplay/sessions",
            json={
                "model": "talkhuman-3.1",
                "voice_name": "Batman",
                "roleplay_mode": "cinematic_live_monologue",
                "output_mode": "audio_with_text_events",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["feature"], "RolePlay")
        self.assertEqual(payload["voice_name"], "Batman")
        self.assertNotIn("charon", json.dumps(payload).casefold())

    def test_translate_languages_include_full_dropdowns(self) -> None:
        response = self.client.get("/v1/eburon/translate/languages")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        source_codes = {language["code"] for language in payload["source_languages"]}
        target_codes = {language["code"] for language in payload["target_languages"]}

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertGreaterEqual(payload["source_count"], 240)
        self.assertGreaterEqual(payload["target_count"], 240)
        self.assertIn("auto", source_codes)
        self.assertIn("es", target_codes)
        self.assertIn("zh-CN", target_codes)
        self.assertIn("zh-TW", target_codes)

    def test_translate_languages_do_not_shrink_when_backend_is_configured(self) -> None:
        with (
            patch(
                "app.services.official_translate_adapter.is_configured",
                return_value=True,
            ),
            patch(
                "app.services.official_translate_adapter.list_languages",
                return_value=[{"code": "en", "name": "English"}],
            ),
        ):
            response = self.client.get("/v1/eburon/translate/languages")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        target_codes = {language["code"] for language in payload["target_languages"]}

        self.assertGreaterEqual(payload["target_count"], 240)
        self.assertIn("zh-CN", target_codes)
        self.assertIn("zh-TW", target_codes)
        self.assertIn("yua", target_codes)

    def test_playground_voice_dropdown_uses_alias_labels(self) -> None:
        with open("app/static/playground/playground.js", encoding="utf-8") as file:
            script = file.read()

        self.assertIn("value: voice.alias", script)
        self.assertIn("label: `${voice.alias}", script)
        self.assertNotIn("label: `${voice.display_name}", script)

    def test_root_is_playground_entry_page(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("Eburon AI Playground", response.text)
        self.assertIn('href="/docs"', response.text)
        self.assertIn('href="/api"', response.text)
        self.assertIn('href="/openapi.json"', response.text)
        self.assertIn('href="/playground"', response.text)
        self.assertIn("Swagger UI", response.text)

    def test_playground_route_is_canonical_entry_page(self) -> None:
        response = self.client.get("/playground")
        self.assertEqual(response.status_code, 200)

        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("Eburon AI Playground", response.text)
        self.assertIn('id="talkhumanVoice"', response.text)
        self.assertIn('id="translateTarget"', response.text)

    def test_api_discovery_is_linked_separately(self) -> None:
        response = self.client.get("/api")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["playground"], "/playground")
        self.assertEqual(payload["docs"], "/docs")

    def test_favicon_does_not_return_translate_error(self) -> None:
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")

    def test_unknown_non_translate_route_uses_api_error(self) -> None:
        response = self.client.get("/missing")
        self.assertEqual(response.status_code, 404)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["error"]["code"], "EBURON_API_NOT_FOUND")
        self.assertNotIn("product", payload)
        self.assertNotIn("translatehuman-3.1", json.dumps(payload))

    def test_unknown_translate_route_uses_translate_not_found(self) -> None:
        response = self.client.get("/v1/eburon/translate/missing")
        self.assertEqual(response.status_code, 404)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["product"], "Eburon Translate")
        self.assertEqual(payload["model"], "translatehuman-3.1")
        self.assertEqual(payload["error"]["code"], "EBURON_TRANSLATE_NOT_FOUND")

    def test_text_translation(self) -> None:
        response = self.client.post(
            "/v1/eburon/translate/text",
            json={
                "model": "translatehuman-3.1",
                "source_language": "en",
                "target_language": "es",
                "text": "Hello, how are you?",
                "format": "text",
                "preserve_tone": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["translated_text"], "Hola, ¿cómo estás?")
        self.assertEqual(payload["detected_language"], "en")

    def test_text_translation_uses_configured_official_adapter(self) -> None:
        with (
            patch(
                "app.services.official_translate_adapter.is_configured",
                return_value=True,
            ),
            patch(
                "app.services.official_translate_adapter.translate_text",
                return_value=("Buenos días", "en"),
            ) as translate_text,
        ):
            response = self.client.post(
                "/v1/eburon/translate/text",
                json={
                    "model": "translatehuman-3.1",
                    "source_language": "auto",
                    "target_language": "es",
                    "text": "Good morning",
                    "format": "text",
                    "preserve_tone": True,
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["translated_text"], "Buenos días")
        self.assertEqual(payload["detected_language"], "en")
        translate_text.assert_called_once_with(
            "Good morning",
            "auto",
            "es",
            "text",
        )

    def test_language_detection(self) -> None:
        response = self.client.post(
            "/v1/eburon/translate/detect",
            json={"model": "translatehuman-3.1", "text": "Hola, ¿cómo estás?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["detected_language"], "es")
        self.assertGreater(payload["confidence"], 0.9)

    def test_image_rejects_invalid_base64_with_public_error(self) -> None:
        response = self.client.post(
            "/v1/eburon/translate/images",
            json={
                "model": "translatehuman-3.1",
                "source_language": "auto",
                "target_language": "es",
                "image": {"mime_type": "image/png", "data": "not-base64"},
                "output_mode": "text_blocks",
            },
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()

        self.assertEqual(payload["provider"], "Eburon AI")
        self.assertEqual(payload["product"], "Eburon Translate")
        self.assertEqual(payload["error"]["code"], "EBURON_TRANSLATE_ERROR")
        self.assertNotIn("cloud", json.dumps(payload).casefold())

    def test_document_job_and_download(self) -> None:
        encoded_document = base64.b64encode(b"Hello, how are you?").decode("ascii")
        response = self.client.post(
            "/v1/eburon/translate/documents",
            json={
                "model": "translatehuman-3.1",
                "source_language": "en",
                "target_language": "es",
                "document": {
                    "filename": "contract.txt",
                    "mime_type": "text/plain",
                    "data": encoded_document,
                },
                "preserve_layout": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        job_id = response.json()["job_id"]

        job_response = self.client.get(f"/v1/eburon/translate/jobs/{job_id}")
        self.assertEqual(job_response.status_code, 200)
        self.assertEqual(job_response.json()["status"], "completed")

        download_response = self.client.get(
            f"/v1/eburon/translate/documents/{job_id}/download"
        )
        self.assertEqual(download_response.status_code, 200)
        self.assertIn(b"Eburon Translate output", download_response.content)

    def test_website_job_preview(self) -> None:
        response = self.client.post(
            "/v1/eburon/translate/websites",
            json={
                "model": "translatehuman-3.1",
                "source_language": "en",
                "target_language": "es",
                "url": "https://example.com",
                "mode": "single_page",
                "preserve_links": True,
                "preserve_html_structure": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        preview_response = self.client.get(payload["preview_url"])
        self.assertEqual(preview_response.status_code, 200)
        self.assertIn("text/html", preview_response.headers["content-type"])
        self.assertIn("example.com", preview_response.text)

    def test_openapi_has_no_backend_provider_leaks(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        openapi_text = json.dumps(response.json()).casefold()

        for banned in (
            "gemini",
            "google",
            "cloud_translation_v3",
            "cloud_vision_ocr",
            "internal_text_adapter",
            "internal_image_ocr_adapter",
        ):
            self.assertNotIn(banned, openapi_text)


if __name__ == "__main__":
    unittest.main()
