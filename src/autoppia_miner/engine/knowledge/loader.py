"""Load baseline action sequences and index successful traces by ``taskId``.

The default data file lives alongside this module::

    src/autoppia_miner/engine/knowledge/baseline_actions.json

Override with env ``TASK_RESULTS_PATH``.

Replay: actions are emitted from index ``step_index + 1`` (skip index ``0``).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("agent")

_INDEX: dict[str, list[dict[str, Any]]] = {}

_DATA_FILE = "baseline_actions.json"


def _resolve_path() -> Path | None:
    """Resolve the baseline actions JSON path."""
    env = os.environ.get("TASK_RESULTS_PATH")
    if env:
        return Path(env)

    # Co-located with this module
    bundled = Path(__file__).resolve().parent / _DATA_FILE
    if bundled.is_file():
        return bundled

    return None


def _load() -> None:
    path = _resolve_path()
    if path is None:
        logger.info("baseline actions data not found, knowledge base disabled")
        return

    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("failed to load baseline actions: %s", exc)
        return

    loaded = 0
    for entry in data:
        task = entry.get("task", {})
        task_id = task.get("taskId")
        status = entry.get("status")
        response = entry.get("response")

        if not task_id or status != "success" or response is None:
            continue

        actions = response.get("actions", [])
        _INDEX[task_id] = actions
        loaded += 1

    logger.info("knowledge base loaded: %d task baselines from %s", loaded, path)


def lookup(task_id: str) -> list[dict[str, Any]] | None:
    """Return baseline action list for *task_id*, or ``None`` on miss."""
    return _INDEX.get(task_id)


_load()
