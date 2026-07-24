"""Plan creation tool — generates structured plan markdown files.

The LLM calls this tool when asked to produce a plan, strategy, or
step-by-step approach. The tool saves the markdown content to disk
so it can be served as a downloadable/ viewable artifact.

Usage (from the LLM):
    create_blueprint(
        title="Analysis Blueprint",
        description="A concise 1-2 sentence summary for the card.",
        content="# Full markdown blueprint...",
        filename="analysis_blueprint.md",
    )
"""

from __future__ import annotations

import json
import os
import uuid

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Reuse the same charts directory that visualisation tools use, so the
# API's static file mount (``/api/v1/charts``) serves plan files too.
# We import the *module* and access CHARTS_DIR at call time so that
# the API's lifespan override (viz_mod.CHARTS_DIR = abs_path) is
# visible to this module at runtime.
from tools.visualization import visualization as _viz_module

# Prefix embedded in tool output so the streaming layer can detect plan URLs.
ARTIFACT_URL_PREFIX = "ARTIFACT_URL:"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class CreateBlueprintSchema(BaseModel):
    title: str = Field(
        description=(
            "Short, human-readable title for the plan card "
            "(e.g. 'Implementation Plan Created')."
        ),
    )
    description: str = Field(
        description=(
            "Brief 1-2 sentence summary shown on the plan card below the title. "
            "Describes what the plan covers at a high level."
        ),
    )
    content: str = Field(
        description=(
            "Full markdown content of the plan. Use headings, lists, tables, "
            "and code blocks as needed. This is the complete document shown "
            "when the user clicks 'View Plan'."
        ),
    )
    filename: str = Field(
        default="implementation_plan.md",
        description=(
            "Filename for the plan artifact (e.g. 'data_migration_plan.md'). "
            "Must end with .md"
        ),
    )


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------


class CreateBlueprintTool(BaseTool):
    name: str = "create_blueprint"
    description: str = (
        "Generate a structured blueprint document and save it as a markdown artifact. "
        "Call this whenever the user asks for a blueprint, plan document, strategy, "
        "step-by-step approach, implementation steps, migration plan, or roadmap. "
        "Provide a clear title, a one-sentence description for the card preview, "
        "and the full markdown content. The blueprint will appear as an interactive card "
        "with options to view the full document."
    )
    args_schema: type[BaseModel] = CreateBlueprintSchema

    def _run(
        self,
        title: str,
        description: str,
        content: str,
        filename: str = "implementation_plan.md",
    ) -> str:
        # Ensure filename ends with .md
        if not filename.endswith(".md"):
            filename += ".md"

        # Ensure output directory exists
        charts_dir = _viz_module.CHARTS_DIR
        os.makedirs(charts_dir, exist_ok=True)

        # Prepend a unique ID to avoid collisions
        unique_id = uuid.uuid4().hex[:12]
        safe_filename = f"plan_{unique_id}_{filename}"
        filepath = os.path.join(charts_dir, safe_filename)

        # Write the markdown content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = os.path.getsize(filepath)
        api_url = f"/api/v1/charts/{safe_filename}"

        # Encode metadata as JSON so the streaming layer can forward it
        metadata = json.dumps({
            "url": api_url,
            "title": title,
            "description": description,
            "filename": safe_filename,
            "file_size": file_size,
        })

        return (
            f"{ARTIFACT_URL_PREFIX}{metadata}\n"
            f"Plan saved to {filepath}"
        )
