"""Pydantic data models for the Data Intelligence Layer (DIL)."""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class ColumnStructuralInfo(BaseModel):
    """Detailed structural profiling information for a single column."""

    name: str
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    sample: str | None = None
    is_numeric: bool = False
    is_categorical: bool = False
    is_datetime: bool = False
    is_boolean: bool = False
    is_candidate_id: bool = False
    stats: dict[str, Any] = Field(default_factory=dict)


class StructuralProfile(BaseModel):
    """Full dataset structural profile."""

    row_count: int
    column_count: int
    memory_mb: float
    duplicate_rows: int
    duplicate_percentage: float
    columns: list[ColumnStructuralInfo]
    candidate_ids: list[str] = Field(default_factory=list)
    datetime_columns: list[str] = Field(default_factory=list)
    numeric_columns: list[str] = Field(default_factory=list)
    categorical_columns: list[str] = Field(default_factory=list)
    boolean_columns: list[str] = Field(default_factory=list)


class QualityIssue(BaseModel):
    """Specific quality anomaly or defect detected in a column or dataset."""

    column_name: str | None = None
    issue_type: str  # e.g., 'missing_values', 'impossible_value', 'duplicate_rows', 'whitespace'
    severity: Literal["info", "low", "medium", "high", "critical"] = "medium"
    description: str
    affected_count: int = 0


class QualityProfile(BaseModel):
    """Data quality evaluation scores and issues."""

    overall_score: float  # 0.0 to 100.0
    completeness: float   # 0.0 to 100.0
    uniqueness: float     # 0.0 to 100.0
    consistency: float    # 0.0 to 100.0
    validity: float       # 0.0 to 100.0
    integrity: float      # 0.0 to 100.0
    issues: list[QualityIssue] = Field(default_factory=list)


class ReadinessBreakdown(BaseModel):
    """Breakdown of readiness scores by DIL layer/dimension."""

    structure: float = 0.0
    quality: float = 0.0
    semantics: float = 0.0
    domain: float = 0.0
    knowledge: float = 0.0


class ConceptAlternative(BaseModel):
    """Alternative concept suggestion."""

    concept: str
    confidence: float
    description: str | None = None


class ColumnSemantic(BaseModel):
    """Semantic meaning and concept mapping for a column."""

    column_name: str
    inferred_concept: str
    semantic_role: Literal["identifier", "measure", "dimension", "target", "datetime", "text"] = "measure"
    entity_type: str | None = None
    units: str | None = None
    confidence: float = 1.0
    source: Literal["heuristic", "llm", "human"] = "heuristic"
    alternatives: list[ConceptAlternative] = Field(default_factory=list)
    needs_review: bool = False
    description: str | None = None


class SemanticProfile(BaseModel):
    """Full dataset semantic profile."""

    overall_confidence: float = 1.0
    columns: list[ColumnSemantic] = Field(default_factory=list)
    target_candidates: list[str] = Field(default_factory=list)
    predictor_candidates: list[str] = Field(default_factory=list)


class DomainProfile(BaseModel):
    """Dataset domain classification profile."""

    primary_domain: str = "generic"
    confidence: float = 1.0
    reasoning: str = ""
    subdomains: list[str] = Field(default_factory=list)


class IntelligenceRecordData(BaseModel):
    """Complete dataset intelligence payload."""

    structural_profile: StructuralProfile
    quality_profile: QualityProfile
    semantic_profile: SemanticProfile | None = None
    domain_profile: DomainProfile | None = None
    readiness_score: float  # 0.0 to 100.0
    readiness_breakdown: ReadinessBreakdown
    warnings: list[str] = Field(default_factory=list)
    version: int = 1
