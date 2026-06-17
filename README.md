# Eburon Core

FastAPI gateway for public Eburon AI product endpoints.

## Run

```bash
python3 -m uvicorn app.main:app --reload
```

Docs are available at `http://127.0.0.1:8000/docs`.

## Test

```bash
python3 -m unittest discover -s tests
```

