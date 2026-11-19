"""Tratamento padronizado de erros da API (T-015).

Toda resposta de erro segue o envelope:

    {"error": {"code": "...", "message": "...", "details": ...}}
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Erro de negócio com payload padronizado."""

    def __init__(
        self,
        code: str,
        message: str,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details

    def to_payload(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.http_status, content=exc.to_payload())

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        error = AppError(
            code="validation_error",
            message="Os dados recebidos são inválidos.",
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            # Não reflete os valores enviados (ex.: senhas) na resposta
            # (T-065, AC-094); jsonable_encoder converte Decimals de
            # limites (ex.: gt) em JSON.
            details=jsonable_encoder(
                [
                    {
                        key: value
                        for key, value in item.items()
                        if key not in {"input", "ctx"}
                    }
                    for item in exc.errors()
                ]
            ),
        )
        return JSONResponse(status_code=error.http_status, content=error.to_payload())

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        _request: Request, _exc: Exception
    ) -> JSONResponse:
        error = AppError(
            code="internal_error",
            message="Ocorreu um erro inesperado. Tente novamente.",
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        return JSONResponse(status_code=error.http_status, content=error.to_payload())
