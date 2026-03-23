"""Entrypoint for ``uvicorn main:app`` (backwards-compatible)."""

from __future__ import annotations

import sys
from pathlib import Path

# Repo checkout: package lives under ``src/``; ensure it is importable even when
# the editable install is missing or a different ``VIRTUAL_ENV`` is active.
_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.is_dir():
    src_str = str(_src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

from autoppia_miner.web.app import app  # noqa: E402

__all__ = ["app"]
