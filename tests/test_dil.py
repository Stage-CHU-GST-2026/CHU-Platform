"""Unit tests for the Data Intelligence Layer (DIL) package."""

import pandas as pd
import pytest

from dil import (
    evaluate_quality,
    generate_structural_profile,
    calculate_readiness,
)


def test_dil_pipeline():
    # Sample DataFrame
    data = {
        "patient_id": [101, 102, 103, 104, 105],
        "age": [25, 40, -5, 65, 200],  # Has 2 invalid ages (<0, >150)
        "glucose": [90.5, 110.0, None, 140.2, 95.0],
        "gender": ["Male", "female", "MALE", "Female", "Male "],  # Casing and whitespace issue
    }
    df = pd.DataFrame(data)

    # 1. Structural profile
    struct = generate_structural_profile(df)
    assert struct.row_count == 5
    assert struct.column_count == 4
    assert "patient_id" in struct.candidate_ids
    assert "age" in struct.numeric_columns
    assert "gender" in struct.categorical_columns

    # 2. Quality evaluation
    quality = evaluate_quality(df, struct)
    assert quality.overall_score < 100.0
    assert any(issue.issue_type == "impossible_value" for issue in quality.issues)
    assert any(issue.issue_type == "whitespace_inconsistency" for issue in quality.issues)
    assert any(issue.issue_type == "casing_inconsistency" for issue in quality.issues)

    # 3. Readiness calculation
    readiness, breakdown, warnings = calculate_readiness(struct, quality)
    assert 0.0 <= readiness <= 100.0
    assert breakdown.structure > 0
    assert breakdown.quality > 0
