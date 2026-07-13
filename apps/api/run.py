"""
Run the Data Analyst API server.

Usage:
    uv run --directory apps/api run.py
"""

from __future__ import annotations

import os
import sys

# ----- Working directory: project root -----
_proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(_proj_root)

# Allow imports from api/src and the root packages/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, _proj_root)

if __name__ == "__main__":
    import uvicorn

    from api.config import settings

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
