from fastapi import Request
from fastapi.responses import JSONResponse
from api.models import ErrorResponse


async def http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(status_code=exc.status_code, message=exc.detail).dict()
    )