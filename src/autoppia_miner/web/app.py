"""FastAPI application factory and global exception handling."""

from __future__ import annotations

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from autoppia_miner.web.logging_config import configure_agent_logging
from autoppia_miner.web.routes import router

configure_agent_logging()
logger = logging.getLogger("agent")

SAFE_WAIT_RESPONSE = {"actions": [{"type": "WaitAction", "time_seconds": 1.0}]}


def create_app() -> FastAPI:
    """Build the FastAPI app (routes + exception handler)."""
    application = FastAPI(title="Autoppia Web Agent")
    application.include_router(router)

    @application.exception_handler(Exception)
    async def catch_all_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch unhandled exceptions and return a safe WaitAction."""
        logger.error(
            "Unhandled exception: %s: %s\n%s",
            type(exc).__name__,
            exc,
            traceback.format_exc(),
        )
        return JSONResponse(status_code=200, content=SAFE_WAIT_RESPONSE)

    return application


app = create_app()
