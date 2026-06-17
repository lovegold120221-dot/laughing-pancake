from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import FileResponse
import os

from app.core.errors import (
    EburonTranslateError,
    eburon_translate_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.routes import eburon_translate, health, talkhuman, models, talkhuman_roleplay

openapi_tags = [
    {
        "name": "Eburon AI TalkHuman",
        "description": "Realtime expressive voice endpoints using talkhuman-3.1.",
    },
    {
        "name": "Eburon AI TalkHuman RolePlay",
        "description": "Cinematic realtime role-play and live monologue endpoints using talkhuman-3.1."
    },
    {
        "name": "Eburon AI Translate",
        "description": "Multimodal translation endpoints using translatehuman-3.1 for text, images, documents, and websites.",
    },
    {
        "name": "Eburon AI Models",
        "description": "Public Eburon AI model aliases and capabilities.",
    },
    {
        "name": "Health",
        "description": "Server health and readiness checks.",
    },
]

app = FastAPI(
    title="Eburon AI API",
    version="1.0.0",
    description=(
        "Eburon AI unified API gateway. "
        "TalkHuman-3.1 provides realtime expressive human-like voice API. "
        "TalkHuman RolePlay provides cinematic realtime role-play and live monologue endpoint. "
        "TranslateHuman-3.1 provides multimodal translation for text, images, documents, and websites. "
        "All public model names are Eburon AI aliases."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=openapi_tags,
)

app.add_exception_handler(EburonTranslateError, eburon_translate_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

app.include_router(health.router)
app.include_router(eburon_translate.router)
app.include_router(talkhuman.router)
app.include_router(talkhuman_roleplay.router)
app.include_router(models.router)

# Mount static files for playground
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/playground", include_in_schema=False)
async def playground():
    return FileResponse("app/static/playground/index.html")

@app.get("/", tags=["Health"])

async def root() -> dict:
    return {
        "provider": "Eburon AI",
        "status": "ok",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "products": [
            {
                "product": "Eburon Translate",
                "model": "translatehuman-3.1",
                "base_url": "/v1/eburon/translate",
            },
            {
                "product": "TalkHuman",
                "model": "talkhuman-3.1",
                "base_url": "/v1/eburon/talkhuman",
            },
        ],
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)
