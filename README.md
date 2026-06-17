# Eburon Core

FastAPI gateway for public Eburon AI product endpoints.

## Run

```bash
python3 -m uvicorn app.main:app --reload
```

Docs are available at `http://127.0.0.1:8000/docs`.

## Vercel

This project is prepared for Vercel through `api/index.py` and `vercel.json`.

- `/` serves the Eburon AI Playground.
- `/playground` is an alias for the same page.
- `/api` returns public API discovery metadata.
- `/docs` serves Swagger UI.
- `/redoc` serves ReDoc.
- `/openapi.json` serves the OpenAPI schema.

Set `GOOGLE_API_KEY` or `EBURON_GOOGLE_API_KEY` in Vercel project environment variables for live translation/OCR adapters.

## Test

```bash
python3 -m unittest discover -s tests
```
