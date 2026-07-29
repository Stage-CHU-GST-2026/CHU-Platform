"""Data Intelligence Layer (DIL) package."""

from dil.domain_detector import detect_domain
from dil.models import (
    ColumnSemantic,
    ColumnStructuralInfo,
    ConceptAlternative,
    DomainProfile,
    IntelligenceRecordData,
    QualityIssue,
    QualityProfile,
    ReadinessBreakdown,
    SemanticProfile,
    StructuralProfile,
)
from dil.quality_engine import evaluate_quality
from dil.readiness import calculate_readiness, calculate_structure_readiness
from dil.semantic_engine import generate_semantic_profile, resolve_column_semantic
from dil.structural_profiler import generate_structural_profile

__all__ = [
    "ColumnSemantic",
    "ColumnStructuralInfo",
    "ConceptAlternative",
    "DomainProfile",
    "IntelligenceRecordData",
    "QualityIssue",
    "QualityProfile",
    "ReadinessBreakdown",
    "SemanticProfile",
    "StructuralProfile",
    "generate_structural_profile",
    "evaluate_quality",
    "generate_semantic_profile",
    "resolve_column_semantic",
    "detect_domain",
    "calculate_readiness",
    "calculate_structure_readiness",
]
