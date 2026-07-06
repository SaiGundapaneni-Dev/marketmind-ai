import logging

from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger("marketmind")


async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        "Unhandled error while processing %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred."
            }
        }
    )