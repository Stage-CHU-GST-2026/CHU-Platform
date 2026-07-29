"""Dataset Readiness Score Evaluator."""

from __future__ import annotations

from dil.models import DomainProfile, QualityProfile, ReadinessBreakdown, SemanticProfile, StructuralProfile


def calculate_structure_readiness(struct_profile: StructuralProfile) -> float:
    """Calculate structural readiness score (0-100)."""
    if struct_profile.row_count == 0 or struct_profile.column_count == 0:
        return 0.0

    score = 100.0

    # Deduct for missing candidate primary key
    if not struct_profile.candidate_ids:
        score -= 10.0

    # Deduct for duplicate rows
    score -= min(30.0, struct_profile.duplicate_percentage)

    # Deduct if column count is extremely low (<2)
    if struct_profile.column_count < 2:
        score -= 20.0

    return max(0.0, round(score, 2))


def calculate_readiness(
    struct_profile: StructuralProfile,
    quality_profile: QualityProfile,
    semantic_profile: SemanticProfile | None = None,
    domain_profile: DomainProfile | None = None,
    knowledge_score: float = 0.0,
) -> tuple[float, ReadinessBreakdown, list[str]]:
    """Compute weighted composite readiness score and warnings."""
    struct_score = calculate_structure_readiness(struct_profile)
    qual_score = quality_profile.overall_score
    semantic_score = round(semantic_profile.overall_confidence * 100.0, 2) if semantic_profile else 0.0
    domain_score = round(domain_profile.confidence * 100.0, 2) if domain_profile else 0.0

    warnings: list[str] = []

    if struct_profile.row_count == 0:
        warnings.append("Dataset has 0 rows.")
    if struct_profile.duplicate_rows > 0:
        warnings.append(f"Contains {struct_profile.duplicate_rows} duplicate rows ({struct_profile.duplicate_percentage}%).")
    if quality_profile.completeness < 70.0:
        warnings.append(f"Low completeness score: {quality_profile.completeness}%.")

    if semantic_profile and any(c.needs_review for c in semantic_profile.columns):
        review_cnt = sum(1 for c in semantic_profile.columns if c.needs_review)
        warnings.append(f"{review_cnt} column(s) require human semantic concept review.")

    # Weighted calculation
    if semantic_profile is None and domain_profile is None:
        readiness = round((struct_score * 0.50) + (qual_score * 0.50), 2)
    else:
        readiness = round(
            (struct_score * 0.30)
            + (qual_score * 0.30)
            + (semantic_score * 0.25)
            + (domain_score * 0.10)
            + (knowledge_score * 0.05),
            2,
        )

    breakdown = ReadinessBreakdown(
        structure=struct_score,
        quality=qual_score,
        semantics=semantic_score,
        domain=domain_score,
        knowledge=knowledge_score,
    )

    return readiness, breakdown, warnings
