"""
Custom exceptions and exception handlers for FastAPI application.
Handles FileNotFoundError, ValueError, and generic exceptions with proper HTTP responses.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def file_not_found_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
    """
    Handler cho FileNotFoundError - trả về HTTP 500.
    Validates: Requirements 7.1
    """
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handler cho ValueError - trả về HTTP 400.
    Validates: Requirements 6.2, 6.3, 6.4, 6.5
    """
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler cho generic Exception - trả về HTTP 500.
    Validates: Requirements 7.2, 7.4
    """
    return JSONResponse(
        status_code=500,
        content={"detail": f"Lỗi nội bộ: {str(exc)}"}
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler cho HTTPException - đảm bảo format JSON với trường detail.
    Validates: Requirements 7.3
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler cho RequestValidationError - trả về HTTP 422 với format JSON.
    Validates: Requirements 4.4, 7.3
    """
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )
