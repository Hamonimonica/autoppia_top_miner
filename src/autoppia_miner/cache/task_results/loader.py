"""Load ``task_results.json`` and index successful traces by ``taskId``.

Default file location (in-repo, deeper than project root)::

    <project_root>/data/task_results.json

Override with env ``TASK_RESULTS_PATH``. Legacy fallbacks: repo root
``task_results.json`` and cwd-based paths.

Replay: actions are emitted from index ``step_index + 1`` (skip index ``0``).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("agent")

_CACHE: dict[str, list[dict[str, Any]]] = {}


def _project_root() -> Path | None:
    """Checkout root: directory that has ``pyproject.toml`` and ``src/``."""
    for p in Path(__file__).resolve().parents:
        if (p / "pyproject.toml").is_file() and (p / "src").is_dir():
            return p
    return None


def _resolve_task_results_path() -> Path | None:
    """Resolve JSON path: env, then ``data/task_results.json``, then legacy."""
    env = os.environ.get("TASK_RESULTS_PATH")
    if env:
        return Path(env)

    root = _project_root()
    if root is not None:
        primary = root / "data" / "task_results.json"
        if primary.is_file():
            return primary

        legacy_root = root / "task_results.json"
        if legacy_root.is_file():
            return legacy_root

    cwd_data = Path.cwd() / "data" / "task_results.json"
    if cwd_data.is_file():
        return cwd_data

    cwd_legacy = Path.cwd() / "task_results.json"
    if cwd_legacy.is_file():
        return cwd_legacy

    return None


def _load_cache() -> None:
    cache_path = _resolve_task_results_path()
    if cache_path is None:
        logger.info("task_results.json not found, cache disabled")
        return

    try:
        data = json.loads(cache_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("failed to load task_results.json: %s", exc)
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
        _CACHE[task_id] = actions
        loaded += 1

    logger.info(
        "task results cache loaded: %d tasks from %s",
        loaded,
        cache_path,
    )


def lookup(task_id: str) -> list[dict[str, Any]] | None:
    """Return cached action list for *task_id*, or ``None`` on cache miss."""
    return _CACHE.get(task_id)


_load_cache()
