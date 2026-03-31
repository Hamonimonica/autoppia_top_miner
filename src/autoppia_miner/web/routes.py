"""HTTP routes for the IWA miner."""

from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from autoppia_miner.engine.knowledge import lookup as knowledge_lookup
from autoppia_miner.domain.request import ActRequest
from autoppia_miner.engine.decision import decide

logger = logging.getLogger("agent")

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Health check — must respond quickly (sandbox timeout)."""
    return {"status": "healthy"}


@router.post("/act")
async def act(request: ActRequest):
    """Run one agent step: baseline knowledge from index 1, else LLM decision."""
    logger.info(
        "act request",
        extra={
            "task_id": request.task_id,
            "url": request.url,
            "step_index": request.step_index,
        },
    )

    known_actions = knowledge_lookup(request.task_id)
    if known_actions is not None:
        # Produce from step 1: skip known_actions[0] (redundant navigate / setup).
        next_idx = request.step_index + 1
        if next_idx < len(known_actions):
            action = known_actions[next_idx]
            logger.info(
                "baseline match",
                extra={
                    "task_id": request.task_id,
                    "step_index": request.step_index,
                    "action_type": action.get("type", "unknown"),
                    "total_actions": len(known_actions),
                },
            )
            return JSONResponse(content={"actions": [action]})
        logger.info(
            "baseline complete",
            extra={
                "task_id": request.task_id,
                "step_index": request.step_index,
            },
        )
        return JSONResponse(content={"actions": []})

    response = decide(request)

    action_type = (
        type(response.actions[0]).__name__ if response.actions else "done"
    )
    logger.info(
        "act response",
        extra={"action_type": action_type},
    )

    return response
