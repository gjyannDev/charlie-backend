"""
main.py - FastAPI application entry point.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError as FastAPIValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import get_logger
from app.middleware.exception_logging import ExceptionLoggingMiddleware
from app.modules.auth.Routes import auth_router

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
)

for router in [auth_router]:
    app.include_router(router=router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(ExceptionLoggingMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(FastAPIValidationError)
async def validation_exception_handler(request: Request, exc: FastAPIValidationError):
    logger.warning(
        f"Validation error at {request.url}: {exc.errors()} | Body: {exc.body}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
