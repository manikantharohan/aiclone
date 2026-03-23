from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from models.schemas import ErrorResponse
from routes.chat import router as chat_router


settings = get_settings()
logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# CORS: restrict to frontend origin(s) from env
_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("HTTPException: %s %s", exc.status_code, exc.detail)
    payload = ErrorResponse(detail=str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning("Validation error: %s", exc)
    payload = ErrorResponse(detail="Invalid request.", meta={"errors": exc.errors()})
    return JSONResponse(
        status_code=422,
        content=payload.model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:  # noqa: BLE001
    logger.exception("Unhandled server error: %s", exc)
    payload = ErrorResponse(detail="Internal server error.")
    return JSONResponse(
        status_code=500,
        content=payload.model_dump(),
    )


@app.get("/health", tags=["system"])
async def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model": settings.GROQ_MODEL if settings.GROQ_API_KEY else settings.HF_MODEL,
    }


# Include WebSocket / chat routes
app.include_router(chat_router, tags=["chat"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

