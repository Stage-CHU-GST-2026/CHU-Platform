"""Plan creation tool — generates structured plan markdown files."""

from __future__ import annotations

import json
import os
import uuid

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .visualization import CHARTS_DIR

ARTIFACT_URL_PREFIX = "ARTIFACT_URL:"


class CreateBlueprintSchema(BaseModel):
    title: str = Field(
        description="Short, human-readable title for the plan card (e.g. 'Implementation Plan Created')."
    )
    description: str = Field(
        description="Brief 1-2 sentence summary shown on the plan card below the title."
    )
    content: str = Field(
        description="Full markdown content of the plan."
    )
    filename: str = Field(
        default="implementation_plan.md",
        description="Filename for the plan artifact (e.g. 'data_migration_plan.md'). Must end with .md",
    )


class CreateBlueprintTool(BaseTool):
    name: str = "create_blueprint"
    description: str = (
        "Generate a structured blueprint document and save it as a markdown artifact."
    )
    args_schema: type[BaseModel] = CreateBlueprintSchema

    def _run(
        self,
        title: str,
        description: str,
        content: str,
        filename: str = "implementation_plan.md",
    ) -> str:
        if not filename.endswith(".md"):
            filename += ".md"

        os.makedirs(CHARTS_DIR, exist_ok=True)

        unique_id = uuid.uuid4().hex[:12]
        safe_filename = f"plan_{unique_id}_{filename}"
        filepath = os.path.join(CHARTS_DIR, safe_filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = os.path.getsize(filepath)
        api_url = f"/api/v1/charts/{safe_filename}"

        metadata = json.dumps(
            {
                "url": api_url,
                "title": title,
                "description": description,
                "filename": safe_filename,
                "file_size": file_size,
            }
        )

        return f"{ARTIFACT_URL_PREFIX}{metadata}\nPlan saved to {filepath}"
