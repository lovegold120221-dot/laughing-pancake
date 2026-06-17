from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

TRANSLATE_ERROR_CODE = "EBURON_TRANSLATE_ERROR"
TRANSLATE_VALIDATION_ERROR_CODE = "EBURON_TRANSLATE_VALIDATION_ERROR"
PUBLIC_PROVIDER = "Eburon AI"
PUBLIC_TRANSLATE_MODEL = "translatehuman-3.1"
PUBLIC_TRANSLATE_PRODUCT = "Eburon Translate"


class EburonTranslateError(Exception):
    def __init__(
        self,
        message: str = "The translation request could not be completed.",
        *,
        status_code: int = 400,
        code: str = TRANSLATE_ERROR_CODE,
        model: str = PUBLIC_TRANSLATE_MODEL,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        self.model = model


def translate_error_payload(
    *,
    message: str = "The translation request could not be completed.",
    code: str = TRANSLATE_ERROR_CODE,
    model: str = PUBLIC_TRANSLATE_MODEL,
) -> dict:
    return {
        "provider": PUBLIC_PROVIDER,
        "product": PUBLIC_TRANSLATE_PRODUCT,
        "model": model,
        "error": {
            "code": code,
            "message": message,
        },
    }


def api_error_payload(
    *,
    message: str = "The Eburon AI request could not be completed.",
    code: str = "EBURON_API_ERROR",
) -> dict:
    return {
        "provider": PUBLIC_PROVIDER,
        "error": {
            "code": code,
            "message": message,
        },
    }


async def eburon_translate_error_handler(
    request: Request,
    exc: EburonTranslateError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=translate_error_payload(
            message=exc.message,
            code=exc.code,
            model=exc.model,
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    if not request.url.path.startswith("/v1/eburon/translate"):
        return JSONResponse(
            status_code=422,
            content=api_error_payload(
                message="The Eburon AI request is invalid.",
                code="EBURON_API_VALIDATION_ERROR",
            ),
        )

    return JSONResponse(
        status_code=422,
        content=translate_error_payload(
            message="The translation request is invalid.",
            code=TRANSLATE_VALIDATION_ERROR_CODE,
        ),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    if isinstance(exc.detail, dict) and exc.detail.get("provider") == PUBLIC_PROVIDER:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    if request.url.path.startswith("/v1/eburon/translate"):
        if exc.status_code == 404:
            return JSONResponse(
                status_code=404,
                content=translate_error_payload(
                    message="The requested translation endpoint was not found.",
                    code="EBURON_TRANSLATE_NOT_FOUND",
                ),
            )
        if exc.status_code == 405:
            return JSONResponse(
                status_code=405,
                content=translate_error_payload(
                    message="The requested translation endpoint does not support this method.",
                    code="EBURON_TRANSLATE_METHOD_NOT_ALLOWED",
                ),
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=translate_error_payload(),
        )

    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content=api_error_payload(
                message="The requested Eburon AI endpoint was not found.",
                code="EBURON_API_NOT_FOUND",
            ),
        )
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content=api_error_payload(
                message="The requested Eburon AI endpoint does not support this method.",
                code="EBURON_API_METHOD_NOT_ALLOWED",
            ),
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=api_error_payload(),
    )
