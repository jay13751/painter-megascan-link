"""Thin wrappers around Painter Python APIs.

The plugin can still delegate some work to the JavaScript shim when Painter's
Python surface is too limited, but simple state queries live here.
"""

from __future__ import annotations

from typing import Optional


def is_project_open() -> Optional[bool]:
    try:
        import substance_painter.project as project
    except Exception:
        return None

    try:
        return bool(project.is_open())
    except Exception:
        return None
