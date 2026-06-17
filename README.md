# Eburon Core

FastAPI gateway for public Eburon AI product endpoints.

## Run

```bash
python3 -m uvicorn app.main:app --reload
```

Docs are available at `http://127.0.0.1:8000/docs`.

## Vercel

This project is prepared for Vercel through `api/index.py` and `vercel.json`.

- `/playground` serves the Eburon AI Playground and is the canonical entry page.
- `/` serves the same playground page for root visitors.
- `/api` returns public API discovery metadata.
- `/docs` serves Swagger UI.
- `/redoc` serves ReDoc.
- `/openapi.json` serves the OpenAPI schema.

Set `EBURON_GOOGLE_API_KEY`, `GOOGLE_API_KEY`, or `GOOGLE_CLOUD_API_KEY` in Vercel project environment variables for live translation/OCR adapters.

## Test

```bash
python3 -m unittest discover -s tests
```
