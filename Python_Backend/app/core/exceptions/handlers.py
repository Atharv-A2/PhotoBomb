from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.base import ApplicationException


def register_exception_handlers(
    app: FastAPI,
) -> None:
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request,
        exc: ApplicationException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
            },
        )